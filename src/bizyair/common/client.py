import json
import os
import urllib.error
import urllib.request
from typing import Dict

__all__ = ["send_request"]

from .env_var import BIZYAIR_API_KEY, BIZYAIR_DEBUG, BIZYAIR_DEV_REQUEST_URL


def set_api_key(API_KEY="YOUR_API_KEY"):
    global BIZYAIR_API_KEY
    BIZYAIR_API_KEY = API_KEY


def validate_api_key(api_key):
    if api_key is None or not api_key.startswith("sk-"):
        return False
    return True


def get_api_key():
    global BIZYAIR_API_KEY
    if not validate_api_key(BIZYAIR_API_KEY):
        error_message = (
            "BIZYAIR_API_KEY is not set or invalid. "
            "Please provide a valid API key starting with 'sk-'. "
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

        if BIZYAIR_DEV_REQUEST_URL:
            url = BIZYAIR_DEV_REQUEST_URL
        if BIZYAIR_DEBUG:
            print(f"{method=} {url=}")
        if verbose:
            print(f"{method=} {url=} {headers=} {data=}")
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
    ret = json.loads(response_data)
    if "result" in ret:  # cloud

        msg = json.loads(ret["result"])
    else:  # local
        msg = ret
    return msg


def fetch_models_by_type(url: str, model_type: str, *, verbose=False) -> dict:
    if not validate_api_key(BIZYAIR_API_KEY):
        return {}

    payload = {
        "api_key": get_api_key(),
        "model_type": model_type,
        "secret": "6x7=42",
    }
    msg = send_request(
        url=url, data=json.dumps(payload).encode("utf-8"), verbose=verbose
    )
    return msg


# class BaseClient:
#     def __init__(self, api_url, api_key: str = None):
#         self.api_url = api_url
#         self.API_KEY: str = api_key

#     def get_headers(self, sse=False):
#         if self.API_KEY is None or not self.API_KEY.startswith("sk-"):
#             raise ValueError(
#                 f"API key is not set. Please provide a valid API key, {self.API_KEY=}"
#             )

#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "authorization": f"Bearer {self.API_KEY}",
#         }

#         if sse:
#             headers["accept"] = "text/event-stream"

#         return headers

#     def _handle_url_error(self, e):
#         error_message = str(e)
#         if "Unauthorized" in error_message:
#             raise Exception(
#                 "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
#                 "If you have the key, please click the 'BizyAir Key' button at the bottom right to set the key."
#             )
#         else:
#             raise Exception(
#                 f"Failed to connect to the server: {e}, if you have no key, "
#             )


# class BizyAirRequestClient(BaseClient):
#     def __init__(self, api_url, workflow_api, api_key=None):
#         super().__init__(api_url, api_key)
#         self.workflow_api = workflow_api

#     def send_request(self):
#         try:
#             data = json.dumps(self.workflow_api).encode("utf-8")
#             req = urllib.request.Request(
#                 self.api_url, data=data, headers=self.get_headers(), method="GET"
#             )
#             with urllib.request.urlopen(req) as response:
#                 response_data = response.read().decode("utf-8")
#                 return response_data
#         except urllib.error.URLError as e:
#             self._handle_url_error(e)


# class BizyAirStreamClient(BaseClient):
#     def __init__(self, api_url, workflow_api, api_key=None):
#         super().__init__(api_url, api_key)
#         self.workflow_api = workflow_api
#         self.response = None

#     def __enter__(self):
#         data = json.dumps(self.workflow_api).encode("utf-8")
#         req = urllib.request.Request(
#             self.api_url, data=data, headers=self.get_headers(sse=True), method="POST"
#         )
#         self.response = urllib.request.urlopen(req)
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         if self.response:
#             self.response.close()

#     def events(self):
#         try:
#             for line in self.response:
#                 decoded_line = line.decode("utf-8")
#                 if decoded_line.startswith("data:"):
#                     event_data = decoded_line[5:].strip()
#                     yield event_data
#         except GeneratorExit:
#             self.close()

#     def close(self):
#         if self.response:
#             self.response.close()


# # Example usage
# if __name__ == "__main__":
#     api_url = "http://0.0.0.0:8000/supernode/test-dummy1"
#     workflow_api = {"key1": "value1", "key2": "value2"}
#     api_key = "YOUR_API_KEY"

#     # Example for sending a POST request
#     request_client = BizyAirRequestClient(api_url, workflow_api, api_key)
#     try:
#         response_data = request_client.send_request()
#         print(f"Response Data: {response_data}")
#     except Exception as e:
#         print(e)

#     # Example for SSE client using with statement
#     try:
#         with BizyAirStreamClient(api_url, workflow_api, api_key) as stream_client:
#             for event_data in stream_client.events():
#                 print(f"Event Data: {event_data}")
#     except Exception as e:
#         print(e)
