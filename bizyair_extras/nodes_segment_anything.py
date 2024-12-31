import os
from pathlib import Path
from urllib.parse import urlparse

import comfy.model_management
import folder_paths
import groundingdino.datasets.transforms as T
import numpy as np
import torch

from bizyair import BizyAirBaseNode

sam_model_list = {
    "sam_vit_h (2.56GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    },
    "sam_vit_l (1.25GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    },
    "sam_vit_b (375MB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    },
    "sam_hq_vit_h (2.57GB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth"
    },
    "sam_hq_vit_l (1.25GB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_l.pth"
    },
    "sam_hq_vit_b (379MB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_b.pth"
    },
    "mobile_sam(39MB)": {
        "model_url": "https://github.com/ChaoningZhang/MobileSAM/blob/master/weights/mobile_sam.pt"
    },
}

groundingdino_model_dir_name = "grounding-dino"
groundingdino_model_list = {
    "GroundingDINO_SwinT_OGC (694MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinT_OGC.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth",
    },
    "GroundingDINO_SwinB (938MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinB.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swinb_cogcoor.pth",
    },
}


def list_sam_model():
    return list(sam_model_list.keys())


def list_groundingdino_model():
    return list(groundingdino_model_list.keys())


class BizyAir_SAMModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list_sam_model(),),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = ("SAM_PREDICTOR",)
    NODE_DISPLAY_NAME = "☁️BizyAir Load SAM Model"


class BizyAir_GroundingDinoModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list_groundingdino_model(),),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = ("GROUNDING_DINO_MODEL",)
    NODE_DISPLAY_NAME = "☁️BizyAir Load GroundingDino Model"


class BizyAir_VITMatteModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        method_list = [
            "VITMatte",
            "VITMatte(local)",
        ]
        return {
            "required": {
                "detail_method": (method_list,),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = (
        "VitMatte_MODEL",
        "VitMatte_predictor",
    )
    NODE_DISPLAY_NAME = "☁️BizyAir Load VITMatte Model"


class BizyAir_GroundingDinoSAMSegment(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "grounding_dino_model": ("GROUNDING_DINO_MODEL", {}),
                "sam_predictor": ("SAM_PREDICTOR", {}),
                "image": ("IMAGE", {}),
                "prompt": ("STRING", {}),
                "box_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "text_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = ("IMAGE", "MASK")
    NODE_DISPLAY_NAME = "☁️BizyAir GroundingDinoSAMSegment"


class BizyAir_TrimapGenerate(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "detail_erode": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "detail_dilate": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("trimap",)
    NODE_DISPLAY_NAME = "☁️BizyAir Trimap Generate"


class BizyAir_VITMattePredict(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
                "trimap": ("MASK",),
                "vitmatte_model": ("VitMatte_MODEL", {}),
                "vitmatte_predictor": ("VitMatte_predictor", {}),
                "black_point": (
                    "FLOAT",
                    {
                        "default": 0.15,
                        "min": 0.01,
                        "max": 0.98,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "white_point": (
                    "FLOAT",
                    {
                        "default": 0.99,
                        "min": 0.02,
                        "max": 0.99,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "max_megapixels": (
                    "FLOAT",
                    {"default": 2.0, "min": 1, "max": 999, "step": 0.1},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    # FUNCTION = "main"
    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    NODE_DISPLAY_NAME = "☁️BizyAir VITMatte Predict"
