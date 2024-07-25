import os

import numpy as np
import torch


from .utils import (
    decode_and_deserialize,
    send_post_request,
    serialize_and_encode,
    get_api_key,
)

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)

MAX_RESOLUTION = 1536


class CuteYou:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/cuteyou"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "width": (
                    "INT",
                    {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8},
                ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 35}),
                "cfg": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 100.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    CATEGORY = "☁️BizyAir"

    def generate_image(self, image, seed, denoise, width, height, steps, cfg):
        API_KEY = get_api_key()
        input_image, compress = serialize_and_encode(image, compress=True)

        payload = {
            "denoise": denoise,
            "image": input_image,
            "width": width,
            "height": height,
            "steps": steps,
            "seed": seed,
            "cfg": cfg,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )

        tensors_np = decode_and_deserialize(response)
        tensors = torch.from_numpy(tensors_np)

        return (tensors,)


NODE_CLASS_MAPPINGS = {
    "BizyAirCuteYou": CuteYou,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirCuteYou": "☁️BizyAir Cute Your Images",
}
