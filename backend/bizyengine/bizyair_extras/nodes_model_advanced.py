# ComfyUI/comfy_extras/nodes_model_advanced.py
import nodes
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, data_types


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


class ModelSamplingFlux(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "max_shift": (
                    "FLOAT",
                    {"default": 1.15, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "base_shift": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "width": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "patch"
    CATEGORY = "advanced/model"
