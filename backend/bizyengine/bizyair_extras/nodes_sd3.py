# sd3.5
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, data_types
from bizyengine.core.path_utils import path_manager as folder_paths


class TripleCLIPLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip_name1": (folder_paths.get_filename_list("clip"),),
                "clip_name2": (folder_paths.get_filename_list("clip"),),
                "clip_name3": (folder_paths.get_filename_list("clip"),),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    # FUNCTION = "load_clip"

    CATEGORY = "advanced/loaders"


class ControlNetApplySD3(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "control_net": (data_types.CONTROL_NET,),
                "vae": (data_types.VAE,),
                "image": ("IMAGE",),
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

    CATEGORY = "conditioning/controlnet"
    # DEPRECATED = True
    NODE_DISPLAY_NAME = "Apply Controlnet with VAE"
    RETURN_TYPES = (data_types.CONDITIONING, data_types.CONDITIONING)
    RETURN_NAMES = ("positive", "negative")
