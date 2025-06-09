import json
import time
import warnings

import requests

try:
    from comfy_api_nodes.apinode_utils import (
        download_url_to_video_output,
        tensor_to_base64_string,
    )
except ModuleNotFoundError as e:
    download_url_to_video_output = None
    tensor_to_base64_string = None

    ERROR_MSG = f"Error {e} ComfyUI API nodes module not found. Please ensure you have ComfyUI version 0.3.36 or later installed."

    warnings.warn(ERROR_MSG)

from ..core import pop_api_key_and_prompt_id
from ..core.common import client
from ..core.common.env_var import BIZYAIR_DEBUG
from ..core.nodes_base import BizyAirBaseNode
from ..core.path_utils import compose_model_name


class WanApiNodeBase:
    MODEL_ENDPOINTS = {
        "Wan-AI/Wan2.1-I2V-14B-480P-Diffusers": "https://bizyair-api.siliconflow.cn/x/v1/supernode/faas-wan-i2v-14b-480p-server"
    }


class Wan_LoraLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_name": (
                    [
                        "to choose",
                    ],
                ),
                "model_version_id": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
            },
            "optional": {
                "lora_weight": (
                    "FLOAT",
                    {
                        "default": 1,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.05,
                        "tooltip": "LoRA权重强度",
                    },
                ),
            },
        }

    RETURN_TYPES = ("LORA_CONFIG",)
    RETURN_NAMES = ("lora_config",)
    FUNCTION = "apply_lora"
    CATEGORY = "Diffusers/WAN Video Generation"

    @classmethod
    def VALIDATE_INPUTS(cls, lora_name, model_version_id):
        if lora_name == "to choose":
            return False
        if model_version_id is not None and model_version_id != "":
            return True
        return True

    def apply_lora(self, lora_name, lora_weight=0.75, model_version_id="", **kwargs):
        lora_name = compose_model_name(model_version_id, fallback_name=lora_name)
        return ([(lora_name, lora_weight)],)


class Wan_ImageToVideoPipeline(WanApiNodeBase, BizyAirBaseNode):

    POLLING_INTERVAL = 10  # sec
    MAX_POLLING_TIME = 60 * 20  # sec

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": (
                    "IMAGE",
                    {
                        "default": None,
                        "tooltip": "Optional reference image to guide video generation",
                    },
                ),
                "model_id": (["Wan-AI/Wan2.1-I2V-14B-480P-Diffusers"],),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Text description of the video",
                    },
                ),
            },
            "optional": {
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Negative text prompt to guide what to avoid in the video",
                    },
                ),
                "steps": ("INT", {"default": 30, "min": 1, "max": 40}),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 6.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFF,
                        "step": 1,
                        "display": "number",
                        "control_after_generate": True,
                        "tooltip": "Seed for video generation (0 for random)",
                    },
                ),
                "use_teacache": (["enable", "disable"],),
                "lora_config": ("LORA_CONFIG", {}),
            },
        }

    RETURN_TYPES = ("VIDEO",)

    FUNCTION = "generate_video"
    CATEGORY = "Diffusers/WAN Video Generation"

    def _encode_image(self, image_tensor):
        # https://docs.comfy.org/custom-nodes/backend/snippets
        tensor_to_base64_string(image_tensor=image_tensor, mime_type="image/webp")
        base64_str = "data:image/webp;base64," + tensor_to_base64_string(
            image_tensor=image_tensor, mime_type="image/webp"
        )
        return base64_str

    def _prepare_headers(self, api_key):
        headers = client._headers(api_key=api_key)
        headers["X-Fn-Task-Mode"] = "non-blocking"
        return headers

    def _send_initial_request(self, endpoint, request_data, **kwargs):
        headers = self._prepare_headers(api_key=kwargs["api_key"])
        payload = {"prompt": request_data}
        if "prompt_id" in kwargs:
            payload["prompt_id"] = kwargs["prompt_id"]
        response = client.send_request(
            url=endpoint,
            data=json.dumps(payload).encode(),
            headers=headers,
        )
        return response["query_url"]

    def _poll_for_completion(self, query_url, **kwargs):
        start_time = time.time()
        headers = self._prepare_headers(api_key=kwargs["api_key"])

        while time.time() - start_time < self.MAX_POLLING_TIME:
            response = requests.get(query_url, headers=headers)
            try:
                response_data = response.json()
                if response_data["data_status"] == "COMPLETED":
                    return response_data
                time.sleep(self.POLLING_INTERVAL)
            except (json.JSONDecodeError, KeyError) as e:
                if BIZYAIR_DEBUG:
                    print(
                        f"Response parsing error: {e} | Raw response: {response.text}"
                    )
                time.sleep(self.POLLING_INTERVAL)

        raise TimeoutError("Task processing timeout")

    def _process_result(self, result_data):
        video_url = result_data["data"]["payload"]
        return (download_url_to_video_output(video_url),)

    def generate_video(
        self,
        model_id: str,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 0,
        image=None,
        lora_config=[],
        use_teacache="enable",
        **kwargs,
    ):
        if download_url_to_video_output is None or tensor_to_base64_string is None:
            raise ImportError(ERROR_MSG)

        req_dict = {}
        req_dict["guidance_scale"] = kwargs.pop("cfg", 6.0)
        req_dict["num_inference_steps"] = kwargs.pop("steps", 30)
        req_dict["prompt"] = prompt
        req_dict["negative_prompt"] = negative_prompt
        req_dict["seed"] = seed
        if lora_config:
            if len(lora_config) > 1:
                raise NotImplementedError(f"TODO, tmp only support one lora")
            req_dict["lora_name_list"] = [x[0] for x in lora_config]
            req_dict["lora_weight_list"] = [x[1] for x in lora_config]
        else:
            req_dict["lora_name_list"] = []
            req_dict["lora_weight_list"] = []

        if use_teacache == "enable":
            req_dict["teacache"] = 0.3
        else:
            req_dict["teacache"] = 0

        extra_data = pop_api_key_and_prompt_id(kwargs)
        req_dict["image"] = self._encode_image(image_tensor=image)
        endpoint = self.MODEL_ENDPOINTS[model_id]
        query_url = self._send_initial_request(
            endpoint, request_data=req_dict, **extra_data
        )
        result = self._poll_for_completion(query_url, **extra_data)
        return self._process_result(result)
