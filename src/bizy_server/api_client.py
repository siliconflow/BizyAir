import json
import os
import urllib.parse
import urllib.request

import requests

import bizyair
import bizyair.common

from .errno import errnos, ErrorNo
from .error_handler import ErrorHandler

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://bizyair-api.siliconflow.cn/x/v1"
)


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
        return response.text

    def do_post(self, url, data=None, headers=None):
        if data:
            data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, timeout=3)
        return response.text

    def do_put(self, url, data=None, headers=None):
        if data:
            data = bytes(json.dumps(data), "utf-8")
        response = requests.put(url, data=data, headers=headers, timeout=3)
        return response.text

    def do_delete(self, url, data=None, headers=None):
        if data:
            data = bytes(json.dumps(data), "utf-8")
        response = requests.delete(url, data=data, headers=headers, timeout=3)
        return response.text

    async def user_info(self) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
        try:
            resp = self.do_get(server_url, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != errnos.OK:
                if ret["code"] == 401:
                    return None, errnos.INVALID_API_KEY
                else:
                    return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user info: {str(e)}")
            return None, errnos.GET_USER_INFO

    async def sign(self, signature: str) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files/{signature}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_get(server_url, params=None, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != errnos.OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None

        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to sign model: {str(e)}")
            return None, errnos.SIGN_FILE

    async def commit_file(self, signature: str, object_key: str) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files"

        payload = {
            "sign": signature,
            "object_key": object_key,
        }
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_post(server_url, data=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != errnos.OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit file: {str(e)}")
            return None, errnos.COMMIT_FILE

    async def commit_bizy_model(self, payload) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/bizy_models"

        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_post(server_url, data=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != errnos.OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit model: {str(e)}")
            return None, errnos.COMMIT_BIZY_MODEL
