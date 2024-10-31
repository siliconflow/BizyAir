import hashlib
import json
import os
import uuid
from enum import Enum

import folder_paths
import node_helpers
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import (
    decode_base64_to_np,
    decode_data,
    encode_data,
    encode_image_to_base64,
)
from nodes import LoadImage

from .utils import (
    decode_and_deserialize,
    get_api_key,
    send_post_request,
    serialize_and_encode,
)


class RemoveBackground:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/removebg"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "remove_background"

    CATEGORY = "☁️BizyAir"

    def remove_background(self, image):
        API_KEY = get_api_key()
        device = image.device
        _, h, w, _ = image.shape
        assert (
            w <= 1536 and h <= 1536
        ), f"width and height must be less than 1536, but got {w} and {h}"

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
        input_image, compress = serialize_and_encode(image, compress=True)
        payload["image"] = input_image
        payload["is_compress"] = compress

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        tensors = decode_and_deserialize(response)
        t_images = tensors["images"].to(device)
        t_mask = tensors["mask"].to(device)
        return (t_images, t_mask)


class GenerateLightningImage:
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
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    CATEGORY = "☁️BizyAir"

    def generate_image(self, prompt, seed, width, height, cfg, batch_size):
        API_KEY = get_api_key()
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


<<<<<<< HEAD
class BizyAirSegmentAnythingText:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"
=======
class AuraSR:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/aurasr"
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
<<<<<<< HEAD
                "prompt": ("STRING", {}),
                "box_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "text_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "text_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def text_sam(self, image, prompt, box_threshold, text_threshold):
=======
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "super_resolution"

    CATEGORY = "☁️BizyAir/Super Resolution"

    def super_resolution(self, image):
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

<<<<<<< HEAD
        payload = {
            "image": None,
            "mode": 1,  # 文本分割模式
            "params": {
                "prompt": prompt,
                "box_threshold": box_threshold,
                "text_threshold": text_threshold,
            },
=======
        # support RGB mode only now
        image = image[:, :, :, :3]

        payload = {
            "is_compress": True,
            "image": None,
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
<<<<<<< HEAD
        image = image.squeeze(0).numpy()
        image_pil = Image.fromarray((image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image
=======
        input_image = encode_data(image, disable_image_marker=True)
        payload["image"] = input_image
        payload["is_compress"] = True
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f

        ret: str = send_post_request(self.API_URL, payload=payload, headers=headers)
        ret = json.loads(ret)

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        if ret["status"] == "error":
            raise Exception(ret["message"])

        msg = ret["data"]
<<<<<<< HEAD
        if msg["type"] not in ("bizyair",):
            raise Exception(f"Unexpected response type: {msg}")

        if "error" in msg:
            raise Exception(f"Error happens: {msg}")

        img = msg["image"]
        mask_image = msg["mask_image"]

        img = (
            (torch.from_numpy(decode_base64_to_np(img)).float() / 255.0)
            .unsqueeze(0)
            .to(device)
        )
        img_mask = (
            torch.from_numpy(decode_base64_to_np(mask_image)).float() / 255.0
        ).to(device)
        img_mask = img_mask.mean(dim=-1)
        img_mask = img_mask.unsqueeze(0)
        return (img, img_mask)
=======
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        image_b64 = msg["data"]["payload"]

        image = decode_data(image_b64)
        image = image.to(device)
        return (image,)
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f


NODE_CLASS_MAPPINGS = {
    "BizyAirRemoveBackground": RemoveBackground,
    "BizyAirGenerateLightningImage": GenerateLightningImage,
<<<<<<< HEAD
    "BizyAirSegmentAnythingText": BizyAirSegmentAnythingText,
=======
    "BizyAirAuraSR": AuraSR,
>>>>>>> 33dd52814ef85fb7f16b090657af466a86434d3f
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirRemoveBackground": "☁️BizyAir Remove Image Background",
    "BizyAirGenerateLightningImage": "☁️BizyAir Generate Photorealistic Images",
}
