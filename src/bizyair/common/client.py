import json
import pprint
import time
import urllib.error
import urllib.request
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Union

import aiohttp
import comfy

__all__ = ["send_request"]

from dataclasses import dataclass, field

from .env_var import BIZYAIR_API_KEY, BIZYAIR_DEBUG, BIZYAIR_SERVER_ADDRESS

IS_API_KEY_VALID = None


@dataclass
class APIKeyState:
    current_api_key: str = field(default=None)
    is_valid: bool = field(default=None)


api_key_state = APIKeyState()


def set_api_key(api_key: str = "YOUR_API_KEY", override: bool = False):
    global BIZYAIR_API_KEY, api_key_state
    if api_key_state.is_valid is not None and not override:
        warnings.warn("API key has already been set and will not be overridden.")
        return
    if validate_api_key(api_key):
        BIZYAIR_API_KEY = api_key
        api_key_state.is_valid = True
        print("\033[92mAPI key is set successfully.\033[0m")
    else:
        api_key_state.is_valid = False
        warnings.warn("Invalid API key provided.")


def validate_api_key(api_key: str = None) -> bool:
    global api_key_state
    if not api_key or not isinstance(api_key, str):
        warnings.warn("API key is not set.")
        return False
    # if api_key_state.current_api_key == api_key and api_key_state.is_valid is not None:
    #     return api_key_state.is_valid
    api_key_state.current_api_key = api_key
    url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}

    try:
        response_data = send_request(
            method="GET", url=url, headers=headers, callback=None
        )
        if "message" not in response_data or response_data["message"] != "Ok":
            api_key_state.is_valid = False
            print(f"\033[91mAPI key validation failed. API Key: {api_key}\033[0m")
        else:
            api_key_state.is_valid = True
    except Exception as e:
        api_key_state.is_valid = False
        print(f"\033[91mError validating API key: {api_key}, error: {e}\033[0m")
    return api_key_state.is_valid


def get_api_key() -> str:
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


def process_response_data(response_data: dict) -> dict:
    # Check if 'result' key exists, indicating a cloud response
    if "result" in response_data:
        try:
            msg = json.loads(response_data["result"])
        except json.JSONDecodeError:
            raise ValueError(f"Failed to decode JSON from response. {response_data=}")
    else:
        # Handle local response directly
        msg = response_data

    return msg  # Return processed data or modify as needed


def send_request(
    method: str = "POST",
    url: str = None,
    data: bytes = None,
    verbose=False,
    callback: callable = process_response_data,
    response_handler: callable = json.loads,
    **kwargs,
) -> Union[dict, Any]:
    try:
        headers = kwargs.pop("headers") if "headers" in kwargs else _headers()
        headers["User-Agent"] = "BizyAir Client"

        req = urllib.request.Request(
            url, data=data, headers=headers, method=method, **kwargs
        )
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        error_message = str(e)
        if verbose:
            print(f"URLError encountered: {error_message}")
        if "Unauthorized" in error_message:
            raise PermissionError(
                "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
                "If you have the key, please click the 'BizyAir Key' button at the bottom right to set the key."
            )
        else:
            raise ConnectionError(
                f"Failed to connect to the server: {error_message}.\n"
                + "Please check your API key and ensure the server is reachable.\n"
                + "Also, verify your network settings and disable any proxies if necessary.\n"
                + "After checking, please restart the ComfyUI service."
            )
    if response_handler:
        response_data = response_handler(response_data)
    if callback:
        return callback(response_data)
    return response_data


async def async_send_request(
    method: str = "POST",
    url: str = None,
    data: bytes = None,
    verbose=False,
    callback: callable = process_response_data,
    **kwargs,
) -> dict:
    headers = kwargs.pop("headers") if "headers" in kwargs else _headers()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, data=data, headers=headers, **kwargs
            ) as response:
                response_data = await response.text()
                if response.status != 200:
                    error_message = f"HTTP Status {response.status}"
                    if verbose:
                        print(f"Error encountered: {error_message}")
                    if response.status == 401:
                        raise PermissionError(
                            "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
                            "If you have the key, please click the 'BizyAir Key' button at the bottom right to set the key."
                        )
                    else:
                        raise ConnectionError(
                            f"Failed to connect to the server: {error_message}.\n"
                            + "Please check your API key and ensure the server is reachable.\n"
                            + "Also, verify your network settings and disable any proxies if necessary.\n"
                            + "After checking, please restart the ComfyUI service."
                        )
                if callback:
                    return callback(json.loads(response_data))
                return json.loads(response_data)
    except aiohttp.ClientError as e:
        print(f"Error fetching data: {e}")
        return {}
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return {}


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


def get_task_result(task_id: str, offset: int = 0) -> dict:
    """
    Get the result of a task.
    """
    import requests

    url = f"https://uat-bizyair-api.siliconflow.cn/x/v1/bizy_task/{task_id}"
    response_json = send_request(
        method="GET", url=url, data=json.dumps({"offset": offset}).encode("utf-8")
    )
    out = response_json
    events = out.get("data", {}).get("events", [])
    new_events = []
    for event in events:
        if (
            "data" in event
            and isinstance(event["data"], str)
            and event["data"].startswith("https://")
        ):
            event["data"] = requests.get(event["data"]).json()
        new_events.append(event)
    out["data"]["events"] = new_events
    return out


@dataclass
class BizyAirTask:
    TASK_DATA_STATUS = ["PENDING", "PROCESSING", "COMPLETED"]
    task_id: str
    data_pool: list[dict] = field(default_factory=list)
    data_status: str = None

    @staticmethod
    def check_inputs(inputs: dict) -> bool:
        return (
            inputs.get("code") == 20000
            and inputs.get("status", False)
            and "task_id" in inputs.get("data", {})
        )

    @classmethod
    def from_data(cls, inputs: dict, check_inputs: bool = True) -> "BizyAirTask":
        if check_inputs and not cls.check_inputs(inputs):
            raise ValueError(f"Invalid inputs: {inputs}")
        data = inputs.get("data", {})
        task_id = data.get("task_id", "")
        return cls(task_id=task_id, data_pool=[], data_status="started")

    def is_finished(self) -> bool:
        if not self.data_pool:
            return False
        if self.data_pool[-1].get("data_status") == self.TASK_DATA_STATUS[-1]:
            return True
        return False

    def send_request(self, offset: int = 0) -> dict:
        if offset >= len(self.data_pool):
            return get_task_result(self.task_id, offset)
        else:
            return self.data_pool[offset]

    def get_data(self, offset: int = 0) -> dict:
        if offset >= len(self.data_pool):
            return {}
        return self.data_pool[offset]

    @staticmethod
    def _fetch_remote_data(url: str) -> dict:
        import requests

        return requests.get(url).json()

    def get_last_data(self) -> dict:
        return self.get_data(len(self.data_pool) - 1)

    def do_task_until_completed(
        self, *, timeout: int = 480, poll_interval: float = 1
    ) -> list[dict]:
        offset = 0
        start_time = time.time()
        pbar = None
        while not self.is_finished():
            try:
                print(f"do_task_until_completed: {offset}")
                data = self.send_request(offset)
                data_lst = self._extract_data_list(data)
                self.data_pool.extend(data_lst)
                offset += len(data_lst)
                for data in data_lst:
                    message = data.get("data", {}).get("message", {})
                    if (
                        isinstance(message, dict)
                        and message.get("event", None) == "progress"
                    ):
                        value = message["data"]["value"]
                        total = message["data"]["max"]
                        if pbar is None:
                            pbar = comfy.utils.ProgressBar(total)
                        pbar.update_absolute(value + 1, total, None)
            except Exception as e:
                print(f"Exception: {e}")

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for task {self.task_id} to finish")

            time.sleep(poll_interval)

        return self.data_pool

    def _extract_data_list(self, data):
        data_lst = data.get("data", {}).get("events", [])
        if not data_lst:
            raise ValueError(f"No data found in task {self.task_id}")
        return data_lst
