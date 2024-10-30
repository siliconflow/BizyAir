# ComfyUI/comfy_extras/nodes_model_advanced.py
from bizyair import BizyAirBaseNode, BizyAirNodeIO, data_types


class ModelSamplingSD3(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "shift": (
                    "FLOAT",
                    {"default": 3.0, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "patch"

    CATEGORY = "advanced/model"
