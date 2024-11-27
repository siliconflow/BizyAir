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
                "rotate_pitch": ("FLOAT", {"default": 0, "min": -20, "max": 20, "step": 0.5, "display": display, "tooltip": "looking up or down"}),
                "rotate_yaw": ("FLOAT", {"default": 0, "min": -20, "max": 20, "step": 0.5, "display": display, "tooltip": "looking left or right"}),
                "rotate_roll": ("FLOAT", {"default": 0, "min": -20, "max": 20, "step": 0.5, "display": display, "tooltip": "tilting head"}),

                "blink": ("FLOAT", {"default": 0, "min": -20, "max": 5, "step": 0.5, "display": display}),
                "eyebrow": ("FLOAT", {"default": 0, "min": -10, "max": 15, "step": 0.5, "display": display, "tooltip": "move eyebrow up or down"}),
                "wink": ("FLOAT", {"default": 0, "min": 0, "max": 25, "step": 0.5, "display": display, "tooltip": "left eye wink"}),
                "pupil_x": ("FLOAT", {"default": 0, "min": -15, "max": 15, "step": 0.5, "display": display, "tooltip": "shift pupil without moving eyes"}),
                "pupil_y": ("FLOAT", {"default": 0, "min": -15, "max": 15, "step": 0.5, "display": display, "tooltip": "shift pupil without moving eyes"}),
                "aaa": ("FLOAT", {"default": 0, "min": -30, "max": 120, "step": 1, "display": display, "tooltip": "张嘴"}),
                "eee": ("FLOAT", {"default": 0, "min": -20, "max": 15, "step": 0.2, "display": display, "tooltip": "咧嘴"}),
                "woo": ("FLOAT", {"default": 0, "min": -20, "max": 15, "step": 0.2, "display": display, "tooltip": "嘟嘴"}),
                "smile": ("FLOAT", {"default": 0, "min": -0.3, "max": 1.3, "step": 0.01, "display": display}),

                "src_ratio": ("FLOAT", {"default": 1, "min": 0, "max": 1, "step": 0.01, "display": display}),
                "sample_ratio": ("FLOAT", {"default": 1, "min": -0.2, "max": 1.2, "step": 0.01, "display": display}),
                "sample_parts": (["OnlyExpression", "OnlyRotation", "OnlyMouth", "OnlyEyes", "All"], {"tooltip": "which part of the sample image is applied to source image"}),
                "crop_factor": ("FLOAT", {"default": 1.7, "min": 1.5, "max": 2.5, "step": 0.1, "tooltip": "a multiplier to the size of cropped space from face detection"}),

                "src_image": ("IMAGE",),
            },

            "optional": {
                "sample_image": ("IMAGE", {"tooltip": "an optional image to apply to source image"}),
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
