import base64
import json
import pickle
import zlib


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
