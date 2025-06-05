import asyncio
import json

import aiohttp
from aiohttp import web
from bizyengine.core import BizyAirMiscBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.image_utils import decode_data, encode_comfy_image, encode_data
from server import PromptServer

from .utils import (
    decode_and_deserialize,
    get_llm_response,
    get_vlm_response,
    send_post_request,
    serialize_and_encode,
)


class SiliconCloudLLMAPI(BizyAirMiscBaseNode):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        default_system_prompt = """你是一个 stable diffusion prompt 专家，为我生成适用于 Stable Diffusion 模型的prompt。 我给你相关的单词，你帮我扩写为适合 Stable Diffusion 文生图的 prompt。要求： 1. 英文输出 2. 除了 prompt 外，不要输出任何其它的信息 """
        return {
            "required": {
                "model": ((), {}),
                "system_prompt": (
                    "STRING",
                    {
                        "default": default_system_prompt,
                        "multiline": True,
                        "dynamicPrompts": True,
                    },
                ),
                "user_prompt": (
                    "STRING",
                    {
                        "default": "小猫，梵高风格",
                        "multiline": True,
                        "dynamicPrompts": True,
                    },
                ),
                "max_tokens": ("INT", {"default": 512, "min": 100, "max": 1e5}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_llm_model_response"
    OUTPUT_NODE = False
    CATEGORY = "☁️BizyAir/AI Assistants"

    def get_llm_model_response(
        self, model, system_prompt, user_prompt, max_tokens, temperature, **kwargs
    ):
        if model == "No LLM Enhancement":
            return {"ui": {"text": (user_prompt,)}, "result": (user_prompt,)}
        ret = get_llm_response(
            model, system_prompt, user_prompt, max_tokens, temperature, **kwargs
        )
        text = ret["choices"][0]["message"]["content"]
        return (text,)  # if update ui:  {"ui": {"text": (text,)}, "result": (text,)}


class SiliconCloudVLMAPI(BizyAirMiscBaseNode):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ((), {}),
                "system_prompt": (
                    "STRING",
                    {
                        "default": "你是一个能分析图像的AI助手。请仔细观察图像，并根据用户的问题提供详细、准确的描述。",
                        "multiline": True,
                    },
                ),
                "user_prompt": (
                    "STRING",
                    {
                        "default": "请描述这张图片的内容，并指出任何有趣或不寻常的细节。",
                        "multiline": True,
                    },
                ),
                "images": ("IMAGE",),
                "max_tokens": ("INT", {"default": 512, "min": 100, "max": 1e5}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01},
                ),
                "detail": (["auto", "low", "high"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_vlm_model_response"
    OUTPUT_NODE = False
    CATEGORY = "☁️BizyAir/AI Assistants"

    def get_vlm_model_response(
        self,
        model,
        system_prompt,
        user_prompt,
        images,
        max_tokens,
        temperature,
        detail,
        **kwargs,
    ):
        if model == "No VLM Enhancement":
            return (user_prompt,)

        # 使用 encode_comfy_image 函数编码图像批次
        encoded_images_json = encode_comfy_image(
            images, image_format="WEBP", lossless=True
        )
        encoded_images_dict = json.loads(encoded_images_json)

        # 提取所有编码后的图像
        base64_images = list(encoded_images_dict.values())

        ret = get_vlm_response(
            model,
            system_prompt,
            user_prompt,
            base64_images,
            max_tokens,
            temperature,
            detail,
            **kwargs,
        )
        text = ret["choices"][0]["message"]["content"]
        return (text,)


class BizyAirJoyCaption(BizyAirMiscBaseNode):
    # refer to: https://huggingface.co/spaces/fancyfeast/joy-caption-pre-alpha
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/joycaption2"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "do_sample": (["enable", "disable"],),
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "round": 0.001,
                        "display": "number",
                    },
                ),
                "max_tokens": (
                    "INT",
                    {
                        "default": 256,
                        "min": 16,
                        "max": 512,
                        "step": 16,
                        "display": "number",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "joycaption"

    CATEGORY = "☁️BizyAir/AI Assistants"

    def joycaption(self, image, do_sample, temperature, max_tokens, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        SIZE_LIMIT = 1536
        # device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        payload = {
            "image": None,
            "do_sample": do_sample == "enable",
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "caption_type": "Descriptive",
            "caption_length": "any",
            "extra_options": [],
            "name_input": "",
            "custom_prompt": "A descriptive caption for this image:\n",
        }
        input_image = encode_data(image, disable_image_marker=True)
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
            if ret["type"] == "error":
                raise Exception(ret["message"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        msg = ret["data"]
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        caption = msg["data"]
        return (caption,)


class BizyAirJoyCaption2(BizyAirMiscBaseNode):
    def __init__(self):
        pass

    # refer to: https://huggingface.co/spaces/fancyfeast/joy-caption-pre-alpha
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/joycaption2"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "do_sample": ([True, False],),
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "round": 0.001,
                        "display": "number",
                    },
                ),
                "max_tokens": (
                    "INT",
                    {
                        "default": 256,
                        "min": 16,
                        "max": 512,
                        "step": 16,
                        "display": "number",
                    },
                ),
                "caption_type": (
                    [
                        "Descriptive",
                        "Descriptive (Informal)",
                        "Training Prompt",
                        "MidJourney",
                        "Booru tag list",
                        "Booru-like tag list",
                        "Art Critic",
                        "Product Listing",
                        "Social Media Post",
                    ],
                ),
                "caption_length": (
                    ["any", "very short", "short", "medium-length", "long", "very long"]
                    + [str(i) for i in range(20, 261, 10)],
                ),
                "extra_options": (
                    "STRING",
                    {
                        "default": "If there is a person/character in the image you must refer to them as {name}.",
                        "tooltip": "Extra options for the model",
                        "multiline": True,
                    },
                ),
                "name_input": (
                    "STRING",
                    {
                        "default": "Jack",
                        "tooltip": "Name input is only used if an Extra Option is selected that requires it.",
                    },
                ),
                "custom_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "joycaption2"

    CATEGORY = "☁️BizyAir/AI Assistants"

    def resize_if_large(self, image, max_size=2048):
        import torch.nn.functional as F

        _, h, w, _ = image.shape

        if h <= max_size and w <= max_size:
            return image

        if h > w:
            new_h = max_size
            new_w = int(w * (max_size / h))
        else:
            new_w = max_size
            new_h = int(h * (max_size / w))

        image = image.permute(0, 3, 1, 2)
        resized_image = F.interpolate(
            image, size=(new_h, new_w), mode="bilinear", align_corners=False
        )
        resized_image = resized_image.permute(0, 2, 3, 1)

        return resized_image

    def joycaption2(
        self,
        image,
        do_sample,
        temperature,
        max_tokens,
        caption_type,
        caption_length,
        extra_options,
        name_input,
        custom_prompt,
        **kwargs,
    ):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        image = self.resize_if_large(image)

        payload = {
            "image": None,
            "do_sample": do_sample == True,
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "caption_type": caption_type,
            "caption_length": caption_length,
            "extra_options": [extra_options],
            "name_input": name_input,
            "custom_prompt": custom_prompt,
        }
        input_image = encode_data(image, disable_image_marker=True)
        payload["image"] = input_image
        if "prompt_id" in extra_data:
            payload["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(payload).encode("utf-8")

        ret: str = client.send_request(
            url=self.API_URL, data=data, headers=headers, callback=None
        )

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
            if ret["type"] == "error":
                raise Exception(ret["message"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        msg = ret["data"]
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        caption = msg["data"]
        return (caption,)


class BizyAirJoyCaption3(BizyAirJoyCaption2):
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/joycaption3"


NODE_CLASS_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": SiliconCloudLLMAPI,
    "BizyAirSiliconCloudVLMAPI": SiliconCloudVLMAPI,
    "BizyAirJoyCaption": BizyAirJoyCaption,
    "BizyAirJoyCaption2": BizyAirJoyCaption2,
    "BizyAirJoyCaption3": BizyAirJoyCaption3,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": "☁️BizyAir SiliconCloud LLM API",
    "BizyAirSiliconCloudVLMAPI": "☁️BizyAir SiliconCloud VLM API",
    "BizyAirJoyCaption": "☁️BizyAir Joy Caption",
    "BizyAirJoyCaption2": "☁️BizyAir Joy Caption2",
    "BizyAirJoyCaption3": "☁️BizyAir Joy Caption3",
}
