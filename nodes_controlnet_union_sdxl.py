""" 
huggingface: https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
github: https://github.com/xinsir6/ControlNetPlus/tree/main
"""
import json
import os
import numpy as np
import requests
from .utils import get_api_key
from .image_utils import encode_comfy_image, decode_comfy_image

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


class StableDiffusionXLControlNetUnionPipeline:
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
                "prompt": ("STRING", {"forceInput": True}),
                "negative_prompt": ("STRING", {"forceInput": True}),
                "control_guidance_start": (
                    "FLOAT",
                    {"default": 0, "min": 0.0, "max": 1, "step": 0.1,},
                ),
                "control_guidance_end": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1, "step": 0.1,},
                ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "☁️BizyAir/ControlNet"

    @staticmethod
    def get_headers():
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {get_api_key()}",
        }

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
                height, width = v.shape[1:3]
                ratio = np.sqrt(1024.0 * 1024.0 / (width * height))
                new_width, new_height = int(width * ratio), int(height * ratio)
                controlnet_img[k] = encode_comfy_image(v)

        print(
            f"Utilizing a height of {new_height} and width of {width} for processing."
        )
        payload = {
            "width": new_width,
            "height": new_height,
            "controlnet_img": controlnet_img,
        }
        payload.update(**kwargs)

        response = requests.post(
            self.API_URL, json=payload, headers=self.get_headers(),
        )

        result = response.json()
        if response.status_code != 200:
            raise RuntimeError(f"Failed to create task: {result['error']}")

        if "result" in result:  # cloud
            msg = json.loads(result["result"])
            img_data = msg["data"]["payload"]
        else:  # local
            img_data = result["data"]["payload"]

        output = decode_comfy_image(img_data)
        return (output,)


NODE_CLASS_MAPPINGS = {
    "StableDiffusionXLControlNetUnionPipeline": StableDiffusionXLControlNetUnionPipeline,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StableDiffusionXLControlNetUnionPipeline": "☁️BizyAir Controlnet Union SDXL 1.0",
}
