"""ComfyUI Advanced Redux Control
Reference: https://github.com/kaibioinfo/ComfyUI_AdvancedRefluxControl
"""

from bizyengine.core import BizyAirBaseNode, data_types
from bizyengine.core.path_utils import path_manager as folder_paths

STRENGTHS = ["highest", "high", "medium", "low", "lowest"]
STRENGTHS_VALUES = [1, 2, 3, 4, 5]
IMAGE_MODES = ["center crop (square)", "keep aspect ratio", "autocrop with mask"]


class StyleModelApplySimple(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "style_model": (data_types.STYLE_MODEL,),
                "clip_vision_output": ("CLIP_VISION_OUTPUT",),
                "image_strength": (STRENGTHS, {"default": "medium"}),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    CATEGORY = "conditioning/style_model"
    NODE_DISPLAY_NAME = "Apply style model (simple)"


class ReduxAdvanced(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "style_model": (data_types.STYLE_MODEL,),
                "clip_vision": ("CLIP_VISION",),
                "image": ("IMAGE",),
                "downsampling_factor": ("INT", {"default": 3, "min": 1, "max": 9}),
                "downsampling_function": (
                    ["nearest", "bilinear", "bicubic", "area", "nearest-exact"],
                    {"default": "area"},
                ),
                "mode": (IMAGE_MODES, {"default": "center crop (square)"}),
                "weight": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
            "optional": {
                "mask": ("MASK",),
                "autocrop_margin": (
                    "FLOAT",
                    {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = (data_types.CONDITIONING, "IMAGE", "MASK")
    # FUNCTION = "apply_stylemodel"
    NODE_DISPLAY_NAME = "Apply Redux model (advanced)"
    CATEGORY = "conditioning/style_model"
