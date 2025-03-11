from bizyengine.core import BizyAirBaseNode


class JanusModelLoader(BizyAirBaseNode):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_name": (
                    ["deepseek-ai/Janus-Pro-7B"],
                ),  # "deepseek-ai/Janus-Pro-1B",
            },
        }

    RETURN_TYPES = ("BIZYAIR_JANUS_MODEL", "BIZYAIR_JANUS_PROCESSOR")
    RETURN_NAMES = ("model", "processor")
    # FUNCTION = "load_model"
    CATEGORY = "Janus-Pro"


class JanusImageUnderstanding(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("BIZYAIR_JANUS_MODEL",),
                "processor": ("BIZYAIR_JANUS_PROCESSOR",),
                "image": ("IMAGE",),
                "question": (
                    "STRING",
                    {"multiline": True, "default": "Describe this image in detail."},
                ),
                "seed": (
                    "INT",
                    {"default": 666666666666666, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
                "temperature": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0}),
                "max_new_tokens": ("INT", {"default": 512, "min": 1, "max": 2048}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    # FUNCTION = "analyze_image"
    CATEGORY = "Janus-Pro"


class JanusImageGeneration(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("BIZYAIR_JANUS_MODEL",),
                "processor": ("BIZYAIR_JANUS_PROCESSOR",),
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": "A beautiful photo of"},
                ),
                "seed": (
                    "INT",
                    {"default": 666666666666666, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
                "batch_size": ("INT", {"default": 4, "min": 4, "max": 9}),
                "cfg_weight": (
                    "FLOAT",
                    {"default": 5.0, "min": 1.0, "max": 10.0, "step": 0.5},
                ),
                "temperature": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1},
                ),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    # FUNCTION = "generate_images"
    CATEGORY = "Janus-Pro"
