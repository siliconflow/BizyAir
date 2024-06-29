import base64
import json
import os
import pickle
import zlib
import time

import requests

COMFY_AIR_SERVER_ADDRESS = os.getenv(
    "COMFY_AIR_SERVER_ADDRESS", "http://127.0.0.1:8000"
)


class SuperResolution:
    API_URL = f"{COMFY_AIR_SERVER_ADDRESS}/supernode/superresolution"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),
                "scale": (["2x", "4x"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "super_resolution"

    CATEGORY = "ComfyAir"

    def super_resolution(self, image, scale="2x", API_KEY=""):
        _, w, h, _ = image.shape
        assert (
            w <= 512 and h <= 512
        ), f"width and height must be less than 512, but got {w} and {h}"

        payload = {
            "scale": scale,
            "is_compress": True,
            "image": None,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image = pickle.dumps(image)
        input_image = zlib.compress(input_image)
        input_image = base64.b64encode(input_image).decode("utf-8")
        payload["image"] = input_image

        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to the server: {e}")

        data = json.loads(response.text)["data"]
        tensor_bytes = base64.b64decode(data["payload"])
        if data["is_compress"]:
            tensor_bytes = zlib.decompress(tensor_bytes)
        image = pickle.loads(tensor_bytes)

        return (image,)


class RemoveBackground:
    API_URL = f"{COMFY_AIR_SERVER_ADDRESS}/supernode/removebg"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "remove_background"

    CATEGORY = "ComfyAir"

    def remove_background(self, image, API_KEY=""):
        _, w, h, _ = image.shape
        assert (
            w <= 1024 and h <= 1024
        ), f"width and height must be less than 1024, but got {w} and {h}"

        payload = {
            "is_compress": True,
            "image": None,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image = pickle.dumps(image)
        input_image = zlib.compress(input_image)
        input_image = base64.b64encode(input_image).decode("utf-8")
        payload["image"] = input_image

        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to the server: {e}")

        data = json.loads(response.text)["data"]
        tensor_bytes = base64.b64decode(data["payload"])
        if data["is_compress"]:
            tensor_bytes = zlib.decompress(tensor_bytes)
        tensors = pickle.loads(tensor_bytes)

        return (tensors["images"], tensors["mask"])


NODE_CLASS_MAPPINGS = {
    "ComfyAirSuperResolution": SuperResolution,
    "ComfyAirRemoveBackground": RemoveBackground,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyAirSuperResolution": "ComfyAir Super Resolution",
    "ComfyAirRemoveBackground": "ComfyAir Remove Background",
}
