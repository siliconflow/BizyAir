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

from .utils import (
    decode_and_deserialize,
    get_api_key,
    send_get_request,
    send_post_request,
    serialize_and_encode,
)


class INFER_MODE(Enum):
    auto = 0
    text = 1
    points_box = 2
    batched_boxes = 3


class EDIT_MODE(Enum):
    box = 0
    point = 1


BIZYAIR_SERVER_ADDRESS = "http://127.0.0.1:8000"


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


class BizyAirSegmentAnythingText:
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
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "text_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def text_sam(self, image, prompt, box_threshold, text_threshold):
        API_KEY = get_api_key()
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


class BizyAirSegmentAnythingBox:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)

        img = node_helpers.pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ["MPO"]

        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == "I":
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if "A" in i.getbands():
                mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        return {
            "required": {"image": (sorted(files), {"image_upload": True})},
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "box_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def box_sam(self, image):
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        # 预处理img
        image, _ = self.load_image(image)

        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        json_msg = send_get_request("http://127.0.0.1:9999/api/bizyair/getsam")
        json_msg = json.loads(json_msg)
        print("why json_msg:", json_msg)
        is_box = json_msg["mode"] == EDIT_MODE.box.value
        assert is_box
        coordinates = [
            json.loads(json_msg["coords"][key]) for key in json_msg["coords"]
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
            "mode": INFER_MODE.batched_boxes.value,  # Point/Box分割模式
            "params": {
                "input_points": None,
                "input_label": None,
                "input_boxes": json.dumps(input_box),
            },
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

        coord = send_get_request("http://127.0.0.1:9999/api/bizyair/getsam")
        coord = json.loads(coord)
        return (img, img_mask)

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


class BizyAirSegmentAnythingPoint:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)

        img = node_helpers.pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ["MPO"]

        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == "I":
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if "A" in i.getbands():
                mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        return {
            "required": {"image": (sorted(files), {"image_upload": True})},
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "point_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def point_sam(self, image):
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        # 预处理load_image
        image, _ = self.load_image(image)

        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        json_msg = send_get_request("http://127.0.0.1:9999/api/bizyair/getsam")
        json_msg = json.loads(json_msg)
        is_point = json_msg["mode"] == EDIT_MODE.point.value
        assert is_point
        coordinates = [
            json.loads(json_msg["coords"][key]) for key in json_msg["coords"]
        ]
        input_points = [
            [float(coord["startx"]), float(coord["starty"])] for coord in coordinates
        ]
        input_label = [coord["pointType"] for coord in coordinates]
        payload = {
            "image": None,
            "mode": INFER_MODE.points_box.value,  # Point/Box分割模式
            "params": {
                "input_points": json.dumps(input_points),
                "input_label": json.dumps(input_label),
                "input_boxes": None,
            },
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

        coord = send_get_request("http://127.0.0.1:9999/api/bizyair/getsam")
        coord = json.loads(coord)
        print("why coord:", coord)
        return (img, img_mask)

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


NODE_CLASS_MAPPINGS = {
    "BizyAirSuperResolution": SuperResolution,
    "BizyAirRemoveBackground": RemoveBackground,
    "BizyAirGenerateLightningImage": GenerateLightningImage,
    "BizyAirAuraSR": AuraSR,
    "BizyAirSegmentAnythingText": BizyAirSegmentAnythingText,
    "BizyAirSegmentAnythingBox": BizyAirSegmentAnythingBox,
    "BizyAirSegmentAnythingPoint": BizyAirSegmentAnythingPoint,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirAuraSR": "☁️BizyAir Photorealistic Image Super Resolution",
    "BizyAirSuperResolution": "☁️BizyAir Anime Image Super Resolution",
    "BizyAirRemoveBackground": "☁️BizyAir Remove Image Background",
    "BizyAirGenerateLightningImage": "☁️BizyAir Generate Photorealistic Images",
    "BizyAirSegmentAnythingText": "☁️BizyAir Text Guided SAM",
    "BizyAirSegmentAnythingBox": "☁️BizyAir Box Guided SAM",
    "BizyAirSegmentAnythingPoint": "☁️BizyAir Point Guided SAM",
}
