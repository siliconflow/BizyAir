import asyncio
import json
import os
import urllib

import aiohttp
import bizyengine.core as core
from bizyengine.core.common import get_api_key
from bizyengine.core.common.env_var import (
    BIZYAIR_PRODUCTION_TEST,
    BIZYAIR_SERVER_MODE,
    BIZYAIR_X_SERVER,
    BIZYAIR_Y_SERVER,
)
from openai import OpenAI

from .errno import ErrorNo, errnos
from .error_handler import ErrorHandler
from .profile import user_profile
from .utils import is_string_valid

version_path = os.path.join(os.path.dirname(__file__), "..", "version.txt")
with open(version_path, "r") as file:
    CLIENT_VERSION = file.read().strip()

# API请求地址
QWEN_MODEL_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
QWEN_IMAGE_API_URL = "https://api.siliconflow.cn/v1/images/generations"


class APIClient:
    def __init__(self):
        self.error_handler = ErrorHandler()

    async def get_session(self):
        timeout = aiohttp.ClientTimeout(total=30)
        return aiohttp.ClientSession(timeout=timeout)

    def auth_header(self, api_key: str = None):
        try:
            if not BIZYAIR_SERVER_MODE:
                api_key = get_api_key()
            if not api_key:
                return None, errnos.INVALID_API_KEY
            auth = f"Bearer {api_key}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": auth,
                "x-bizyair-client-version": CLIENT_VERSION,
                "X-Client-Type": "bizyair",
            }
            if BIZYAIR_PRODUCTION_TEST != None:
                headers["x-bizyair-production-test"] = BIZYAIR_PRODUCTION_TEST
            if user_profile.getLang():
                headers["lang"] = user_profile.getLang()

            return headers, None
        except ValueError as e:
            error_message = e.args[0] if e.args else "Invalid API key"
            errnos.INVALID_API_KEY.message = error_message
            return None, errnos.INVALID_API_KEY

    async def do_get(self, url, params=None, headers=None):
        if params:
            query_string = urllib.parse.urlencode(params, doseq=True)
            url = f"{url}?{query_string}"
        async with await self.get_session() as session:
            async with session.get(url, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    isJson = isinstance(resp_json, dict)
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status) if isJson else resp_json,
                        None,
                        {
                            user_profile.getLang(): (
                                resp_json.get("message", await response.text())
                                if isJson
                                else resp_json
                            )
                        },
                    )
                return resp_json, None

    async def do_post(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.post(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    isJson = isinstance(resp_json, dict)
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status) if isJson else resp_json,
                        None,
                        {
                            user_profile.getLang(): (
                                resp_json.get("message", await response.text())
                                if isJson
                                else resp_json
                            )
                        },
                    )
                return resp_json, None

    async def do_put(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.put(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    isJson = isinstance(resp_json, dict)
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status) if isJson else resp_json,
                        None,
                        {
                            user_profile.getLang(): (
                                resp_json.get("message", await response.text())
                                if isJson
                                else resp_json
                            )
                        },
                    )
                return resp_json, None

    async def do_delete(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.delete(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    isJson = isinstance(resp_json, dict)
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status) if isJson else resp_json,
                        None,
                        {
                            user_profile.getLang(): (
                                resp_json.get("message", await response.text())
                                if isJson
                                else resp_json
                            )
                        },
                    )
                return resp_json, None

    async def user_info(self) -> tuple[dict | None, ErrorNo | None]:
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_X_SERVER}/user/info"
        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user info: {str(e)}")
            return None, errnos.GET_USER_INFO

    async def sign(
        self, signature: str, type: str, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/files/{signature}"
        params = None
        if is_string_valid(type):
            params = {"type": type}

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None

        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to sign model: {str(e)}")
            return None, errnos.SIGN_FILE

    async def commit_file(
        self,
        signature: str,
        object_key: str,
        md5_hash: str,
        type: str,
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/files"

        payload = {
            "sign": signature,
            "object_key": object_key,
            "md5_hash": md5_hash,
            "type": type,
        }
        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, data=payload, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit file: {str(e)}")
            return None, errnos.COMMIT_FILE

    async def commit_bizy_model(self, payload) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models"

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, data=payload, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit model: {str(e)}")
            return None, errnos.COMMIT_BIZY_MODEL

    async def delete_bizy_model(
        self, model_id: int, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/{model_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_delete(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to delete model: {str(e)}")
            return None, errnos.DELETE_BIZY_MODEL

    async def query_community_models(
        self,
        current: int,
        page_size: int,
        keyword: str = None,
        model_types: list[str] = None,
        base_models: list[str] = None,
        sort: str = None,
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/community"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query community models: {str(e)}")
            return None, errnos.QUERY_COMMUNITY_MODELS

    async def query_official_models(
        self,
        current: int,
        page_size: int,
        keyword: str = None,
        model_types: list[str] = None,
        base_models: list[str] = None,
        sort: str = None,
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/official"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query official models: {str(e)}")
            return None, errnos.QUERY_OFFICIAL_MODELS

    async def query_models(
        self,
        mode: str,
        current: int,
        page_size: int,
        keyword: str = None,
        model_types: list[str] = None,
        base_models: list[str] = None,
        sort: str = None,
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/{mode}"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query models: {str(e)}")
            return None, errnos.QUERY_MODELS

    async def get_model_detail(
        self, model_id: int, source: str, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/{model_id}/detail?source={source}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get model detail: {str(e)}")
            return None, errnos.GET_MODEL_DETAIL

    async def get_model_version_detail(
        self, version_id: int, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/versions/{version_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to get model version detail: {str(e)}"
            )
            return None, errnos.GET_MODEL_VERSION_DETAIL

    async def fork_model_version(
        self, version_id: int, request_api_key: str = None
    ) -> tuple[None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/versions/{version_id}/fork"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, headers=headers)
            if err is not None:
                return None, err

            return None, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to fork model version: {str(e)}")
            return None, errnos.FORK_MODEL_VERSION

    async def unfork_model_version(
        self, version_id: int, request_api_key: str = None
    ) -> tuple[None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/versions/{version_id}/fork"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_delete(server_url, headers=headers)
            if err is not None:
                return None, err

            return None, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to unfork model version: {str(e)}")
            return None, errnos.UNFORK_MODEL_VERSION

    async def update_model(
        self,
        model_id: int,
        name: str,
        type_: str,
        versions: list[dict],
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/bizy_models/{model_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        data = {"name": name, "type": type_, "versions": versions}

        try:
            ret, err = await self.do_put(server_url, data=data, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to update model: {str(e)}")
            return None, errnos.UPDATE_MODEL

    async def get_upload_token(
        self, filename: str, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={filename}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get upload token: {str(e)}")
            return None, errnos.GET_UPLOAD_TOKEN

    async def toggle_user_like(
        self, like_type: str, object_id: str, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        if like_type == "model_version":
            server_url = f"{BIZYAIR_X_SERVER}/bizy_models/versions/{object_id}/like"
        else:
            return None, errnos.UNSUPPORT_LIKE_TYPE

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to toggle user like: {str(e)}")
            return None, errnos.TOGGLE_USER_LIKE

    async def get_download_url(
        self, sign: str, model_version_id: int, request_api_key: str = None
    ) -> tuple[str | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/files/temp-download/{sign}?version_id={model_version_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"]["url"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get download url: {str(e)}")
            return None, errnos.GET_DOWNLOAD_URL

    async def get_share_model_files(self, shareId, payload) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_X_SERVER}/{shareId}/models/files"
        try:

            def callback(ret: dict):
                if ret["code"] != errnos.OK.code:
                    return [], ErrorNo(
                        500, ret["code"], None, {user_profile.getLang(): ret["message"]}
                    )
                if not ret or "data" not in ret or ret["data"] is None:
                    return [], None

                outputs = [
                    x["label_path"] for x in ret["data"]["files"] if x["label_path"]
                ]
                outputs = core.path_utils.filter_files_extensions(
                    outputs,
                    extensions=core.path_utils.path_manager.supported_pt_extensions,
                )
                return outputs, None

            ret = await core.common.client.async_send_request(
                method="GET", url=server_url, params=payload, callback=callback
            )
            return ret[0], ret[1]
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to list share model files: response {ret} error {str(e)}"
            )
            return [], errnos.LIST_SHARE_MODEL_FILE_ERR

    async def commit_dataset(
        self, payload, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, data=payload, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit dataset: {str(e)}")
            return None, errnos.COMMIT_DATASET

    async def update_dataset(
        self,
        dataset_id: int,
        name: str,
        versions: list[dict],
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets/{dataset_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        data = {"name": name, "versions": versions}

        try:
            ret, err = await self.do_put(server_url, data=data, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to update dataset: {str(e)}")
            return None, errnos.UPDATE_DATASET

    async def get_dataset_version_detail(
        self, version_id: int, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets/versions/{version_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to get dataset version detail: {str(e)}"
            )
            return None, errnos.GET_MODEL_VERSION_DETAIL

    async def delete_dataset(
        self, dataset_id: int, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets/{dataset_id}"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_delete(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to delete dataset: {str(e)}")
            return None, errnos.DELETE_DATASET

    async def query_datasets(
        self,
        current: int,
        page_size: int,
        keyword: str = None,
        annotated: str = None,
        request_api_key: str = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if annotated:
            params["annotated"] = annotated

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query datasets: {str(e)}")
            return None, errnos.QUERY_DATASETS

    async def get_dataset_detail(
        self, dataset_id: int, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/datasets/{dataset_id}/detail"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get dataset detail: {str(e)}")
            return None, errnos.GET_DATASET_DETAIL

    async def create_share(
        self, payload, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/share"

        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, data=payload, headers=headers)
            if err is not None:
                return None, err
            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to create share: {str(e)}")
            return None, errnos.CREATE_SHARE

    async def get_share_detail(self, code: str) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/share/{code}"

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get share detail: {str(e)}")
            return None, errnos.GET_SHARE_DETAIL

    async def get_data_dict(
        self, request_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/dict"
        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get data dict: {str(e)}")
            return None, errnos.GET_DATA_DICT

    async def get_notification_unread_count(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/notifications/unread_count"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to get notification unread counts: {str(e)}"
            )
            return None, errnos.GET_NOTIF_UNREAD_COUNT

    async def fetch_notifications(
        self,
        page_size: int,
        last_pm_id: int,
        last_broadcast_id: int,
        types: list | None,
        read_status: bool | None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/notifications"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        params = {"page_size": page_size}
        if last_pm_id > 0:
            params["last_pm_id"] = last_pm_id
        if last_broadcast_id > 0:
            params["last_broadcast_id"] = last_broadcast_id
        if types and len(types) > 0:
            params["types"] = types
        if read_status:
            params["read_status"] = read_status

        try:
            ret, err = await self.do_get(server_url, headers=headers, params=params)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query notifications: {str(e)}")
            return None, errnos.QUERY_NOTIF

    async def read_notifications(
        self, notif_ids: list[int]
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/notifications/read"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        if notif_ids is None or len(notif_ids) < 1:
            return None, errnos.INVALID_NOTIF_ID

        payload = {"ids": notif_ids}

        try:
            ret, err = await self.do_post(server_url, headers=headers, data=payload)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to mark notifications as read: {str(e)}"
            )
            return None, errnos.READ_NOTIF

    async def read_all_notifications(
        self, type: int
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/notifications/read_all"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        payload = {}
        if type > 0:
            payload["type"] = type

        try:
            ret, err = await self.do_post(server_url, headers=headers, data=payload)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to mark all notifications as read: {str(e)}"
            )
            return None, errnos.READ_ALL_NOTIF

    async def get_wallet(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/wallet"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get wallet info: {str(e)}")
            return None, errnos.GET_WALLET_INFO

    async def query_coins(
        self, current: int, page_size: int, coin_type: int = 0, expire_days: int = 0
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/coins"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        params = {"current": current, "page_size": page_size}
        if coin_type > 0:
            params["coin_type"] = coin_type
        if expire_days > 0:
            params["expire_days"] = expire_days

        try:
            ret, err = await self.do_get(server_url, headers=headers, params=params)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query coins: {str(e)}")
            return None, errnos.QUERY_COINS

    async def get_user_metadata(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/user/metadata"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user metadata: {str(e)}")
            return None, errnos.GET_USER_METADATA

    async def update_user_info(
        self, name: str = None, avatar: str = None, introduction: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/user/metadata"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        payload = {}
        if name is not None:
            payload["name"] = name
        if avatar is not None:
            payload["avatar"] = avatar
        if introduction is not None:
            payload["introduction"] = introduction

        try:
            ret, err = await self.do_put(server_url, headers=headers, data=payload)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to update user info: {str(e)}")
            return None, errnos.UPDATE_USER_INFO

    async def user_real_name(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_X_SERVER}/user/real_name"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_post(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to verify real name: {str(e)}")
            return None, errnos.USER_REAL_NAME

    async def buy_product(
        self, product_id: int, platform: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/pay/product/{product_id}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        payload = {}
        if platform is not None:
            payload["platform"] = platform

        try:
            ret, err = await self.do_post(server_url, headers=headers, data=payload)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to buy product: {str(e)}")
            return None, errnos.BUY_PRODUCT

    async def get_pay_status(self, orderNum: str) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/pay/orders/{orderNum}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get pay status: {str(e)}")
            return None, errnos.PAY_STATUS

    async def cancel_pay_order(
        self, orderNum: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/pay/orders/{orderNum}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_delete(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to cancel payment: {str(e)}")
            return None, errnos.PAY_CANCEL

    async def list_pay_orders(
        self, current: int, page_size: int, status: str | None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/pay/page"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        params = {"current": current, "page_size": page_size}
        if status is not None:
            params["status"] = status

        try:
            ret, err = await self.do_get(server_url, headers=headers, params=params)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to list pay orders: {str(e)}")
            return None, errnos.LIST_PAY_ORDER

    async def list_products(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/products"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to list products: {str(e)}")
            return None, errnos.LIST_PRODUCTS

    async def get_year_cost(
        self, year: str = None, query_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/invoices/year_cost"
        params = {}
        if year:
            params["year"] = year
        if query_api_key:
            params["api_key"] = query_api_key

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get year cost: {str(e)}")
            return None, errnos.GET_YEAR_COST

    async def get_month_cost(
        self, month: str = None, query_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/invoices/month_cost"
        params = {}
        if month:
            params["month"] = month
        if query_api_key:
            params["api_key"] = query_api_key

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get month cost: {str(e)}")
            return None, errnos.GET_MONTH_COST

    async def get_day_cost(
        self, day: str = None, query_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/invoices/day_cost"
        params = {}
        if day:
            params["date"] = day
        if query_api_key:
            params["api_key"] = query_api_key

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get day cost: {str(e)}")
            return None, errnos.GET_DAY_COST

    async def get_recent_cost(
        self, query_api_key: str = None
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_Y_SERVER}/invoices/recent_cost"
        params = {}
        if query_api_key:
            params["api_key"] = query_api_key

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = await self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get recent cost: {str(e)}")
            return None, errnos.GET_RECENT_COST

    def forward_model_request(self, request_data):
        try:
            api_key = get_api_key()
            if not api_key:
                return None, errnos.INVALID_API_KEY

            request_data["stream"] = True
            # 硅基云API接受top_k但是openai库不支持
            request_data.pop("top_k")
            # 参数检查
            if "messages" not in request_data:
                return None, errnos.MODEL_API_ERROR

            if (
                not isinstance(request_data["messages"], list)
                or len(request_data["messages"]) == 0
            ):
                return None, errnos.MODEL_API_ERROR

            if "model" not in request_data:
                return None, errnos.MODEL_API_ERROR

            # TODO: 前端能选择provider、model之后删除下句，但目前无此规划是写死的模型
            request_data["model"] = f"SiliconFlow:{request_data['model']}"

            # 获取前端生成的request_id和prompt_id
            request_id = request_data.pop("request_id", None)
            prompt_id = request_data.pop("prompt_id", None)
            extra_body = {}
            if request_id:
                extra_body["request_id"] = request_id
            if prompt_id:
                extra_body["prompt_id"] = prompt_id

            client = OpenAI(
                base_url=BIZYAIR_X_SERVER,
                api_key=api_key,
                timeout=60.0,
                max_retries=0,
            )
            return client.chat.completions.with_streaming_response.create(
                extra_body=extra_body, **request_data
            )

        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Model API forwarding failed: {str(e)}")
            return None, errnos.MODEL_API_ERROR

    async def forward_image_request(self, request_data):
        try:
            api_key = get_api_key()
            if not api_key:
                return None, errnos.INVALID_API_KEY
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            # 创建异步HTTP会话
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    QWEN_IMAGE_API_URL, headers=headers, json=request_data
                ) as response:
                    # 读取并解析响应
                    if response.status != 200:
                        error_text = await response.text()
                        print(
                            f"\033[31m[BizyAir]\033[0m Image generation failed: {error_text}"
                        )
                        return None, errnos.MODEL_API_ERROR

                    result = await response.json()
                    return result, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Image generation request failed: {str(e)}")
            return None, errnos.MODEL_API_ERROR

    async def fetch_all_llm_models(self, request_api_key: str = None):
        url = f"{BIZYAIR_X_SERVER}/llm/models"
        headers, err = self.auth_header(api_key=request_api_key)
        if err is not None:
            print(f"fetch_all_models: error getting headers: {err}")
            return []
        params = {"type": "text", "sub_type": "chat"}

        try:
            data, err = await self.do_get(url, params=params, headers=headers)
            if err is not None:
                print(f"fetch_all_models: error fetching models: {err}")
                return []

            all_models = [model["id"] for model in data["data"]]
            return all_models
        except aiohttp.ClientError as e:
            print(f"Error fetching models: {e}")
            return []
        except asyncio.exceptions.TimeoutError:
            print("Request to fetch models timed out")
            return []
