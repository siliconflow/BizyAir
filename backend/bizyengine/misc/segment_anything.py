import hashlib
import json
import os
from enum import Enum

import folder_paths
import numpy as np
import torch
from bizyengine.core import BizyAirMiscBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.image_utils import decode_base64_to_np, encode_image_to_base64
from nodes import LoadImage
from PIL import Image, ImageOps, ImageSequence

from .route_sam import SAM_COORDINATE


class INFER_MODE(Enum):
    auto = 0
    text = 1
    points_box = 2
    batched_boxes = 3


class EDIT_MODE(Enum):
    box = 0
    point = 1


class BizyAirSegmentAnythingText(BizyAirMiscBaseNode):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {}),
                "box_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "text_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "text_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def text_sam(self, image, prompt, box_threshold, text_threshold, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        SIZE_LIMIT = 1536
        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        payload = {
            "image": None,
            "mode": 1,  # 文本分割模式
            "params": {
                "prompt": prompt,
                "box_threshold": box_threshold,
                "text_threshold": text_threshold,
            },
        }
        image = image.squeeze(0).numpy()
        image_pil = Image.fromarray((image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image
        if "prompt_id" in extra_data:
            payload["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(payload).encode("utf-8")

        ret = client.send_request(
            url=self.API_URL,
            data=data,
            headers=headers,
            callback=None,
        )

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        if ret["status"] == "error":
            raise Exception(ret["message"])

        msg = ret["data"]
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


class BizyAirSegmentAnythingPointBox(BizyAirMiscBaseNode):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "is_point": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("processed_image", "mask", "original_image")
    FUNCTION = "apply"

    CATEGORY = "☁️BizyAir/segment-anything"

    def apply(self, image, is_point, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        SIZE_LIMIT = 1536

        # 加载原始图像
        original_image, _ = LoadImage().load_image(image)
        # 直接克隆原始图像用于处理和透传
        image_to_process = original_image.clone()

        device = image_to_process.device
        _, w, h, c = image_to_process.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"
        if is_point:
            coordinates = [
                json.loads(SAM_COORDINATE["point_coords"][key])
                for key in SAM_COORDINATE["point_coords"]
            ]

            input_points = [
                [float(coord["startx"]), float(coord["starty"])]
                for coord in coordinates
            ]

            input_label = [coord["pointType"] for coord in coordinates]
            payload = {
                "image": None,
                "mode": INFER_MODE.points_box.value,
                "params": {
                    "input_points": json.dumps(input_points),
                    "input_label": json.dumps(input_label),
                    "input_boxes": None,
                },
            }
        else:
            coordinates = [
                json.loads(SAM_COORDINATE["box_coords"][key])
                for key in SAM_COORDINATE["box_coords"]
            ]
            input_box = [
                [
                    float(coord["startx"]),
                    float(coord["starty"]),
                    float(coord["endx"]),
                    float(coord["endy"]),
                ]
                for coord in coordinates
            ]

            payload = {
                "image": None,
                "mode": INFER_MODE.batched_boxes.value,
                "params": {
                    "input_points": None,
                    "input_label": None,
                    "input_boxes": json.dumps(input_box),
                },
            }

        # 处理用于API的图像
        api_image = image_to_process.squeeze(0).numpy()
        image_pil = Image.fromarray((api_image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image
        if "prompt_id" in extra_data:
            payload["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(payload).encode("utf-8")

        ret = client.send_request(
            url=self.API_URL, data=data, headers=headers, callback=None
        )

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        if ret["status"] == "error":
            if "data" in ret:
                if "error" in ret["data"]:
                    raise Exception(ret["data"]["error"])
            raise Exception(ret["message"])

        msg = ret["data"]
        if msg["type"] not in ("bizyair",):
            raise Exception(f"Unexpected response type: {msg}")

        if "error" in msg:
            raise Exception(f"Error happens: {msg}")

        img = msg["image"]
        mask_image = msg["mask_image"]

        processed_img = (
            (torch.from_numpy(decode_base64_to_np(img)).float() / 255.0)
            .unsqueeze(0)
            .to(device)
        )
        img_mask = (
            torch.from_numpy(decode_base64_to_np(mask_image)).float() / 255.0
        ).to(device)
        img_mask = img_mask.mean(dim=-1)
        img_mask = img_mask.unsqueeze(0)

        # 直接返回克隆的原始图像,无需转换
        return (processed_img, img_mask, image_to_process)

    @classmethod
    def IS_CHANGED(s, image, is_point):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image, is_point):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


NODE_CLASS_MAPPINGS = {
    "BizyAirSegmentAnythingText": BizyAirSegmentAnythingText,
    "BizyAirSegmentAnythingPointBox": BizyAirSegmentAnythingPointBox,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSegmentAnythingText": "☁️BizyAir Text Guided SAM",
    "BizyAirSegmentAnythingPointBox": "☁️BizyAir Point-Box Guided SAM",
}
