import os
import uuid

import torch
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, create_node_data
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.data_types import CONDITIONING
from bizyengine.core.image_utils import encode_data

from .utils import (
    decode_and_deserialize,
    get_api_key,
    send_post_request,
    serialize_and_encode,
)

CATEGORY_NAME = "☁️BizyAir/Kolors"


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


class BizyAir_MinusZoneChatGLM3TextEncode(BizyAirMZChatGLM3TextEncode, BizyAirBaseNode):
    RETURN_TYPES = (CONDITIONING,)

    FUNCTION = "mz_encode"

    def mz_encode(self, text):
        out = self.encode(text)[0]
        node_data = create_node_data(
            class_type="ComfyAirLoadData",
            inputs={"conditioning": {"relay": out}},
            outputs={"slot_index": 3},
        )
        node_data["is_changed"] = uuid.uuid4().hex
        return (
            BizyAirNodeIO(
                self.assigned_id,
                nodes={self.assigned_id: encode_data(node_data, old_version=True)},
            ),
        )


NODE_CLASS_MAPPINGS = {
    "BizyAir_MinusZoneChatGLM3TextEncode": BizyAir_MinusZoneChatGLM3TextEncode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAir_MinusZoneChatGLM3TextEncode": "☁️BizyAir MinusZone ChatGLM3 Text Encode",
}
