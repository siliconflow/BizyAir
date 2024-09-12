import json
import pprint
import urllib.error
import urllib.request
import warnings
from typing import Dict

__all__ = ["send_request"]

from .env_var import BIZYAIR_API_KEY, BIZYAIR_DEBUG


def set_api_key(API_KEY="YOUR_API_KEY"):
    global BIZYAIR_API_KEY
    if validate_api_key(BIZYAIR_API_KEY):
        warnings.warn("API key has already been set", RuntimeWarning)
    elif validate_api_key(API_KEY):
        BIZYAIR_API_KEY = API_KEY


IS_API_KEY_VALID = None


def validate_api_key(api_key):
    global IS_API_KEY_VALID
    if api_key is None:
        return False
    if IS_API_KEY_VALID is not None:
        return IS_API_KEY_VALID

    url = "https://api.siliconflow.cn/v1/user/info"
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
            response_data = json.loads(response_data)
            if "message" not in response_data:
                IS_API_KEY_VALID = False
            if response_data["message"] != "Ok":
                IS_API_KEY_VALID = False
            IS_API_KEY_VALID = True
    except Exception as e:
        print(
            "\n\n\033[91m[BizyAir]\033[0m "
            f"Fail to validate the api key: {api_key}, with error {e} \n\n"
        )
        print(f"")
        IS_API_KEY_VALID = False
    finally:
        return IS_API_KEY_VALID


def get_api_key():
    global BIZYAIR_API_KEY
    if not validate_api_key(BIZYAIR_API_KEY):
        error_message = (
            "BIZYAIR_API_KEY is not set or invalid. "
            "Please refer to cloud.siliconflow.cn to get a valid API key. "
            f"Current BIZYAIR_API_KEY: {BIZYAIR_API_KEY}"
        )
        raise ValueError(error_message)
    return BIZYAIR_API_KEY


def _headers():
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {get_api_key()}",
    }
    return headers


def send_request(
    method: str = "POST", url: str = None, data: bytes = None, verbose=False, **kwargs
) -> Dict:
    try:
        headers = kwargs.pop("headers", _headers())
        req = urllib.request.Request(
            url, data=data, headers=headers, method=method, **kwargs
        )
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        error_message = str(e)
        print(f"{error_message=}")
        if "Unauthorized" in error_message:
            raise Exception(
                "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
                "If you have the key, please click the 'BizyAir Key' button at the bottom right to set the key."
            )
        else:
            raise Exception(
                f"Failed to connect to the server: {error_message}, if you have no key, "
            )
    try:
        ret = json.loads(response_data)
        if "result" in ret:  # cloud
            msg = json.loads(ret["result"])
        else:  # local
            msg = ret
        return msg
    except json.decoder.JSONDecodeError:
        pprint.pprint(response_data)


def fetch_models_by_type(
    url: str, model_type: str, *, method="GET", verbose=False
) -> dict:
    if not validate_api_key(BIZYAIR_API_KEY):
        return {}

    payload = {"type": model_type}
    if BIZYAIR_DEBUG:
        pprint.pprint(payload)
    msg = send_request(
        method=method,
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        verbose=verbose,
    )
    return msg
