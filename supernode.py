import json
import os
import uuid

import torch
import numpy as np
from PIL import Image
from bizyair.image_utils import decode_data, encode_data, encode_image_to_base64,decode_base64_to_np

from .utils import (
    decode_and_deserialize,
    get_api_key,
    send_post_request,
    serialize_and_encode,
)

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


class SuperResolution:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/superresolution"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "scale": (["2x", "4x"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "super_resolution"

    CATEGORY = "☁️BizyAir/Super Resolution"

    def super_resolution(self, image, scale="2x"):
        API_KEY = get_api_key()
        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= 512 and h <= 512
        ), f"width and height must be less than 512, but got {w} and {h}"

        # support RGB mode only now
        image = image[:, :, :, :3]

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
        input_image, compress = serialize_and_encode(image, compress=True)
        payload["image"] = input_image
        payload["is_compress"] = compress

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        image = decode_and_deserialize(response)
        image = image.to(device)
        return (image,)


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


class AuraSR:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/aurasr"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "super_resolution"

    CATEGORY = "☁️BizyAir/Super Resolution"

    def super_resolution(self, image):
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        # support RGB mode only now
        image = image[:, :, :, :3]

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
        input_image = encode_data(image, disable_image_marker=True)
        payload["image"] = input_image
        payload["is_compress"] = True

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
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        image_b64 = msg["data"]["payload"]

        image = decode_data(image_b64)
        image = image.to(device)
        return (image,)

class BizyAirSegmentAnything:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    # RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "auto_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def auto_sam(self, image):
        print("why image.shape:", image.shape)
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        # device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        payload = {
            "image": None, 
            "input_points": None,
            "input_label": None,
            "input_boxes": None,
            "prompt": None,
            "threshold": 0.3,             #置信度
            "mode": 0           #自动分割模式
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        image = image.squeeze(0).numpy()
        image_pil = Image.fromarray((image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image

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
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        img = msg["image"]
        
        img = (torch.from_numpy(decode_base64_to_np(img)).float()/255.0).unsqueeze(0)

        return (img,)

NODE_CLASS_MAPPINGS = {
    "BizyAirSuperResolution": SuperResolution,
    "BizyAirRemoveBackground": RemoveBackground,
    "BizyAirGenerateLightningImage": GenerateLightningImage,
    "BizyAirAuraSR": AuraSR,
    "BizyAirSegmentAnything": BizyAirSegmentAnything,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirAuraSR": "☁️BizyAir Photorealistic Image Super Resolution",
    "BizyAirSuperResolution": "☁️BizyAir Anime Image Super Resolution",
    "BizyAirRemoveBackground": "☁️BizyAir Remove Image Background",
    "BizyAirGenerateLightningImage": "☁️BizyAir Generate Photorealistic Images",
    "BizyAirSegmentAnything": "☁️BizyAir Auto SegmentAnything",
}
