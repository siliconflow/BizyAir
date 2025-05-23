import base64
import json
import os
import pickle
import urllib.parse
import urllib.request
import zlib
from typing import List, Tuple, Union

import numpy as np
from bizyengine.core import pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)


#
# TODO: Deprecated, delete this
def send_post_request(api_url, payload, headers):
    import warnings

    warnings.warn(message=f"send_post_request is deprecated")
    """
    Sends a POST request to the specified API URL with the given payload and headers.

    Args:
        api_url (str): The URL of the API endpoint.
        payload (dict): The payload to send in the POST request.
        headers (dict): The headers to include in the POST request.

    Raises:
        Exception: If there is an error connecting to the server or the request fails.
    """
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
        return response_data
    except urllib.error.URLError as e:
        if "Unauthorized" in str(e):
            raise Exception(
                "Key is invalid, please refer to https://cloud.siliconflow.cn to get the API key.\n"
                "If you have the key, please click the 'BizyAir Key' button at the bottom right to set the key."
            )
        else:
            raise Exception(
                f"Failed to connect to the server: {e}, if you have no key, "
            )


def serialize_and_encode(obj: Union[np.ndarray], compress=True) -> Tuple[str, bool]:
    """
    Serializes a Python object, optionally compresses it, and then encodes it in base64.

    Args:
        obj: The Python object to serialize.
        compress (bool): Whether to compress the serialized object using zlib. Default is True.

    Returns:
        str: The base64 encoded string of the serialized (and optionally compressed) object.
    """
    serialized_obj = pickle.dumps(obj)

    if compress:
        serialized_obj = zlib.compress(serialized_obj)

    if BIZYAIR_DEBUG:
        print(
            f"serialize_and_encode: size of bytes is {format_bytes(len(serialized_obj))}"
        )

    encoded_obj = base64.b64encode(serialized_obj).decode("utf-8")

    if BIZYAIR_DEBUG:
        print(
            f"serialize_and_encode: size of base64 text is {format_bytes(len(serialized_obj))}"
        )

    return (encoded_obj, compress)


def decode_and_deserialize(response_text) -> np.ndarray:
    if BIZYAIR_DEBUG:
        print(
            f"decode_and_deserialize: size of text is {format_bytes(len(response_text))}"
        )

    ret = json.loads(response_text)

    if "result" in ret:
        msg = json.loads(ret["result"])
    else:
        msg = ret
    if msg["type"] not in (
        "comfyair",
        "bizyair",
    ):  # DO NOT CHANGE THIS LINE: "comfyair" is the type from the server node
        # TODO: change both server and client "comfyair" to "bizyair"
        raise Exception(f"Unexpected response type: {msg}")

    data = msg["data"]

    tensor_bytes = base64.b64decode(data["payload"])
    if data.get("is_compress", None):
        tensor_bytes = zlib.decompress(tensor_bytes)

    if BIZYAIR_DEBUG:
        print(
            f"decode_and_deserialize: size of bytes is {format_bytes(len(tensor_bytes))}"
        )

    deserialized_object = pickle.loads(tensor_bytes)
    return deserialized_object


def format_bytes(num_bytes: int) -> str:
    """
    Converts a number of bytes to a human-readable string with units (B, KB, or MB).

    :param num_bytes: The number of bytes to convert.
    :return: A string representing the number of bytes in a human-readable format.
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KB"
    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"


def get_llm_response(
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    **kwargs,
):
    api_url = f"{BIZYAIR_SERVER_ADDRESS}/chat/completions"
    extra_data = pop_api_key_and_prompt_id(kwargs)
    headers = client.headers(api_key=extra_data["api_key"])

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9,
        "top_k": 50,
        "stream": False,
        "n": 1,
    }
    if "prompt_id" in extra_data:
        payload["prompt_id"] = extra_data["prompt_id"]
    data = json.dumps(payload).encode("utf-8")

    response = client.send_request(
        url=api_url,
        data=data,
        headers=headers,
        callback=None,
    )
    return response


def get_vlm_response(
    model: str,
    system_prompt: str,
    user_prompt: str,
    base64_images: List[str],
    max_tokens: int = 1024,
    temperature: float = 0.7,
    detail: str = "auto",
    **kwargs,
):
    api_url = f"{BIZYAIR_SERVER_ADDRESS}/chat/completions"
    extra_data = pop_api_key_and_prompt_id(kwargs)
    headers = client.headers(api_key=extra_data["api_key"])

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": system_prompt}],
        },  # 此方法皆适用于两种 VL 模型
        # {
        #     "role": "system",
        #     "content": system_prompt,
        # },  # role 为 "system" 的这种方式只适用于 QwenVL 系列模型,并不适用于 InternVL 系列模型
    ]

    user_content = []
    for base64_image in base64_images:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/webp;base64,{base64_image}",
                    "detail": detail,
                },
            }
        )
    user_content.append({"type": "text", "text": user_prompt})

    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9,
        "top_k": 50,
        "stream": False,
        "n": 1,
    }
    if "prompt_id" in extra_data:
        payload["prompt_id"] = extra_data["prompt_id"]
    data = json.dumps(payload).encode("utf-8")

    response = client.send_request(
        url=api_url,
        headers=headers,
        data=data,
        callback=None,
    )
    return response
