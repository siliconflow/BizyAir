import base64
import json
import os
import pickle
import zlib

import requests

COMFYAIR_DEBUG = os.getenv("COMFYAIR_DEBUG", False)


def send_post_request(api_url, payload, headers):
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
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to the server: {e}")

    return response


def serialize_and_encode(obj, compress=True):
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

    if COMFYAIR_DEBUG:
        print(
            f"serialize_and_encode: size of bytes is {format_bytes(len(serialized_obj))}"
        )

    encoded_obj = base64.b64encode(serialized_obj).decode("utf-8")

    if COMFYAIR_DEBUG:
        print(
            f"serialize_and_encode: size of base64 text is {format_bytes(len(serialized_obj))}"
        )

    return (encoded_obj, compress)


def decode_and_deserialize(response_text):
    if COMFYAIR_DEBUG:
        print(
            f"decode_and_deserialize: size of text is {format_bytes(len(response_text))}"
        )

    ret = json.loads(response_text)

    if "result" in ret:
        msg = json.loads(ret["result"])
    else:
        msg = ret
    if (
        msg["type"] != "comfyair"
    ):  # DO NOT CHANGE THIS LINE: "comfyair" is the type from the server node
        # TODO: change both server and client "comfyair" to "bizyair"
        raise Exception(f"Unexpected response type: {msg}")

    data = msg["data"]

    tensor_bytes = base64.b64decode(data["payload"])
    if data["is_compress"]:
        tensor_bytes = zlib.decompress(tensor_bytes)

    if COMFYAIR_DEBUG:
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


def validate_api_key(key: str):
    assert isinstance(key, str), f"API_KEY must be a string, got {type(key)}"
    assert key.startswith(
        "sk"
    ), f"invalid key, please refer to https://cloud.siliconflow.cn to get your API_KEY, got {key}"


def get_api_key():
    from .auth import API_KEY

    validate_api_key(API_KEY)
    return API_KEY


def get_llm_response(
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
):
    api_url = "https://api.siliconflow.cn/v1/chat/completions"
    API_KEY = get_api_key()
    validate_api_key(API_KEY)
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

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
    response = send_post_request(api_url, headers=headers, payload=payload)
    return response
