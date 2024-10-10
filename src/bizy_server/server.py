import asyncio
import logging
import os
import uuid

import aiohttp
from server import PromptServer

import bizyair
import bizyair.common

from .api_client import APIClient
from .errno import (
    EMPTY_ABS_FOLDER_ERR,
    EMPTY_FILES_ERR,
    EMPTY_UPLOAD_ID_ERR,
    INVALID_CLIENT_ID_ERR,
    INVALID_NAME,
    INVALID_SHARE_ID,
    INVALID_TYPE,
    INVALID_UPLOAD_ID_ERR,
    MODEL_ALREADY_EXISTS_ERR,
    NO_ABS_PATH_ERR,
    NO_PUBLIC_FLAG_ERR,
    PATH_NOT_EXISTS_ERR,
    NO_SHARE_ID_ERR,
    INVALID_DESCRIPTION,
    ErrorNo,
)
from .error_handler import ErrorHandler
from .execution import UploadQueue
from .resp import ErrResponse, OKResponse
from .upload_manager import UploadManager
from .utils import get_html_content, check_type, check_str_param, is_string_valid, to_slash, list_types

from comfy.cli_args import args

MAX_UPLOAD_FILE_SIZE = round(args.max_upload_size * 1024 * 1024)

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://bizyair-api.siliconflow.cn/x/v1"
)

API_PREFIX = "bizyair"
MODEL_HOST_API = f"{API_PREFIX}/modelhost"
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
        list_model_html = get_html_content("templates/list_model.html")
        upload_model_html = get_html_content("templates/upload_model.html")

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/list")
        async def forward_list_model_html(request):
            return aiohttp.web.Response(text=list_model_html, content_type="text/html")

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/upload")
        async def forward_upload_model_html(request):
            return aiohttp.web.Response(text=upload_model_html, content_type="text/html")

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/model_types")
        async def list_model_types(request):
            allow_types = list_types()

            return OKResponse(allow_types)

        @self.prompt_server.routes.post(f"/{MODEL_HOST_API}/check_model_exists")
        async def check_model_exists(request):
            json_data = await request.json()
            err = check_type(json_data)
            if err is not None:
                return err

            err = check_str_param(json_data, param_name="name", err=INVALID_TYPE)
            if err is not None:
                return err

            exists, err = await self.api_client.check_model(
                name=json_data["name"], type=json_data["type"]
            )
            if err is not None:
                return ErrResponse(err)

            return OKResponse({"exists": exists})

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/ws")
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

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/check_folder")
        async def check_folder(request):
            absolute_path = request.rel_url.query.get("absolute_path")

            if not is_string_valid(absolute_path):
                return ErrResponse(EMPTY_ABS_FOLDER_ERR)

            if not os.path.isabs(absolute_path):
                return ErrResponse(NO_ABS_PATH_ERR)

            if not os.path.exists(absolute_path):
                return ErrResponse(PATH_NOT_EXISTS_ERR)

            relative_paths = []
            for root, dirs, files in os.walk(absolute_path):
                # Skip the .git directory
                if ".git" in dirs:
                    dirs.remove(".git")

                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, absolute_path)
                    file_size = os.path.getsize(file_path)
                    relative_paths.append(
                        {"path": to_slash(relative_path), "size": file_size}
                    )

            if len(relative_paths) < 1:
                return ErrResponse(EMPTY_FILES_ERR)

            upload_id = uuid.uuid4().hex
            data = {
                "upload_id": upload_id,
                "root": absolute_path,
                "files": relative_paths,
            }
            self.uploads[upload_id] = data

            return OKResponse(data)

        @self.prompt_server.routes.post(f"/{MODEL_HOST_API}/submit_upload")
        async def submit_upload(request):
            sid = request.rel_url.query.get("clientId", "")
            if not is_string_valid(sid):
                return ErrResponse(INVALID_CLIENT_ID_ERR)

            json_data = await request.json()
            err = check_str_param(json_data, "upload_id", EMPTY_UPLOAD_ID_ERR)
            if err is not None:
                return err

            upload_id = json_data.get("upload_id")
            if upload_id not in self.uploads:
                return ErrResponse(INVALID_UPLOAD_ID_ERR)

            err = check_type(json_data)
            if err is not None:
                return err

            err = check_str_param(json_data, "name", INVALID_NAME)
            if err is not None:
                return err

            exists, err = await self.api_client.check_model(
                type=json_data["type"], name=json_data["name"]
            )
            if err is not None:
                return ErrResponse(err)

            if (
                exists
                and "overwrite" not in json_data
                or json_data["overwrite"] is not True
            ):
                return ErrResponse(MODEL_ALREADY_EXISTS_ERR)

            self.uploads[upload_id]["sid"] = sid
            self.uploads[upload_id]["type"] = json_data["type"]
            self.uploads[upload_id]["name"] = json_data["name"]
            self.upload_queue.put(self.uploads[upload_id])

            # enable refresh for lora
            # TODO: enable refresh for other types
            bizyair.path_utils.path_manager.enable_refresh_options("loras")
            return OKResponse(None)

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/models/files")
        async def list_model_files(request):
            err = check_type(request.rel_url.query)
            if err is not None:
                return err

            public = False
            if "public" in request.rel_url.query:
                public = request.rel_url.query["public"]

            payload = {"type": request.rel_url.query["type"], "public": public}

            if "name" in request.rel_url.query:
                payload["name"] = request.rel_url.query["name"]

            if "ext_name" in request.rel_url.query:
                payload["ext_name"] = request.rel_url.query["ext_name"]

            model_files, err = await self.api_client.get_model_files(payload)
            if err is not None:
                return ErrResponse(err)
            return OKResponse(model_files)

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}" + "/{shareId}/models/files")
        async def list_share_model_files(request):
            shareId = request.match_info["shareId"]

            if not is_string_valid(shareId):
                return ErrResponse(INVALID_SHARE_ID)

            err = check_type(request.rel_url.query)
            if err is not None:
                return err

            payload = {
                "type": request.rel_url.query["type"],
            }

            if "name" in request.rel_url.query:
                payload["name"] = request.rel_url.query["name"]

            if "ext_name" in request.rel_url.query:
                payload["ext_name"] = request.rel_url.query["ext_name"]
            model_files, err = await self.api_client.get_share_model_files(
                shareId=shareId, payload=payload
            )
            if err is not None:
                return ErrResponse(err)

            return OKResponse(model_files)

        @self.prompt_server.routes.delete(f"/{MODEL_HOST_API}/models")
        async def delete_model(request):
            json_data = await request.json()

            err = check_type(json_data)
            if err is not None:
                return err

            err = check_str_param(json_data, "name", INVALID_NAME)
            if err is not None:
                return err

            err = await self.api_client.remove_model(
                model_type=json_data["type"], model_name=json_data["name"]
            )
            if err is not None:
                return ErrResponse(err)

            print("BizyAir: Delete successfully")
            return OKResponse(None)

        @self.prompt_server.routes.put(f"/{MODEL_HOST_API}/models/change_public")
        async def change_model_public(request):
            json_data = await request.json()

            err = check_type(json_data)
            if err is not None:
                return err

            err = check_str_param(json_data, "name", INVALID_NAME)
            if err is not None:
                return err

            if "public" not in json_data:
                return ErrResponse(NO_PUBLIC_FLAG_ERR)

            err = await self.api_client.change_public(
                model_type=json_data["type"],
                model_name=json_data["name"],
                public=json_data["public"],
            )
            if err is not None:
                return ErrResponse(err)

            print("BizyAir: Change model visibility successfully")
            return OKResponse(None)

        @self.prompt_server.routes.get(f"/{USER_API}/info")
        async def user_info(request):
            info, err = await self.api_client.user_info()
            if err is not None:
                return ErrResponse(err)

            return OKResponse(info)

        @self.prompt_server.routes.put(f"/{USER_API}/share_id")
        async def update_share_id(request):
            json_data = await request.json()
            if "share_id" not in json_data:
                return ErrResponse(NO_SHARE_ID_ERR)

            ret, err = await self.api_client.update_share_id(share_id=json_data["share_id"])
            if err is not None:
                return ErrResponse(err)

            return OKResponse(ret)

        @self.prompt_server.routes.get(f"/{MODEL_HOST_API}/models/description")
        async def description(request):
            err = check_type(request.rel_url.query)
            if err is not None:
                return err

            err = check_str_param(request.rel_url.query, "name", INVALID_NAME)
            if err is not None:
                return err

            payload = {
                "type": request.rel_url.query["type"],
                "name": request.rel_url.query["name"]
            }

            if "share_id" in request.rel_url.query:
                payload["share_id"] = request.rel_url.query["share_id"]

            get_desc, err = await self.api_client.get_description(payload)
            if err is not None:
                return ErrResponse(err)
            return OKResponse(get_desc)

        @self.prompt_server.routes.put(f"/{MODEL_HOST_API}/models/description")
        async def change_description(request):
            json_data = await request.json()

            err = check_type(json_data)
            if err is not None:
                return err

            err = check_str_param(json_data, "name", INVALID_NAME)
            if err is not None:
                return err

            err = check_str_param(json_data, "description", INVALID_DESCRIPTION)
            if err is not None:
                return err

            payload = {
                "type": json_data["type"],
                "name": json_data["name"],
                "description": json_data["description"],
            }

            desc, err = await self.api_client.update_description(payload)
            if err is not None:
                return ErrResponse(err)
            return OKResponse(desc)

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

