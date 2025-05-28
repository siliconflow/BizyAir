import json
import logging
import os
import pprint
import urllib.error
import urllib.request
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Union

import aiohttp
import comfy

from .caching import CacheManager

__all__ = ["send_request"]

from dataclasses import dataclass, field

from .env_var import (
    BIZYAIR_API_KEY,
    BIZYAIR_DEBUG,
    BIZYAIR_SERVER_ADDRESS,
    BIZYAIR_SERVER_MODE,
    create_api_key_file,
)

version_path = os.path.join(os.path.dirname(__file__), "..", "..", "version.txt")
with open(version_path, "r") as file:
    CLIENT_VERSION = file.read().strip()


@dataclass
class APIKeyState:
    current_api_key: str = field(default=None)
    is_valid: bool = field(default=False)


# Actual api key in use
api_key_state = APIKeyState()


def set_api_key(api_key: str = "YOUR_API_KEY", override: bool = False) -> bool:
    if BIZYAIR_SERVER_MODE:
        return
    logging.debug("client.py set_api_key called")
    global api_key_state
    if api_key_state.is_valid and not override:
        warnings.warn("API key has already been set and will not be overridden.")
        return True
    if validate_api_key(api_key):
        create_api_key_file(api_key)
        api_key_state.is_valid = True
        api_key_state.current_api_key = api_key
        logging.info("\033[92mAPI key is set successfully.\033[0m")
        return True
    else:
        warnings.warn("Invalid API key provided.")
        return False


def validate_api_key(api_key: str = None) -> bool:
    if BIZYAIR_SERVER_MODE:
        return False

    logging.debug("validating api key...")
    if not api_key or not isinstance(api_key, str):
        warnings.warn("invalid api_key")
        return False

    is_valid = False
    # if api_key_state.current_api_key == api_key and api_key_state.is_valid is not None:
    #     return api_key_state.is_valid
    url = f"{BIZYAIR_SERVER_ADDRESS}/user/info"
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
    try:
        response_data = send_request(
            method="GET", url=url, headers=headers, callback=None
        )
        if "message" not in response_data or response_data["message"] != "Ok":
            raise ValueError(
                f"\033[91mAPI key validation failed. API Key: {api_key}\033[0m"
            )
        else:
            is_valid = True
    except ConnectionError as ce:
        raise ValueError(f"\033[91mConnection error: {ce}\033[0m")
    except PermissionError as pe:
        raise ValueError(
            f"\033[91mError validating API key: {api_key}, error: {pe}\033[0m"
        )
    except Exception as e:
        raise ValueError(f"\033[91mOther error: {e}\033[0m")

    logging.debug(f"api key validated: {is_valid}")
    return is_valid


def get_api_key() -> str:
    if BIZYAIR_SERVER_MODE:
        return None
    logging.debug("client.py get_api_key called")
    global api_key_state
    try:
        if not api_key_state.is_valid:
            if validate_api_key(BIZYAIR_API_KEY):
                api_key_state.is_valid = True
                api_key_state.current_api_key = BIZYAIR_API_KEY
                logging.info("API key set successfully")
    except Exception as e:
        logging.error(str(e))
        raise ValueError(str(e))
    return api_key_state.current_api_key


def headers(api_key: str = None):
    return _headers(api_key=api_key)


def _headers(api_key: str = None):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key if api_key else get_api_key()}",
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
    cache_manager: CacheManager = None,
    **kwargs,
) -> Union[dict, Any]:
    try:
        headers = kwargs.pop("headers") if "headers" in kwargs else _headers()
        headers["User-Agent"] = "BizyAir Client"
        headers["x-bizyair-client-version"] = CLIENT_VERSION

        req = urllib.request.Request(
            url, data=data, headers=headers, method=method, **kwargs
        )
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        error_message = str(e)
        response_body = e.read().decode("utf-8") if hasattr(e, "read") else "N/A"
        if verbose:
            logging.error(f"URLError encountered: {error_message}")
            logging.info(f"Response Body: {response_data}")
        code, message = "N/A", "N/A"
        try:
            response_dict = json.loads(response_body)
            if isinstance(response_dict, dict):
                code = response_dict.get("code", "N/A")
                message = response_dict.get("message", "N/A")

        except json.JSONDecodeError:
            if verbose:
                logging.error("Failed to decode response body as JSON.")

        if "Unauthorized" in error_message:
            raise PermissionError(
                "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
                "If you have the key, please click the 'API Key' button at the bottom right to set the key."
            )
        elif code != "N/A" and message != "N/A":
            if code in [20049, 20050]:
                raise ConnectionError(
                    f"""Failed to handle your request:

    {message}"""
                )
            else:
                raise ConnectionError(
                    f"""Failed to handle your request: {error_message}

    Error code: {code}
    Error message: {message}

    The cause of this issue may be incorrect parameter status or ongoing background tasks.
    If retrying after waiting for a while still does not resolve the issue,
    please report it to Bizyair's official support."""
                )
        else:
            common_sites = [
                "https://www.baidu.com",
                "https://www.bing.com",
                "https://www.alibaba.com",
            ]
            results = {}
            for site in common_sites:
                success = False
                try:

                    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                        def redirect_request(self, req, fp, code, msg, headers, newurl):
                            return None

                    opener = urllib.request.build_opener(NoRedirectHandler())
                    response = opener.open(site, timeout=5)
                    success = 200 <= response.getcode() < 400
                except urllib.error.HTTPError as e:
                    success = 200 <= e.code < 400
                except (urllib.error.URLError, TimeoutError):
                    pass
                results[site] = "Success" if success else "Failed"
            raise ConnectionError(
                f"Failed to connect to the server: {url}.\n"
                + "The connection attempts to the public sites return the following results:\n"
                + "\n".join(
                    [f"    {site}: {result}" for site, result in results.items()]
                )
                + "\nPlease check the network connection."
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
                        logging.error(f"Error encountered: {error_message}")
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
        logging.error(f"Error fetching data: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return {}


def fetch_models_by_type(
    url: str, model_type: str, *, method="GET", verbose=False
) -> dict:
    global api_key_state
    if not api_key_state.is_valid:
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
