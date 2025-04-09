from bizyengine.core import BizyAirBaseNode, data_types
from bizyengine.core.path_utils import path_manager as folder_paths

# PuLID Flux datatypes
PULIDFLUX = "BIZYAIR_PULIDFLUX"
EVA_CLIP = "BIZYAIR_EVA_CLIP"
FACEANALYSIS = "BIZYAIR_FACEANALYSIS"


class PulidFluxModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"pulid_file": (folder_paths.get_filename_list("pulid"),)}}
        # return {
        #     "required": {
        #         "pulid_file": (
        #             [
        #                 "to choose",
        #             ],
        #         ),
        #         "model_version_id": (
        #             "STRING",
        #             {
        #                 "default": "",
        #             },
        #         ),
        #     }
        # }

    RETURN_TYPES = (PULIDFLUX,)
    RETURN_NAMES = ("pulid_flux",)
    # FUNCTION = "load_model"
    CATEGORY = "pulid"
    NODE_DISPLAY_NAME = "Load PuLID Flux Model"


class PulidFluxInsightFaceLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "provider": (
                    [
                        "CUDA",
                    ],
                ),
            },
        }

    RETURN_TYPES = (FACEANALYSIS,)
    RETURN_NAMES = ("face_analysis",)
    # FUNCTION = "load_insightface"
    CATEGORY = "pulid"
    NODE_DISPLAY_NAME = "Load InsightFace (PuLID Flux)"


class PulidFluxEvaClipLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
        }

    RETURN_TYPES = (EVA_CLIP,)
    RETURN_NAMES = ("eva_clip",)
    # FUNCTION = "load_eva_clip"
    CATEGORY = "pulid"
    NODE_DISPLAY_NAME = "Load Eva Clip (PuLID Flux)"


class ApplyPulidFlux(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "pulid_flux": (PULIDFLUX,),
                "eva_clip": (EVA_CLIP,),
                "face_analysis": (FACEANALYSIS,),
                "image": ("IMAGE",),
                "weight": (
                    "FLOAT",
                    {"default": 1.0, "min": -1.0, "max": 5.0, "step": 0.05},
                ),
                "start_at": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_at": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
            },
            "optional": {
                "attn_mask": ("MASK",),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "apply_pulid_flux"
    CATEGORY = "pulid"
    NODE_DISPLAY_NAME = "Apply PuLID Flux"
