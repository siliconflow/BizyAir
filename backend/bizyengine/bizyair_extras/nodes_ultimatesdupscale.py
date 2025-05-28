from enum import Enum

import comfy
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO
from bizyengine.core.data_types import CONDITIONING, MODEL, UPSCALE_MODEL, VAE


class USDUMode(Enum):
    LINEAR = 0
    CHESS = 1
    NONE = 2


class USDUSFMode(Enum):
    NONE = 0
    BAND_PASS = 1
    HALF_TILE = 2
    HALF_TILE_PLUS_INTERSECTIONS = 3


MAX_RESOLUTION = 8192
# The modes available for Ultimate SD Upscale
MODES = {
    "Linear": USDUMode.LINEAR,
    "Chess": USDUMode.CHESS,
    "None": USDUMode.NONE,
}
# The seam fix modes
SEAM_FIX_MODES = {
    "None": USDUSFMode.NONE,
    "Band Pass": USDUSFMode.BAND_PASS,
    "Half Tile": USDUSFMode.HALF_TILE,
    "Half Tile + Intersections": USDUSFMode.HALF_TILE_PLUS_INTERSECTIONS,
}


def USDU_base_inputs():
    required = [
        ("image", ("IMAGE",)),
        # Sampling Params
        ("model", (MODEL,)),
        ("positive", (CONDITIONING,)),
        ("negative", (CONDITIONING,)),
        ("vae", (VAE,)),
        ("upscale_by", ("FLOAT", {"default": 2, "min": 0.05, "max": 4, "step": 0.05})),
        ("seed", ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF})),
        ("steps", ("INT", {"default": 20, "min": 1, "max": 10000, "step": 1})),
        ("cfg", ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0})),
        ("sampler_name", (comfy.samplers.KSampler.SAMPLERS,)),
        ("scheduler", (comfy.samplers.KSampler.SCHEDULERS,)),
        ("denoise", ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01})),
        # Upscale Params
        ("upscale_model", (UPSCALE_MODEL,)),
        ("mode_type", (list(MODES.keys()),)),
        (
            "tile_width",
            ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
        ),
        (
            "tile_height",
            ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 8}),
        ),
        ("mask_blur", ("INT", {"default": 8, "min": 0, "max": 64, "step": 1})),
        (
            "tile_padding",
            ("INT", {"default": 32, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
        ),
        # Seam fix params
        ("seam_fix_mode", (list(SEAM_FIX_MODES.keys()),)),
        (
            "seam_fix_denoise",
            ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
        ),
        (
            "seam_fix_width",
            ("INT", {"default": 64, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
        ),
        ("seam_fix_mask_blur", ("INT", {"default": 8, "min": 0, "max": 64, "step": 1})),
        (
            "seam_fix_padding",
            ("INT", {"default": 16, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
        ),
        # Misc
        ("force_uniform_tiles", ("BOOLEAN", {"default": True})),
        ("tiled_decode", ("BOOLEAN", {"default": False})),
    ]

    optional = []

    return required, optional


def prepare_inputs(required: list, optional: list = None):
    inputs = {}
    if required:
        inputs["required"] = {}
        for name, type in required:
            inputs["required"][name] = type
    if optional:
        inputs["optional"] = {}
        for name, type in optional:
            inputs["optional"][name] = type
    return inputs


def remove_input(inputs: list, input_name: str):
    for i, (n, _) in enumerate(inputs):
        if n == input_name:
            del inputs[i]
            break


def rename_input(inputs: list, old_name: str, new_name: str):
    for i, (n, t) in enumerate(inputs):
        if n == old_name:
            inputs[i] = (new_name, t)
            break


class UltimateSDUpscale(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        required, optional = USDU_base_inputs()
        return prepare_inputs(required, optional)

    RETURN_TYPES = ("IMAGE",)
    # FUNCTION = "upscale"
    CATEGORY = "image/upscaling"

    def upscale(self, **kwargs):
        model: BizyAirNodeIO = kwargs.get("model")
        new_model = model.copy(self.assigned_id)
        new_model.add_node_data(
            class_type="UltimateSDUpscale",
            inputs=kwargs,
        )
        return new_model.send_request()
