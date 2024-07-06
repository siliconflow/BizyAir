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
                    {"default": "小猫，梵高风格", "multiline": True, "dynamicPrompts": True,},
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
    OUTPUT_NODE = True

    CATEGORY = "BizyAir"

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
        ret = json.loads(response)
        text = ret["choices"][0]["message"]["content"]
        return {"ui": {"text": (text,)}, "result": (text,)}


NODE_CLASS_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": SiliconCloudLLMAPI,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSiliconCloudLLMAPI": "BizyAir SiliconCloud LLM API",
    "BizyAirShowText": "BizyAir Show Text",
}
