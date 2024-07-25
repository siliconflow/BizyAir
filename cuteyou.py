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

#本地调试
BIZYAIR_SERVER_ADDRESS = "http://127.0.0.1:8000"


MAX_RESOLUTION=16384

class CuteYou:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/cuteyou"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0, "max": 1.0, "step": 0.01 }),
                "width": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                "height": ("INT", {"default": 512, "min": 16, "max": MAX_RESOLUTION, "step": 8}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 35}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    CATEGORY = "☁️BizyAir"

    def generate_image(self, image, seed, denoise, width, height, steps, batch_size):
        API_KEY = get_api_key()
        print("why-----generate_image in supernode.py")
        print(type(image))
        print(image.shape)
        input_image, compress = serialize_and_encode(image, compress=True)

        
        payload = {
            "denoise": denoise,
            "image": input_image,
            "width": width,
            "height": height,
            "steps": steps,
            "seed": seed,
            "batch_size": batch_size,
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