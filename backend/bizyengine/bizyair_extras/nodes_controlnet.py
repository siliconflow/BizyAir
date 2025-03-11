from bizyengine.core import BizyAirBaseNode, data_types
from comfy.cldm.control_types import UNION_CONTROLNET_TYPES


class SetUnionControlNetType(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net": (data_types.CONTROL_NET,),
                "type": (["auto"] + list(UNION_CONTROLNET_TYPES.keys()),),
            }
        }

    CATEGORY = "conditioning/controlnet"
    RETURN_TYPES = (data_types.CONTROL_NET,)

    # FUNCTION = "set_controlnet_type"


class ControlNetInpaintingAliMamaApply(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "control_net": (data_types.CONTROL_NET,),
                "vae": (data_types.VAE,),
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "start_percent": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_percent": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
            }
        }

    # FUNCTION = "apply_inpaint_controlnet"
    CATEGORY = "conditioning/controlnet"
    RETURN_TYPES = (data_types.CONDITIONING, data_types.CONDITIONING)
    RETURN_NAMES = ("positive", "negative")
