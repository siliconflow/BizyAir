from bizyengine.core import BizyAirBaseNode


class Wan_Model_Loader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": (("Wan2.1-T2V-1.3B",),),
            }
        }

    RETURN_TYPES = ("WAN_MODEL",)
    RETURN_NAMES = ("model",)
    CATEGORY = "WanT2V"


class Wan_T2V_Pipeline(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("WAN_MODEL",),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage.",
                    },
                ),
                "resolution": (
                    ["480*832", "832*480", "624*624", "704*544", "544*704"],
                    {"default": "480*832"},
                ),
                "sampling_steps": ("INT", {"default": 50, "min": 1, "max": 50}),
                "guidance_scale": ("FLOAT", {"default": 6.0, "min": 0, "max": 20}),
                "shift_scale": ("FLOAT", {"default": 8.0, "min": 0, "max": 20}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xFFFFFFFFFFFFFFFF}),
                "negative_prompt": (
                    "STRING",
                    {"multiline": True, "default": "Low quality, blurry"},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    CATEGORY = "WanT2V"
    # FUNCTION = "generate_video"
