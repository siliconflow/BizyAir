import asyncio
import logging
import os
import uuid

import aiohttp
from server import PromptServer

import bizyair
import bizyair.common

from .api_client import APIClient
from .errno import errnos, ErrorNo
from .error_handler import ErrorHandler
from .execution import UploadQueue
from .resp import ErrResponse, OKResponse
from .upload_manager import UploadManager
from .utils import (
    check_str_param,
    check_type,
    is_string_valid,
    types,
    base_model_types,
    is_allow_ext_name,
    to_slash,
)

API_PREFIX = "bizyair"
COMMUNITY_API = f"{API_PREFIX}/community"
USER_API = f"{API_PREFIX}/user"

logging.basicConfig(level=logging.DEBUG)


class BizyAirServer:
    def __init__(self):
        BizyAirServer.instance = self
        self.api_client = APIClient()
        self.upload_manager = UploadManager(self)
        self.error_handler = ErrorHandler()
        self.prompt_server = PromptServer.instance
        self.sockets = dict()
        self.uploads = dict()
        self.upload_queue = UploadQueue()
        self.loop = asyncio.get_event_loop()

        self.setup_routes()

    def setup_routes(self):
        @self.prompt_server.routes.get(f"/{COMMUNITY_API}/model_types")
        async def list_model_types(request):
            return OKResponse(types())

        @self.prompt_server.routes.get(f"/{COMMUNITY_API}/base_model_types")
        async def list_base_model_types(request):
            return OKResponse(base_model_types())

        @self.prompt_server.routes.get(f"/{USER_API}/info")
        async def user_info(request):
            info, err = await self.api_client.user_info()
            if err is not None:
                return ErrResponse(err)

            return OKResponse(info)

        @self.prompt_server.routes.get(f"/{API_PREFIX}/ws")
        async def websocket_handler(request):
            ws = aiohttp.web.WebSocketResponse()
            await ws.prepare(request)
            sid = request.rel_url.query.get("clientId", "")
            if sid:
                # Reusing existing session, remove old
                self.sockets.pop(sid, None)
            else:
                sid = uuid.uuid4().hex

            self.sockets[sid] = ws

            try:
                # Send initial state to the new client
                await self.send_json(
                    event="status", data={"status": "connected"}, sid=sid
                )

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data == "ping":
                            await ws.send_str("pong")
                    if msg.type == aiohttp.WSMsgType.ERROR:
                        logging.warning(
                            "ws connection closed with exception %s" % ws.exception()
                        )
            finally:
                self.sockets.pop(sid, None)
            return ws

        @self.prompt_server.routes.get(f"/{COMMUNITY_API}/check_local_file")
        async def check_local_file(request):
            absolute_path = request.rel_url.query.get("absolute_path")

            if not is_string_valid(absolute_path):
                return ErrResponse(errnos.EMPTY_ABS_PATH)

            if not os.path.isabs(absolute_path):
                return ErrResponse(errnos.NO_ABS_PATH)

            if not os.path.exists(absolute_path):
                return ErrResponse(errnos.PATH_NOT_EXISTS)

            if not os.path.isfile(absolute_path):
                return ErrResponse(errnos.NOT_A_FILE)

            if not is_allow_ext_name(absolute_path):
                return ErrResponse(errnos.NOT_ALLOWED_EXT_NAME)

            file_size = os.path.getsize(absolute_path)
            relative_path = os.path.basename(absolute_path)

            upload_id = uuid.uuid4().hex
            data = {
                "upload_id": upload_id,
                "root": os.path.dirname(absolute_path),
                "files": [{"path": to_slash(relative_path), "size": file_size}]
            }
            self.uploads[upload_id] = data

            return OKResponse(data)

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/submit_upload")
        async def submit_upload(request):
            sid = request.rel_url.query.get("clientId", "")
            if not is_string_valid(sid):
                return ErrResponse(errnos.INVALID_CLIENT_ID)

            json_data = await request.json()
            err = check_str_param(json_data, "upload_id", errnos.EMPTY_UPLOAD_ID)
            if err is not None:
                return err

            upload_id = json_data.get("upload_id")
            if upload_id not in self.uploads:
                return ErrResponse(errnos.INVALID_UPLOAD_ID)

            self.uploads[upload_id]["sid"] = sid
            self.upload_queue.put(self.uploads[upload_id])

            return OKResponse(None)
        
        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/models")
        async def commit_bizy_model(request):
            json_data = await request.json()
            
            # 校验name和type
            err = check_str_param(json_data, "name", errnos.INVALID_NAME)
            if err:
                return err
            
            err = check_type(json_data)
            if err:
                return err
            
            # 校验versions
            if "versions" not in json_data or not isinstance(json_data["versions"], list):
                return ErrResponse(errnos.INVALID_VERSIONS)
            
            versions = json_data["versions"]
            version_names = set()
            
            for version in versions:
                # 检查version是否重复
                if version.get("version") in version_names:
                    return ErrResponse(errnos.DUPLICATE_VERSION)
                version_names.add(version.get("version"))
                
                # 检查base_model, path和sign是否有值
                for field in ["base_model", "path", "sign"]:
                    if not is_string_valid(version.get(field)):
                        return ErrResponse(errnos.INVALID_VERSION_FIELD(field))
            
            # 调用API提交模型
            resp, err = await self.api_client.commit_bizy_model(payload=json_data)
            if err:
                return ErrResponse(err)

            # enable refresh for lora
            # TODO: enable refresh for other types
            bizyair.path_utils.path_manager.enable_refresh_options("loras")
            
            return OKResponse(resp)

    async def send_json(self, event, data, sid=None):
        message = {"type": event, "data": data}

        if sid is None:
            sockets = list(self.sockets.values())
            for ws in sockets:
                await self.send_socket_catch_exception(ws.send_json, message)
        elif sid in self.sockets:
            await self.send_socket_catch_exception(self.sockets[sid].send_json, message)

    async def send_error(self, err: ErrorNo, sid=None):
        await self.send_json(
            event="error",
            data={"message": err.message, "code": err.code, "data": err.data},
            sid=sid,
        )

    async def send_socket_catch_exception(self, function, message):
        try:
            await function(message)
        except (
                aiohttp.ClientError,
                aiohttp.ClientPayloadError,
                ConnectionResetError,
        ) as err:
            logging.warning("send error: {}".format(err))

    def send_sync(self, event, data, sid=None):
        asyncio.run_coroutine_threadsafe(self.send_json(event, data, sid), self.loop)

    def send_sync_error(self, err: ErrorNo, sid=None):
        self.send_sync(
            event="errors",
            data={"message": err.message, "code": err.code, "data": err.data},
            sid=sid,
        )
