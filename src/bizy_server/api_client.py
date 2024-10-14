import os
import urllib.parse
import urllib.request
from collections import defaultdict

import requests
import json

from .errno import INVALID_API_KEY_ERR, ErrorNo, CODE_OK, UPDATE_SHATE_ID_ERR, GET_DESCRIPTION_ERR, \
    UPDATE_DESCRIPTION_ERR, CHECK_MODEL_EXISTS_ERR, SIGN_FILE_ERR, COMMIT_FILE_ERR, COMMIT_MODEL_ERR, DELETE_MODEL_ERR, \
    CHANGE_PUBLIC_ERR, CODE_NO_MODEL_FOUND, LIST_MODEL_FILE_ERR, LIST_SHARE_MODEL_FILE_ERR, LIST_MODEL_ERR, \
    GET_USER_INFO_ERR
from .error_handler import ErrorHandler
import bizyair
import bizyair.common

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
            INVALID_API_KEY_ERR.message = error_message
            return None, INVALID_API_KEY_ERR

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

    async def check_model(self, type: str, name: str) -> (bool, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models/check"

        payload = {
            "name": name,
            "type": type,
        }
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_get(server_url, params=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to check model: {str(e)}")
            return None, CHECK_MODEL_EXISTS_ERR

    async def sign(self, signature: str) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/files/{signature}"
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_get(server_url, params=None, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None

        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to sign model: {str(e)}")
            return None, SIGN_FILE_ERR

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
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit file: {str(e)}")
            return None, COMMIT_FILE_ERR

    async def commit_model(
            self, model_files, model_name: str, model_type: str, overwrite: bool
    ) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models"

        payload = {
            "name": model_name,
            "type": model_type,
            "overwrite": overwrite,
            "files": model_files,
        }
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        try:
            resp = self.do_post(server_url, data=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to commit model: {str(e)}")
            return None, COMMIT_MODEL_ERR

    async def remove_model(self, model_name: str, model_type: str) -> ErrorNo:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models"

        payload = {
            "name": model_name,
            "type": model_type,
        }
        headers, err = self.auth_header()
        if err is not None:
            return err

        try:
            resp = self.do_delete(server_url, data=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return ErrorNo(500, ret["code"], None, ret["message"])

            return None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to remove model: {str(e)}")
            return DELETE_MODEL_ERR

    async def change_public(
            self, model_name: str, model_type: str, public: bool
    ) -> ErrorNo:
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models/change_public"

        payload = {
            "name": model_name,
            "type": model_type,
            "public": public,
        }
        headers, err = self.auth_header()
        if err is not None:
            return err

        try:
            resp = self.do_put(server_url, data=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return ErrorNo(500, ret["code"], None, ret["message"])

            return None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to change model visibility: {str(e)}")
            return CHANGE_PUBLIC_ERR

    async def get_model_files(self, payload) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models/files"
        try:
            resp = self.do_get(server_url, params=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                if ret["code"] == CODE_NO_MODEL_FOUND:
                    return [], None
                else:
                    return None, ErrorNo(500, ret["code"], None, ret["message"])

            if not ret["data"]:
                return [], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to list model files: {str(e)}")
            return None, LIST_MODEL_FILE_ERR

        files = ret["data"]["files"]
        result = []
        if len(files) > 0:
            tree = defaultdict(lambda: {"name": "", "list": []})

            for item in files:
                parts = item["label_path"].split("/")
                model_name = parts[0]
                if model_name not in tree:
                    tree[model_name] = {"name": model_name, "list": [item]}
                else:
                    tree[model_name]["list"].append(item)
            result = list(tree.values())

        return result, None

    async def get_share_model_files(self, shareId, payload) -> (dict, ErrorNo):
        server_url = f"{BIZYAIR_SERVER_ADDRESS}/{shareId}/models/files"
        try:

            def callback(ret: dict):
                if ret["code"] != CODE_OK:
                    if ret["code"] == CODE_NO_MODEL_FOUND:
                        return [], None
                    else:
                        return [], ErrorNo(500, ret["code"], None, ret["message"])

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
            print(f"\033[31m[BizyAir]\033[0m Fail to list share model files: {str(e)}")
            return [], LIST_SHARE_MODEL_FILE_ERR

    async def get_models(self, payload) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models"
        try:
            resp = self.do_get(server_url, params=payload, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            if not ret["data"]:
                return [], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to list model: {str(e)}")
            return None, LIST_MODEL_ERR

        models = ret["data"]["models"]
        return models, None

    async def user_info(self) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
        try:
            resp = self.do_get(server_url, headers=headers)
            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                if ret["code"] == 401:
                    return None, INVALID_API_KEY_ERR
                else:
                    return None, ErrorNo(500, ret["code"], None, ret["message"])

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get user info: {str(e)}")
            return None, GET_USER_INFO_ERR

    async def update_share_id(self, share_id) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/user/update_share_id"
        try:
            resp = self.do_put(server_url, data={
                "share_id": share_id
            }, headers=headers)

            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return {}, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to update share_id: {str(e)}")
            return None, UPDATE_SHATE_ID_ERR

    async def get_description(self, payload) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models/get_description"
        try:
            resp = self.do_get(server_url, params=payload, headers=headers)

            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            if not ret["data"]:
                return {}, None

            return ret["data"], None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get description: {str(e)}")
            return None, GET_DESCRIPTION_ERR

    async def update_description(self, payload) -> (dict, ErrorNo):
        headers, err = self.auth_header()
        if err is not None:
            return None, err

        server_url = f"{BIZYAIR_SERVER_ADDRESS}/models/update_description"
        try:
            resp = self.do_put(server_url, data=payload, headers=headers)

            ret = json.loads(resp)
            if ret["code"] != CODE_OK:
                return None, ErrorNo(500, ret["code"], None, ret["message"])

            return {}, None
        except Exception as e:
            print(f"\033[31m[BizyAir]\033[0m Fail to get description: {str(e)}")
            return None, UPDATE_DESCRIPTION_ERR
