import json
import os
import urllib.parse
import urllib.request

import requests

import bizyair
import bizyair.common

from .errno import ErrorNo, errnos
from .error_handler import ErrorHandler

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://bizyair-api.siliconflow.cn/x/v1"
)

CLIENT_VERSION = "v20241029"


class APIClient:
    def __init__(self):
        self.error_handler = ErrorHandler()

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

    def do_get(self, url, params=None, headers=None):
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        response = requests.get(url, params=params, headers=headers, timeout=3)
        resp_json = json.loads(response.text)
        if response.status_code != 200:
            return None, ErrorNo(
                response.status_code,
                resp_json.get("code", response.status_code),
                None,
                resp_json.get("message", response.text),
            )
        return resp_json, None

    def do_post(self, url, data=None, headers=None):
        if data:
            data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, timeout=3)
        resp_json = json.loads(response.text)
        if response.status_code != 200:
            return None, ErrorNo(
                response.status_code,
                resp_json.get("code", response.status_code),
                None,
                resp_json.get("message", response.text),
            )
        return resp_json, None

    def do_put(self, url, data=None, headers=None):
        if data:
            data = bytes(json.dumps(data), "utf-8")
        response = requests.put(url, data=data, headers=headers, timeout=3)
        resp_json = json.loads(response.text)
        if response.status_code != 200:
            return None, ErrorNo(
                response.status_code,
                resp_json.get("code", response.status_code),
                None,
                resp_json.get("message", response.text),
            )
        return resp_json, None

    def do_delete(self, url, data=None, headers=None):
        if data:
            data = bytes(json.dumps(data), "utf-8")
        response = requests.delete(url, data=data, headers=headers, timeout=3)
        resp_json = json.loads(response.text)
        if response.status_code != 200:
            return None, ErrorNo(
                response.status_code,
                resp_json.get("code", response.status_code),
                None,
                resp_json.get("message", response.text),
            )
        return resp_json, None

    async def user_info(self) -> tuple[dict | None, ErrorNo | None]:
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
        try:
            ret, err = self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user info: {str(e)}")
            return None, errnos.GET_USER_INFO

    async def sign(self, signature: str) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files/{signature}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = self.do_get(server_url, params=None, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None

        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to sign model: {str(e)}")
            return None, errnos.SIGN_FILE

    async def commit_file(
        self, signature: str, object_key: str
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files"

        payload = {
            "sign": signature,
            "object_key": object_key,
        }
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = self.do_post(server_url, data=payload, headers=headers)
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
            ret, err = self.do_post(server_url, data=payload, headers=headers)
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
            ret, err = self.do_delete(server_url, headers=headers)
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
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/community"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = self.do_get(server_url, params=params, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to query community models: {str(e)}")
            return None, errnos.QUERY_COMMUNITY_MODELS

    async def query_models(
        self,
        mode: str,
        current: int,
        page_size: int,
        keyword: str = None,
        model_types: list[str] = None,
        base_models: list[str] = None,
    ) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{mode}"
        params = {"current": current, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if model_types:
            params["model_types"] = model_types
        if base_models:
            params["base_models"] = base_models

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = self.do_get(server_url, params=params, headers=headers)
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
            ret, err = self.do_get(server_url, headers=headers)
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
            ret, err = self.do_get(server_url, headers=headers)
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
            ret, err = self.do_post(server_url, headers=headers)
            if err is not None:
                return None, err

            return None, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to fork model version: {str(e)}")
            return None, errnos.FORK_MODEL_VERSION

    async def update_model(
        self, model_id: int, name: str, type_: str, versions: list[dict]
    ) -> tuple[None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models/{model_id}"

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        data = {"name": name, "type": type_, "versions": versions}

        try:
            ret, err = self.do_put(server_url, data=data, headers=headers)
            if err is not None:
                return None, err

            return None, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to update model: {str(e)}")
            return None, errnos.UPDATE_MODEL

    async def get_upload_token(self) -> tuple[dict | None, ErrorNo | None]:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/upload/token"

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            ret, err = self.do_get(server_url, headers=headers)
            if err is not None:
                return None, err

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get upload token: {str(e)}")
            return None, errnos.GET_UPLOAD_TOKEN
