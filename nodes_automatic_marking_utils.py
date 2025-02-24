import asyncio
import json
import os

import aiohttp
import comfy
import folder_paths
import numpy as np
from aiohttp import web
from PIL import Image
from server import PromptServer

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import decode_data, encode_comfy_image, encode_data

from .utils import (
    decode_and_deserialize,
    get_api_key,
    get_llm_response,
    get_vlm_response,
    send_post_request,
    serialize_and_encode,
)

API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/joycaption2"

def joycaption2(
        image,
        do_sample,
        temperature,
        max_tokens,
        caption_type,
        caption_length,
        extra_options,
        name_input,
        custom_prompt,
    ):

        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        print("why img: ", image.shape)
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

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
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image = encode_data(image, disable_image_marker=True)
        payload["image"] = input_image

        ret: str = send_post_request(API_URL, payload=payload, headers=headers)
        ret = json.loads(ret)

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