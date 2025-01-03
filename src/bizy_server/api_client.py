import os
import urllib

import aiohttp

import bizyair
import bizyair.common
from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS

from .errno import ErrorNo, errnos
from .error_handler import ErrorHandler
from .utils import is_string_valid

CLIENT_VERSION = "v20241029"


class APIClient:
    def __init__(self):
        self.error_handler = ErrorHandler()

    async def get_session(self):
        timeout = aiohttp.ClientTimeout(total=30)
        return aiohttp.ClientSession(timeout=timeout)

    def auth_header(self):
        try:
            api_key = bizyair.common.get_api_key()
            auth = f"Bearer {api_key}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": auth,
                "x-bizyair-client-version": CLIENT_VERSION,
            }
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
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status),
                        None,
                        resp_json.get("message", await response.text()),
                    )
                return resp_json, None

    async def do_post(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.post(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status),
                        None,
                        resp_json.get("message", await response.text()),
                    )
                return resp_json, None

    async def do_put(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.put(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status),
                        None,
                        resp_json.get("message", await response.text()),
                    )
                return resp_json, None

    async def do_delete(self, url, data=None, headers=None):
        async with await self.get_session() as session:
            async with session.delete(url, json=data, headers=headers) as response:
                resp_json = await response.json()
                if response.status != 200:
                    return None, ErrorNo(
                        response.status,
                        resp_json.get("code", response.status),
                        None,
                        resp_json.get("message", await response.text()),
                    )
                return resp_json, None

    async def user_info(self) -> tuple[dict | None, ErrorNo | None]:
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
        try:
            ret, err = await self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user info: {str(e)}")
            return None, errnos.GET_USER_INFO

    async def sign(
        self, signature: str, type: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files/{signature}"
        params = None
        if is_string_valid(type):
            params = {"type": type}

        headers, err = self.auth_header()
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
        self, signature: str, object_key: str, md5_hash: str, type: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files"

        payload = {
            "sign": signature,
            "object_key": object_key,
            "md5_hash": md5_hash,
            "type": type,
        }
        headers, err = self.auth_header()
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
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models"

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
        self, model_id: int
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{model_id}"

        headers, err = self.auth_header()
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
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/community"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header()
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
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/official"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header()
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
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{mode}"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models
        if sort:
            params["sort"] = sort

        headers, err = self.auth_header()
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
        self, model_id: int, source: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = (
            f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{model_id}/detail?source={source}"
        )

        headers, err = self.auth_header()
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
        self, version_id: int
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/versions/{version_id}"

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
                f"\033[31m[BizyAir]\033[0m Fail to get model version detail: {str(e)}"
            )
            return None, errnos.GET_MODEL_VERSION_DETAIL

    async def fork_model_version(self, version_id: int) -> tuple[None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/versions/{version_id}/fork"

        headers, err = self.auth_header()
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

    async def update_model(
        self, model_id: int, name: str, type_: str, versions: list[dict]
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{model_id}"

        headers, err = self.auth_header()
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
        self, filename: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/upload/token?file_name={filename}"

        headers, err = self.auth_header()
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
        self, like_type: str, object_id: str
    ) -> tuple[dict | None, ErrorNo | None]:
        if like_type == "model_version":
            server_url = (
                f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/versions/{object_id}/like"
            )
        else:
            return None, errnos.UNSUPPORT_LIKE_TYPE

        headers, err = self.auth_header()
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
        self, sign: str, model_version_id: int
    ) -> tuple[str | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files/temp-download/{sign}?version_id={model_version_id}"

        headers, err = self.auth_header()
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
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/{shareId}/models/files"
        try:

            def callback(ret: dict):
                if ret["code"] != errnos.OK.code:
                    return [], ErrorNo(500, ret["code"], None, f"{ret}")
                if not ret or "data" not in ret or ret["data"] is None:
                    return [], None

                outputs = [
                    x["label_path"] for x in ret["data"]["files"] if x["label_path"]
                ]
                outputs = bizyair.path_utils.filter_files_extensions(
                    outputs,
                    extensions=bizyair.path_utils.path_manager.supported_pt_extensions,
                )
                return outputs, None

            ret = await bizyair.common.client.async_send_request(
                method="GET", url=server_url, params=payload, callback=callback
            )
            return ret[0], ret[1]
        except Exception as e:
            print(
                f"\033[31m[BizyAir]\033[0m Fail to list share model files: response {ret} error {str(e)}"
            )
            return [], errnos.LIST_SHARE_MODEL_FILE_ERR
