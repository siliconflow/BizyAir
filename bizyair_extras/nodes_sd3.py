# sd3.5
from bizyair import BizyAirBaseNode, BizyAirNodeIO, data_types
from bizyair.path_utils import path_manager as folder_paths


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
