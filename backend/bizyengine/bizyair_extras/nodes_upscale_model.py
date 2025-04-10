import bizyengine.core.path_utils as folder_paths
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO
from bizyengine.core.data_types import UPSCALE_MODEL


class UpscaleModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_name": (folder_paths.get_filename_list("upscale_models"),),
                # "model_name": (
                #     [
                #         "to choose",
                #     ],
                # ),
                # "model_version_id": (
                #     "STRING",
                #     {
                #         "default": "",
                #     },
                # ),
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
