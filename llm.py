import json
import os

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import decode_data, encode_data

from .utils import (
    decode_and_deserialize,
    get_api_key,
    get_llm_response,
    send_post_request,
    serialize_and_encode,
)


class SiliconCloudLLMAPI:

    display_name_to_id = {
        "Yi1.5 9B": "01-ai/Yi-1.5-9B-Chat-16K",
        "DeepSeekV2 Chat": "deepseek-ai/DeepSeek-V2-Chat",
        "(Free)GLM4 9B Chat": "THUDM/glm-4-9b-chat",
        "Qwen2 72B Instruct": "Qwen/Qwen2-72B-Instruct",
        "(Free)Qwen2 7B Instruct": "Qwen/Qwen2-7B-Instruct",
        "No LLM Enhancement": "Bypass",
    }

    @classmethod
    def INPUT_TYPES(s):
        models = list(s.display_name_to_id.keys())
        default_sysmtem_prompt = """你是一个 stable diffusion prompt 专家，为我生成适用于 Stable Diffusion 模型的prompt。
我给你相关的单词，你帮我扩写为适合 Stable Diffusion 文生图的 prompt。要求：
1. 英文输出
2. 除了 prompt 外，不要输出任何其它的信息
"""
        return {
            "required": {
                "model": (models, {"default": "(Free)GLM4 9B Chat"}),
                "system_prompt": (
                    "STRING",
                    {
                        "default": default_sysmtem_prompt,
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
        if self.display_name_to_id[model] == "Bypass":
            return {"ui": {"text": (user_prompt,)}, "result": (user_prompt,)}
        response = get_llm_response(
            self.display_name_to_id[model],
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
        bs, w, h, c = image.shape
        assert (
            bs == 1 and w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"batch size must be 1, and width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got bs={bs}, w={w}, h={h}"

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


class BizyAirMultiJoyCaption(BizyAirJoyCaption):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "do_sample": (["enable", "disable"], {"default": "enable"}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "max_tokens": ("INT", {"default": 77, "min": 1, "max": 512}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "multi_joycaption"
    NODE_DISPLAY_NAME = "☁️BizyAir Multi Joy Caption"

    def multi_joycaption(self, images, do_sample, temperature, max_tokens):
        captions = []
        steps = len(images)
        pbar = comfy.utils.ProgressBar(steps)
        for i, image in enumerate(images):
            result = super().joycaption(
                image.unsqueeze(0), do_sample, temperature, max_tokens
            )
            captions.append(result["result"][0])
            pbar.update_absolute(i + 1)
        combined_caption = " | ".join(captions)
        return {"ui": {"text": (combined_caption,)}, "result": (combined_caption,)}


class SaveCaptionsAndImages:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "captions": ("STRING", {"multiline": True}),
                "images": ("IMAGE",),
                "directory_prefix": (
                    "STRING",
                    {"default": "lora_dataset", "multiline": False},
                ),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "apply"

    def apply(self, captions, images, directory_prefix):

        # Split the captions string into a list using " | " as the delimiter
        caption_list = captions.split(" | ")
        full_output_folder = folder_paths.get_output_directory()
        # Find the next available directory number
        i = 0
        while True:
            dir_path = os.path.join(full_output_folder, f"{directory_prefix}_{i:03d}")
            if not os.path.exists(dir_path):
                break
            i += 1
        # Validate input
        if len(caption_list) != len(images):
            raise ValueError(
                "The number of captions does not match the number of images."
            )

        for batch_number, (image, caption) in enumerate(zip(images, caption_list)):
            # Generate a unique filename for each image
            filename = f"image_{batch_number:04d}"

            # Generate file paths
            image_filepath = os.path.join(dir_path, f"{filename}.png")
            caption_filepath = os.path.join(dir_path, f"{filename}.txt")

            # Ensure directory exists
            os.makedirs(dir_path, exist_ok=True)

            # Save the image
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img.save(image_filepath)

            # Write caption to file
            with open(caption_filepath, "w", encoding="utf-8") as caption_file:
                caption_file.write(caption)

            print(f"Image saved to: {image_filepath}")
            print(f"Caption saved to: {caption_filepath}")

        return {}


NODE_CLASS_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": SiliconCloudLLMAPI,
    "BizyAirJoyCaption": BizyAirJoyCaption,
    "BizyAirMultiJoyCaption": BizyAirMultiJoyCaption,
    "SaveCaptionsAndImages": SaveCaptionsAndImages,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": "☁️BizyAir SiliconCloud LLM API",
    "BizyAirJoyCaption": "☁️BizyAir Joy Caption",
    "BizyAirMultiJoyCaption": "☁️BizyAir Multi Joy Caption",
    "SaveCaptionsAndImages": "Save Captions And Images",
}
