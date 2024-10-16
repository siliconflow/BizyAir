import asyncio
import json

import aiohttp
from aiohttp import web
from server import PromptServer

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import decode_data, encode_data

from .utils import (
    decode_and_deserialize,
    get_api_key,
    get_llm_response,
    send_post_request,
    serialize_and_encode,
)


@PromptServer.instance.routes.post("/bizyair/get_silicon_cloud_models")
async def get_silicon_cloud_models_endpoint(request):
    data = await request.json()
    api_key = data.get("api_key", get_api_key())
    url = "https://api.siliconflow.cn/v1/models"
    headers = {"accept": "application/json", "authorization": f"Bearer {api_key}"}
    params = {"type": "text", "sub_type": "chat"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, params=params, timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["id"] for model in data["data"]]
                    models.append("No LLM Enhancement")
                    return web.json_response(models)
                else:
                    print(f"Error fetching models: HTTP Status {response.status}")
                    return web.json_response(
                        ["Error fetching models"], status=response.status
                    )
    except aiohttp.ClientError as e:
        print(f"Error fetching models: {e}")
        return web.json_response(["Error fetching models"], status=500)
    except asyncio.exceptions.TimeoutError:
        print("Request to fetch models timed out")
        return web.json_response(["Request timed out"], status=504)


class SiliconCloudLLMAPI:
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
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_llm_model_response"
    OUTPUT_NODE = False

    CATEGORY = "☁️BizyAir/AI Assistants"

    def get_llm_model_response(
        self, model, system_prompt, user_prompt, max_tokens, temperature
    ):
        if model == "No LLM Enhancement":
            return {"ui": {"text": (user_prompt,)}, "result": (user_prompt,)}
        response = get_llm_response(
            model,
            system_prompt,
            user_prompt,
            max_tokens,
            temperature,
        )
        ret = json.loads(response)
        text = ret["choices"][0]["message"]["content"]
        return {"ui": {"text": (text,)}, "result": (text,)}


class BizyAirJoyCaption:
    # refer to: https://huggingface.co/spaces/fancyfeast/joy-caption-pre-alpha
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/joycaption"

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
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "joycaption"

    CATEGORY = "☁️BizyAir/AI Assistants"

    def joycaption(self, image, do_sample, temperature, max_tokens):
        API_KEY = get_api_key()
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
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image = encode_data(image, disable_image_marker=True)
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

        caption = msg["data"]
        return {"ui": {"text": (caption,)}, "result": (caption,)}


NODE_CLASS_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": SiliconCloudLLMAPI,
    "BizyAirJoyCaption": BizyAirJoyCaption,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": "☁️BizyAir SiliconCloud LLM API",
    "BizyAirJoyCaption": "☁️BizyAir Joy Caption",
}
