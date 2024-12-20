import bizyair.path_utils as folder_paths
from bizyair import BizyAirBaseNode, BizyAirNodeIO
from bizyair.data_types import UPSCALE_MODEL


class UpscaleModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_name": (folder_paths.get_filename_list("upscale_models"),),
            }
        }

    RETURN_TYPES = (UPSCALE_MODEL,)
    # FUNCTION = "load_model"
    CATEGORY = "loaders"


class ImageUpscaleWithModel(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "upscale_model": (UPSCALE_MODEL,),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    # FUNCTION = "upscale"
    CATEGORY = "image/upscaling"
