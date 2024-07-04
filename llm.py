import json
import os

from .utils import get_llm_response


class SiliconCloudLLMAPI:

    display_name_to_id = {
        "Yi1.5 9B": "01-ai/Yi-1.5-9B-Chat-16K",
        "DeepSeekV2 Chat": "deepseek-ai/DeepSeek-V2-Chat",
        "(Free)GLM4 9B Chat": "THUDM/glm-4-9b-chat",
        "Qwen2 72B Instruct": "Qwen/Qwen2-72B-Instruct",
        "Qwen2 7B Instruct": "Qwen/Qwen2-7B-Instruct",
    }

    @classmethod
    def INPUT_TYPES(s):
        models = list(s.display_name_to_id.keys())
        return {
            "required": {
                "model": (models, {"default": "(Free)GLM4 9B Chat"}),
                "system_prompt": (
                    "STRING",
                    {
                        "default": "You are a helpful assistant",
                        "multiline": True,
                        "dynamicPrompts": True,
                    },
                ),
                "user_prompt": (
                    "STRING",
                    {
                        "default": "为我生成适用于 SDXL 模型的提示词，用于画一只可爱的小猫，在户外",
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

    CATEGORY = "ComfyAir"

    def get_llm_model_response(
        self, model, system_prompt, user_prompt, max_tokens, temperature
    ):
        response = get_llm_response(
            self.display_name_to_id[model],
            system_prompt,
            user_prompt,
            max_tokens,
            temperature,
        )
        ret = json.loads(response.text)
        text = ret["choices"][0]["message"]["content"]
        return (text,)


class ShowText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"text": ("STRING", {"forceInput": True}),},
            "hidden": {"unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO",},
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = "ComfyAir"

    def notify(self, text, unique_id=None, extra_pnginfo=None):
        if unique_id and extra_pnginfo and "workflow" in extra_pnginfo[0]:
            workflow = extra_pnginfo[0]["workflow"]
            node = next(
                (x for x in workflow["nodes"] if str(x["id"]) == unique_id[0]), None
            )
            if node:
                node["widgets_values"] = [text]
        return {"ui": {"text": text}, "result": (text,)}


NODE_CLASS_MAPPINGS = {
    "ComfyAirSiliconCloudLLMAPI": SiliconCloudLLMAPI,
    "ComfyAirShowText": ShowText,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyAirSiliconCloudLLMAPI": "ComfyAir SiliconCloud LLM API",
    "ComfyAirShowText": "ComfyAir Show Text",
}
