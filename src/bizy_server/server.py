import asyncio
import logging
import os
import tempfile
import threading
import time
import urllib.parse
import uuid

import aiohttp
from server import PromptServer

import bizyair.common

from .api_client import APIClient
from .errno import ErrorNo, errnos
from .error_handler import ErrorHandler
from .execution import UploadQueue
from .oss import AliOssStorageClient
from .resp import ErrResponse, OKResponse
from .upload_manager import UploadManager
from .utils import (
    base_model_types,
    check_str_param,
    check_type,
    is_allow_ext_name,
    is_string_valid,
    to_slash,
    types,
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
                "files": [{"path": to_slash(relative_path), "size": file_size}],
            }
            self.uploads[upload_id] = data

            return OKResponse(data)

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/models/check_workflow")
        async def check_workflow(request):
            sid = request.rel_url.query.get("clientId", "")
            if not is_string_valid(sid):
                return ErrResponse(errnos.INVALID_CLIENT_ID)

            reader = await request.multipart()
            field = await reader.next()
            if not field or field.name != "file":
                return ErrResponse(errnos.NO_FILE_UPLOAD)

            filename = field.filename
            if not filename:
                return ErrResponse(errnos.NO_FILE_UPLOAD)

            temp_dir = tempfile.gettempdir()
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_file_path = os.path.join(temp_dir, filename)
            with open(temp_file_path, "wb") as f:
                while chunk := await field.read_chunk():
                    f.write(chunk)

            file_size = os.path.getsize(temp_file_path)
            relative_path = os.path.basename(temp_file_path)

            upload_id = uuid.uuid4().hex
            data = {
                "upload_id": upload_id,
                "root": temp_dir,
                "files": [{"path": to_slash(relative_path), "size": file_size}],
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

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/interrupt_upload")
        async def interrupt_upload(request):
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

            if self.uploads.get(upload_id) is None:
                return ErrResponse(errnos.INVALID_UPLOAD_ID)

            await self.upload_manager.interrupt_uploading(upload_id)

            return OKResponse(None)

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/models")
        async def commit_bizy_model(request):
            sid = request.rel_url.query.get("clientId", "")
            if not is_string_valid(sid):
                return ErrResponse(errnos.INVALID_CLIENT_ID)

            json_data = await request.json()

            # 校验name和type
            err = check_str_param(json_data, "name", errnos.INVALID_NAME)
            if err is not None:
                return err

            if "/" in json_data["name"]:
                return ErrResponse(errnos.INVALID_NAME)

            err = check_type(json_data)
            if err is not None:
                return err

            # 校验versions
            if "versions" not in json_data or not isinstance(
                json_data["versions"], list
            ):
                return ErrResponse(errnos.INVALID_VERSIONS)

            versions = json_data["versions"]
            version_names = set()

            for version in versions:
                # 检查version是否重复
                if version.get("version") in version_names:
                    return ErrResponse(errnos.DUPLICATE_VERSION)

                # 检查version字段是否合法
                if not is_string_valid(version.get("version")) or "/" in version.get(
                    "version"
                ):
                    return ErrResponse(errnos.INVALID_VERSION_NAME)

                version_names.add(version.get("version"))

                # 检查base_model, path和sign是否有值
                for field in ["base_model", "path", "sign"]:
                    if not is_string_valid(version.get(field)):
                        return ErrResponse(errnos.INVALID_VERSION_FIELD(field))

            # 调用API提交模型
            resp, err = await self.api_client.commit_bizy_model(payload=json_data)
            if err:
                return ErrResponse(err)

            # 开启线程检查同步状态
            threading.Thread(
                target=self.check_sync_status,
                args=(self, resp["id"], resp["version_ids"], sid),
                daemon=True,
            ).start()

            # enable refresh for lora
            # TODO: enable refresh for other types
            # bizyair.path_utils.path_manager.enable_refresh_options("loras")

            return OKResponse(resp)

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/models/query")
        async def query_my_models(request):
            # 获取查询参数
            mode = request.rel_url.query.get("mode", "")
            if not mode or mode not in ["my", "my_fork", "publicity"]:
                return ErrResponse(errnos.INVALID_QUERY_MODE)

            current = int(request.rel_url.query.get("current", "1"))
            page_size = int(request.rel_url.query.get("page_size", "10"))
            json_data = await request.json()
            keyword = json_data["keyword"]
            model_types = json_data.get("model_types", [])
            base_models = json_data.get("base_models", [])
            sort = json_data.get("sort", "")
            resp, err = None, None

            if mode in ["my", "my_fork"]:
                # 调用API查询模型
                resp, err = await self.api_client.query_models(
                    mode,
                    current,
                    page_size,
                    keyword=keyword,
                    model_types=model_types,
                    base_models=base_models,
                    sort=sort,
                )
            elif mode == "publicity":
                # 调用API查询社区模型
                resp, err = await self.api_client.query_community_models(
                    current,
                    page_size,
                    keyword=keyword,
                    model_types=model_types,
                    base_models=base_models,
                    sort=sort,
                )
            if err:
                return ErrResponse(err)

            return OKResponse(resp)

        @self.prompt_server.routes.get(f"/{COMMUNITY_API}/models/{{model_id}}/detail")
        async def get_model_detail(request):
            # 获取路径参数中的模型ID
            model_id = int(request.match_info["model_id"])

            # 检查model_id是否合法
            if not model_id or model_id <= 0:
                return ErrResponse(errnos.INVALID_MODEL_ID)

            source = request.rel_url.query.get("source", "")

            # 调用API获取模型详情
            resp, err = await self.api_client.get_model_detail(model_id, source)
            if err:
                return ErrResponse(err)

            return OKResponse(resp)

        @self.prompt_server.routes.delete(f"/{COMMUNITY_API}/models/{{model_id}}")
        async def delete_model(request):
            # 获取路径参数中的模型ID
            model_id = int(request.match_info["model_id"])

            # 检查model_id是否合法
            if not model_id or model_id <= 0:
                return ErrResponse(errnos.INVALID_MODEL_ID)

            # 调用API删除模型
            resp, err = await self.api_client.delete_bizy_model(model_id)
            if err:
                return ErrResponse(err)

            return OKResponse(resp)

        @self.prompt_server.routes.put(f"/{COMMUNITY_API}/models/{{model_id}}")
        async def update_model(request):
            sid = request.rel_url.query.get("clientId", "")
            if not is_string_valid(sid):
                return ErrResponse(errnos.INVALID_CLIENT_ID)
            # 获取路径参数中的模型ID
            model_id = int(request.match_info["model_id"])

            # 检查model_id是否合法
            if not model_id or model_id <= 0:
                return ErrResponse(errnos.INVALID_MODEL_ID)

            # 获取请求体数据
            json_data = await request.json()

            # 校验name和type
            err = check_str_param(json_data, "name", errnos.INVALID_NAME)
            if err is not None:
                return err

            if "/" in json_data["name"]:
                return ErrResponse(errnos.INVALID_NAME)

            err = check_type(json_data)
            if err is not None:
                return err

            # 校验versions
            if "versions" not in json_data or not isinstance(
                json_data["versions"], list
            ):
                return ErrResponse(errnos.INVALID_VERSIONS)

            versions = json_data["versions"]
            version_names = set()

            for version in versions:
                # 检查version是否重复
                if version.get("version") in version_names:
                    return ErrResponse(errnos.DUPLICATE_VERSION)

                # 检查version字段是否合法
                if not is_string_valid(version.get("version")) or "/" in version.get(
                    "version"
                ):
                    return ErrResponse(errnos.INVALID_VERSION_NAME)

                version_names.add(version.get("version"))

                # 检查base_model, path和sign是否有值
                for field in ["base_model", "path", "sign"]:
                    if not is_string_valid(version.get(field)):
                        return ErrResponse(errnos.INVALID_VERSION_FIELD(field))

            # 调用API更新模型
            resp, err = await self.api_client.update_model(
                model_id, json_data["name"], json_data["type"], versions
            )
            if err:
                return ErrResponse(err)

            # 开启线程检查同步状态
            threading.Thread(
                target=self.check_sync_status,
                args=(self, resp["id"], resp["version_ids"]),
                daemon=True,
            ).start()

            return OKResponse(None)

        @self.prompt_server.routes.post(
            f"/{COMMUNITY_API}/models/fork/{{model_version_id}}"
        )
        async def fork_model_version(request):
            try:
                # 获取version_id参数
                version_id = request.match_info["model_version_id"]
                if not version_id:
                    return ErrResponse(errnos.INVALID_MODEL_VERSION_ID)

                # 调用API fork模型版本
                _, err = await self.api_client.fork_model_version(version_id)
                if err:
                    return ErrResponse(err)

                return OKResponse(None)

            except Exception as e:
                print(f"\033[31m[BizyAir]\033[0m Fail to fork model version: {str(e)}")
                return ErrResponse(errnos.FORK_MODEL_VERSION)

        @self.prompt_server.routes.post(
            f"/{COMMUNITY_API}/models/like/{{model_version_id}}"
        )
        async def like_model_version(request):
            try:
                # 获取version_id参数
                version_id = request.match_info["model_version_id"]
                if not version_id:
                    return ErrResponse(errnos.INVALID_MODEL_VERSION_ID)

                # 调用API like模型版本
                _, err = await self.api_client.toggle_user_like(
                    "model_version", version_id
                )
                if err:
                    return ErrResponse(err)

                return OKResponse(None)

            except Exception as e:
                print(
                    f"\033[31m[BizyAir]\033[0m Fail to toggle like model version: {str(e)}"
                )
                return ErrResponse(errnos.TOGGLE_USER_LIKE)

        @self.prompt_server.routes.post(f"/{COMMUNITY_API}/files/upload")
        async def upload_file(request):
            try:
                # 获取上传的文件
                reader = await request.multipart()
                field = await reader.next()
                if not field or field.name != "file":
                    return ErrResponse(errnos.NO_FILE_UPLOAD)

                filename = field.filename
                if not filename:
                    return ErrResponse(errnos.NO_FILE_UPLOAD)

                # 读取文件内容
                file_content = await field.read(decode=False)

                filename = urllib.parse.quote(filename)
                # 获取上传凭证
                ret, err = await self.api_client.get_upload_token(filename=filename)
                if err:
                    return ErrResponse(err)

                # 解析返回的凭证信息
                file_info = ret["file"]
                storage_info = ret["storage"]

                def updateProgress(consume_bytes, total_bytes):
                    # do nothing
                    pass

                oss_client = AliOssStorageClient(
                    endpoint=storage_info.get("endpoint"),
                    bucket_name=storage_info.get("bucket"),
                    access_key=file_info.get("access_key_id"),
                    secret_key=file_info.get("access_key_secret"),
                    security_token=file_info.get("security_token"),
                    onUploading=updateProgress,
                    onInterrupted=None,
                )
                await oss_client.upload_file_content(
                    file_content=file_content,
                    file_name=filename,
                    object_name=file_info.get("object_key"),
                )
                return OKResponse(
                    {
                        "url": f'https://{storage_info.get("bucket")}.{storage_info.get("endpoint")}/{file_info.get("object_key")}'
                    }
                )

            except Exception as e:
                print(f"\033[31m[BizyAir]\033[0m Fail to upload file: {str(e)}")
                return ErrResponse(errnos.UPLOAD)

        @self.prompt_server.routes.get(
            f"/{COMMUNITY_API}/models/versions/{{model_version_id}}/workflow_json/{{sign}}"
        )
        async def get_workflow_json(request):
            model_version_id = int(request.match_info["model_version_id"])
            # 检查model_version_id是否合法
            if not model_version_id or model_version_id <= 0:
                return ErrResponse(errnos.INVALID_MODEL_VERSION_ID)

            sign = str(request.match_info["sign"])
            if not sign:
                return ErrResponse(errnos.INVALID_SIGN)

            # 获取上传凭证
            url, err = await self.api_client.get_download_url(
                sign=sign, model_version_id=model_version_id
            )
            if err:
                return ErrResponse(err)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return ErrResponse(
                                ErrorNo(
                                    response.status,
                                    response.status,
                                    None,
                                    "Failed to download JSON",
                                )
                            )
                        json_content = await response.json()
                return OKResponse(json_content)
            except Exception as e:
                print(f"\033[31m[BizyAir]\033[0m Fail to download JSON: {str(e)}")
                return ErrResponse(errnos.DOWNLOAD_JSON)

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

    def check_sync_status(self, bizy_model_id: str, version_ids: list, sid=None):
        while True:
            removed = []
            for version_id in version_ids:
                future = asyncio.run_coroutine_threadsafe(
                    self.api_client.get_model_version_detail(version_id=version_id),
                    self.loop,
                )

                model_version, err = future.result(timeout=2)

                if err is not None:
                    self.send_sync(
                        event="error",
                        data={
                            "message": err.message,
                            "code": err.code,
                            "data": {
                                "bizy_model_id": bizy_model_id,
                                "version_id": version_id,
                            },
                        },
                        sid=sid,
                    )
                    removed.append(version_id)
                    continue

                if model_version["available"]:
                    self.send_sync(
                        event="synced",
                        data={
                            "version_id": model_version["id"],
                            "version": model_version["version"],
                            "model_id": bizy_model_id,
                            "model_name": model_version["bizy_model_name"],
                        },
                        sid=sid,
                    )
                    removed.append(version_id)
                    return

            version_ids = [item for item in version_ids if item not in removed]
            time.sleep(5)
