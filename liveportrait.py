import json

import numpy as np
import torch
from PIL import Image

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import decode_base64_to_np, encode_image_to_base64

from .utils import get_api_key, send_post_request


class BizyAirLPExpressionEditor:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/liveportrait"

    # Ref: https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait/blob/3bba732915e22f18af0d221b9c5c282990181f1b/nodes.py#L840-L867
    @classmethod
    def INPUT_TYPES(s):
        display = "number"
        return {
            "required": {
                "rotate_pitch": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 20,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "抬头低头，范围：[-20, 20]",
                    },
                ),
                "rotate_yaw": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 20,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "左右转头，范围：[-20, 20]",
                    },
                ),
                "rotate_roll": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 20,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "歪头，范围：[-20, 20]",
                    },
                ),
                "blink": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 5,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "睁眼，范围：[-20, 5]",
                    },
                ),
                "eyebrow": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -10,
                        "max": 15,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "眉毛垂直位移，范围：[-10, 15]",
                    },
                ),
                "wink": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 25,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "左眼眨眼，范围：[0, 25]",
                    },
                ),
                "pupil_x": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -15,
                        "max": 15,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "瞳孔水平位移，范围：[-15, 15]",
                    },
                ),
                "pupil_y": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -15,
                        "max": 15,
                        "step": 0.5,
                        "display": display,
                        "tooltip": "瞳孔垂直位移，范围：[-15, 15]",
                    },
                ),
                "aaa": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -30,
                        "max": 120,
                        "step": 1,
                        "display": display,
                        "tooltip": "张嘴，范围：[-30, 120]",
                    },
                ),
                "eee": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 15,
                        "step": 0.2,
                        "display": display,
                        "tooltip": "咧嘴，范围：[-20, 15]",
                    },
                ),
                "woo": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 15,
                        "step": 0.2,
                        "display": display,
                        "tooltip": "嘟嘴，范围：[-20, 15]",
                    },
                ),
                "smile": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": -0.3,
                        "max": 1.3,
                        "step": 0.01,
                        "display": display,
                        "tooltip": "笑，范围：[-0.3, 1.3]",
                    },
                ),
                "src_ratio": (
                    "FLOAT",
                    {
                        "default": 1,
                        "min": 0,
                        "max": 1,
                        "step": 0.01,
                        "display": display,
                        "tooltip": "原图系数，范围：[0, 1]",
                    },
                ),
                "sample_ratio": (
                    "FLOAT",
                    {
                        "default": 1,
                        "min": -0.2,
                        "max": 1.2,
                        "step": 0.01,
                        "display": display,
                        "tooltip": "采样图系数，范围：[-0.2, 1.2]",
                    },
                ),
                "sample_parts": (
                    ["OnlyExpression", "OnlyRotation", "OnlyMouth", "OnlyEyes", "All"],
                    {"tooltip": "采样图采样部位"},
                ),
                "crop_factor": (
                    "FLOAT",
                    {
                        "default": 1.7,
                        "min": 1.5,
                        "max": 2.5,
                        "step": 0.1,
                        "tooltip": "面部捕捉裁剪区域乘数, 范围：[1.5, 2.5]",
                    },
                ),
                "src_image": (
                    "IMAGE",
                    {"tooltip": "原图（必须）"},
                ),
            },
            "optional": {
                "sample_image": (
                    "IMAGE",
                    {"tooltip": "采样图（可选）"},
                ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"

    CATEGORY = "☁️BizyAir/liveportrait"

    def run(
        self,
        rotate_pitch,
        rotate_yaw,
        rotate_roll,
        blink,
        eyebrow,
        wink,
        pupil_x,
        pupil_y,
        aaa,
        eee,
        woo,
        smile,
        src_ratio,
        sample_ratio,
        sample_parts,
        crop_factor,
        src_image,
        sample_image=None,
    ):
        API_KEY = get_api_key()
        device = src_image.device

        payload = {
            "rotate_pitch": rotate_pitch,
            "rotate_yaw": rotate_yaw,
            "rotate_roll": rotate_roll,
            "blink": blink,
            "eyebrow": eyebrow,
            "wink": wink,
            "pupil_x": pupil_x,
            "pupil_y": pupil_y,
            "aaa": aaa,
            "eee": eee,
            "woo": woo,
            "smile": smile,
            "src_ratio": src_ratio,
            "sample_ratio": sample_ratio,
            "sample_parts": sample_parts,
            "crop_factor": crop_factor,
            "src_image": None,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }

        src_image = src_image.squeeze(0).numpy()
        src_image_pil = Image.fromarray((src_image * 255).astype(np.uint8))
        src_str = encode_image_to_base64(src_image_pil, format="PNG")
        payload["src_image"] = src_str
        if sample_image != None:
            sample_image = sample_image.squeeze(0).numpy()
            sample_image_pil = Image.fromarray((sample_image * 255).astype(np.uint8))
            sample_str = encode_image_to_base64(sample_image_pil, format="PNG")
            payload["sample_image"] = sample_str

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
        img = (
            (torch.from_numpy(decode_base64_to_np(img, format="PNG")).float() / 255.0)
            .unsqueeze(0)
            .to(device)
        )

        return (img,)


NODE_CLASS_MAPPINGS = {
    "BizyAirLPExpressionEditor": BizyAirLPExpressionEditor,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirLPExpressionEditor": "☁️BizyAir LivePortrait Expression Editor",
}
