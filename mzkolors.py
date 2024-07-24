import os
import uuid

import torch

from .utils import (
    decode_and_deserialize,
    send_post_request,
    serialize_and_encode,
    get_api_key,
)


CATEGORY_NAME = "☁️BizyAir/Kolors"

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


class BizyAirMZChatGLM3TextEncode:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/mzkolorschatglm3"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)

    FUNCTION = "encode"
    CATEGORY = CATEGORY_NAME

    def encode(self, text):
        API_KEY = get_api_key()
        assert len(text) <= 4096, f"the prompt is too long, length: {len(text)}"

        payload = {
            "text": text,
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

        ret_conditioning = []
        for item in tensors_np:
            t, d = item
            t_tensor = torch.from_numpy(t)
            d_dict = {}
            for k, v in d.items():
                d_dict[k] = torch.from_numpy(v)
            ret_conditioning.append([t_tensor, d_dict])

        return (ret_conditioning,)


NODE_CLASS_MAPPINGS = {
    "BizyAirMZChatGLM3TextEncode": BizyAirMZChatGLM3TextEncode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirMZChatGLM3TextEncode": "☁️BizyAir ChatGLM3 Text Encode",
}
