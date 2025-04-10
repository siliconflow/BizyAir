from bizyengine.core import BizyAirBaseNode, data_types
from bizyengine.core.path_utils import path_manager as folder_paths


class InstantIDModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instantid_file": (folder_paths.get_filename_list("instantid"),)
                # "instantid_file": (
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

    RETURN_TYPES = (data_types.INSTANTID,)
    FUNCTION = "default_function"
    CATEGORY = "InstantID"
    NODE_DISPLAY_NAME = "Load InstantID Model"


class ApplyInstantID(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instantid": (data_types.INSTANTID,),
                "insightface": (data_types.FACEANALYSIS,),
                "control_net": (data_types.CONTROL_NET,),
                "image": ("IMAGE",),
                "model": (data_types.MODEL,),
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "weight": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 5.0,
                        "step": 0.01,
                    },
                ),
                "start_at": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.001,
                    },
                ),
                "end_at": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.001,
                    },
                ),
            },
            "optional": {
                "image_kps": ("IMAGE",),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = (
        data_types.MODEL,
        data_types.CONDITIONING,
        data_types.CONDITIONING,
    )
    RETURN_NAMES = (
        "MODEL",
        "positive",
        "negative",
    )
    # FUNCTION = "apply_instantid" use default_function
    CATEGORY = "InstantID"
    NODE_DISPLAY_NAME = "Apply InstantID"


class ApplyInstantIDAdvanced(ApplyInstantID):
    NODE_DISPLAY_NAME = "Apply InstantID Adavanced"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instantid": (data_types.INSTANTID,),
                "insightface": (data_types.FACEANALYSIS,),
                "control_net": (data_types.CONTROL_NET,),
                "image": ("IMAGE",),
                "model": (data_types.MODEL,),
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "ip_weight": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 3.0,
                        "step": 0.01,
                    },
                ),
                "cn_strength": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.01,
                    },
                ),
                "start_at": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.001,
                    },
                ),
                "end_at": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.001,
                    },
                ),
                "noise": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                    },
                ),
                "combine_embeds": (
                    ["average", "norm average", "concat"],
                    {"default": "average"},
                ),
            },
            "optional": {
                "image_kps": ("IMAGE",),
                "mask": ("MASK",),
            },
        }


class InstantIDFaceAnalysis(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "provider": (["CUDA"],),
            },
        }

    RETURN_TYPES = (data_types.FACEANALYSIS,)
    # FUNCTION = "load_insight_face"
    CATEGORY = "InstantID"
    NODE_DISPLAY_NAME = "InstantID Face Analysis"
