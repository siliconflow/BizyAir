import base64
import json
import pickle
import zlib

import requests


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


def decode_and_deserialize(response_text):
    ret = json.loads(response_text)

    if "result" in ret:
        msg = json.loads(ret["result"])
    else:
        msg = ret

    if msg["type"] != "comfyair":
        raise Exception(f"Unexpected response type: {msg}")

    data = msg["data"]

    tensor_bytes = base64.b64decode(data["payload"])
    if data["is_compress"]:
        tensor_bytes = zlib.decompress(tensor_bytes)
    deserialized_object = pickle.loads(tensor_bytes)
    return deserialized_object
