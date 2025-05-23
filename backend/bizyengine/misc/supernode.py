import hashlib
import json
import os
import uuid
from enum import Enum

import folder_paths
import node_helpers
import numpy as np
import torch
from bizyengine.core import BizyAirMiscBaseNode
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.image_utils import (
    decode_base64_to_np,
    decode_data,
    encode_data,
    encode_image_to_base64,
)
from nodes import LoadImage
from PIL import Image, ImageOps, ImageSequence

from .utils import (
    decode_and_deserialize,
    pop_api_key_and_prompt_id,
    serialize_and_encode,
)


class RemoveBackground(BizyAirMiscBaseNode):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/removebg"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "remove_background"

    CATEGORY = "☁️BizyAir"

    def remove_background(self, image, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        device = image.device
        _, h, w, _ = image.shape
        assert (
            w <= 1536 and h <= 1536
        ), f"width and height must be less than 1536, but got {w} and {h}"

        payload = {
            "is_compress": True,
            "image": None,
        }
        input_image, compress = serialize_and_encode(image, compress=True)
        payload["image"] = input_image
        payload["is_compress"] = compress
        if "prompt_id" in extra_data:
            payload["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(payload).encode("utf-8")

        tensors = client.send_request(
            url=self.API_URL,
            data=data,
            headers=headers,
            callback=None,
            response_handler=decode_and_deserialize,
        )

        t_images = tensors["images"].to(device)
        t_mask = tensors["mask"].to(device)
        return (t_images, t_mask)


class GenerateLightningImage(BizyAirMiscBaseNode):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/realvis4lightning"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {"multiline": True, "dynamicPrompts": True, "default": "a dog"},
                ),
                "seed": ("INT", {"default": 1, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "width": ("INT", {"default": 1024, "min": 16, "max": 1024, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 16, "max": 1024, "step": 8}),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 1.5,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    CATEGORY = "☁️BizyAir"

    def generate_image(self, prompt, seed, width, height, cfg, batch_size, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        assert (
            width <= 1024 and height <= 1024
        ), f"width and height must be less than 1024, but got {width} and {height}"

        payload = {
            "batch_size": batch_size,
            "width": width,
            "height": height,
            "prompt": prompt,
            "cfg": cfg,
            "seed": seed,
        }
        if "prompt_id" in extra_data:
            payload["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(payload).encode("utf-8")

        tensors_np = client.send_request(
            url=self.API_URL,
            data=data,
            headers=headers,
            callback=None,
            response_handler=decode_and_deserialize,
        )
        tensors = torch.from_numpy(tensors_np)

        return (tensors,)


NODE_CLASS_MAPPINGS = {
    "BizyAirRemoveBackground": RemoveBackground,
    "BizyAirGenerateLightningImage": GenerateLightningImage,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirRemoveBackground": "☁️BizyAir Remove Image Background",
    "BizyAirGenerateLightningImage": "☁️BizyAir Generate Photorealistic Images",
}
