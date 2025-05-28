"""
huggingface: https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
github: https://github.com/xinsir6/ControlNetPlus/tree/main
"""

import json
import os

import numpy as np
import requests
from bizyengine.core import BizyAirMiscBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.image_utils import decode_comfy_image, encode_comfy_image


class StableDiffusionXLControlNetUnionPipeline(BizyAirMiscBaseNode):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/diffusers-v1-stablediffusionxlcontrolnetunionpipeline"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "num_inference_steps": ("INT", {"default": 20, "min": 1, "max": 50}),
                "num_images_per_prompt": ("INT", {"default": 1, "min": 1, "max": 4}),
                "guidance_scale": (
                    "FLOAT",
                    {
                        "default": 5.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
            },
            "optional": {
                "openpose_image": ("IMAGE",),
                "depth_image": ("IMAGE",),
                "hed_pidi_scribble_ted_image": ("IMAGE",),
                "canny_lineart_anime_lineart_mlsd_image": ("IMAGE",),
                "normal_image": ("IMAGE",),
                "segment_image": ("IMAGE",),
                "prompt": (
                    "STRING",
                    {
                        "default": "a car",
                        "multiline": True,
                        "dynamicPrompts": True,
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "default": "watermark, text",
                        "multiline": True,
                        "dynamicPrompts": True,
                    },
                ),
                "control_guidance_start": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": 0.0,
                        "max": 1,
                        "step": 0.01,
                    },
                ),
                "control_guidance_end": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1,
                        "step": 0.01,
                    },
                ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "☁️BizyAir/ControlNet"

    def process(
        self,
        openpose_image=None,
        depth_image=None,
        hed_pidi_scribble_ted_image=None,
        canny_lineart_anime_lineart_mlsd_image=None,
        normal_image=None,
        segment_image=None,
        **kwargs,
    ):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        controlnet_img = {
            0: openpose_image,
            1: depth_image,
            2: hed_pidi_scribble_ted_image,
            3: canny_lineart_anime_lineart_mlsd_image,
            4: normal_image,
            5: segment_image,
        }

        for k, v in controlnet_img.items():
            if v is not None:
                # need to resize the image resolution to 1024 * 1024 or same bucket resolution to get the best performance
                # https://github.com/xinsir6/ControlNetPlus/blob/ba6c35b62e9df4c8f3b6429c4844ecc92685c8ec/controlnet_union_test_depth.py#L54-L56
                height, width = v.shape[1:3]
                ratio = np.sqrt(1024.0 * 1024.0 / (width * height))
                new_width, new_height = int(width * ratio), int(height * ratio)
                controlnet_img[k] = encode_comfy_image(v, old_version=True)

        if new_width > 1536 or new_height > 1536:
            error_message = (
                f"Error: Adjusted image dimensions exceed the limit. "
                f"Height: {new_height}, Width: {new_width}. "
                f"Please resize the original image with dimensions "
                f"Height: {height}, Width: {width} to ensure "
                f"Adjusted image dimensions are within 1536 pixels. "
                f"Recommended dimensions: Height: {1024}, Width: {1024}."
            )
            raise RuntimeError(error_message)

        print(
            f"Utilizing a height of {new_height} and width of {new_width} for processing."
        )
        payload = {
            "width": new_width,
            "height": new_height,
            "controlnet_img": controlnet_img,
        }
        payload.update(**kwargs)

        response = requests.post(
            self.API_URL,
            json=payload,
            headers=client.headers(api_key=extra_data["api_key"]),
        )

        result = response.json()
        if response.status_code != 200:
            raise RuntimeError(f"Failed to create task: {result['error']}")

        if "result" in result:  # cloud
            msg = json.loads(result["result"])
            if "error" in msg:
                raise RuntimeError(f"{msg['error']}")
            img_data = msg["data"]["payload"]
        else:  # local
            img_data = result["data"]["payload"]

        output = decode_comfy_image(img_data, old_version=True)
        return (output,)


NODE_CLASS_MAPPINGS = {
    "StableDiffusionXLControlNetUnionPipeline": StableDiffusionXLControlNetUnionPipeline,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StableDiffusionXLControlNetUnionPipeline": "☁️BizyAir Controlnet Union SDXL 1.0",
}
