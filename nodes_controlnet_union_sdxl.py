""" 
huggingface: https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
github: https://github.com/xinsir6/ControlNetPlus/tree/main
"""
import numpy as np
import numpy as np
import requests
import torch
from .image_utils import encode_comfy_image, decode_comfy_image
from .diffusers_server_client import DiffusersServerClient


class DiffusersKSampler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
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
                # "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                # "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                # "positive": ("CONDITIONING", ),
                # "negative": ("CONDITIONING", ),
                "latent_image": ("LATENT",),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "☁️BizyAir/sampling"

    def sample(self, *args, **kwargs):
        return


class ControlNetPlusNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "openpose_image": ("IMAGE",),
                "depth_image": ("IMAGE",),
                "hed_pidi_scribble_ted_image": ("IMAGE",),
                "canny_lineart_anime_lineart_mlsd_image": ("IMAGE",),
                "normal_image": ("IMAGE",),
                "segment_image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"

    CATEGORY = "☁️BizyAir/ControlNetPlus"

    def __init__(self):
        create_task_url = "http://0.0.0.0:8000/supernode/diffusers/v1/controlnetplus"
        get_result_url = "http://localhost:8000/supernode/diffusers/results/{task_id}"
        self.create_task_url = create_task_url
        self.get_result_url = get_result_url

    def process(
        self,
        openpose_image=None,
        depth_image=None,
        hed_pidi_scribble_ted_image=None,
        canny_lineart_anime_lineart_mlsd_image=None,
        normal_image=None,
        segment_image=None,
    ):
        height, width = openpose_image.shape[1:3]
        ratio = np.sqrt(1024.0 * 1024.0 / (width * height))
        new_width, new_height = int(width * ratio), int(height * ratio)
        print(f"{new_height=}x{new_width=}")
        controlnet_img = {
            0: openpose_image,
            1: depth_image,
            2: hed_pidi_scribble_ted_image,
            3: canny_lineart_anime_lineart_mlsd_image,
            4: normal_image,
            5: segment_image,
        }

        # 0 -- openpose
        # 1 -- depth
        # 2 -- hed/pidi/scribble/ted
        # 3 -- canny/lineart/anime_lineart/mlsd
        # 4 -- normal
        # 5 -- segment
        for k, v in controlnet_img.items():
            if v is not None:
                controlnet_img[k] = encode_comfy_image(v)

        payload = {
            "seed": 1,  # Optional, can be None
            "width": new_width,
            "height": new_height,
            "num_inference_steps": 30,  # Optional, defaults to 30
            "prompt": "a girl",  # Required
            "negative_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",  # Required
            "controlnet_img": controlnet_img,
        }

        with DiffusersServerClient(self.create_task_url, self.get_result_url) as client:
            task_id = client.create_task(payload)
            if task_id is None:
                return
            print(f"Task created with ID: {task_id}")
            response_text = client.get_task_result(task_id)
            if response_text is None:
                raise RuntimeError()

            import json

            ret = json.loads(response_text)
            img_data = ret["data"]["payload"]
            output = decode_comfy_image(img_data)
        return (output,)


NODE_CLASS_MAPPINGS = {
    "ControlNetPlusNode": ControlNetPlusNode,
    "DiffusersKSampler": DiffusersKSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ControlNetPlusNode": "ControlNet Plus Node",
    "DiffusersKSampler": "Diffusers KSampler",
}
