"""
Reference: https://github.com/Jonseed/ComfyUI-Detail-Daemon
"""

import nodes
from bizyair import BizyAirBaseNode, data_types


class OutFluxModelSamplingPredNode(BizyAirBaseNode):
    DESCRIPTION = ""
    RETURN_TYPES = (data_types.MODEL,)
    NODE_DISPLAY_NAME = "Outverse Flux Model Pred"
    CATEGORY = "sampling/custom_sampling/samplers"

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
                "reverse_ode": ("BOOLEAN", {"default": False}),
            }
        }


class InFluxModelSamplingPredNode(BizyAirBaseNode):
    RETURN_TYPES = (data_types.MODEL,)
    CATEGORY = "sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "Inverse Flux Model Pred"

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


class FluxForwardODESamplerNode(BizyAirBaseNode):
    RETURN_TYPES = ("SAMPLER",)
    # FUNCTION = "build"
    CATEGORY = "sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "Flux Forward ODE Sampler"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "gamma": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
        }


class FluxReverseODESamplerNode(BizyAirBaseNode):
    RETURN_TYPES = ("SAMPLER",)
    # FUNCTION = "build"
    CATEGORY = "sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "Flux Reverse ODE Sampler"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "latent_image": ("LATENT",),
                "eta": (
                    "FLOAT",
                    {"default": 0.8, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "start_step": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "end_step": ("INT", {"default": 5, "min": 0, "max": 1000, "step": 1}),
            },
            "optional": {
                "eta_trend": (["constant", "linear_increase", "linear_decrease"],)
            },
        }


class FluxDeGuidance(BizyAirBaseNode):

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "append"

    CATEGORY = "fluxtapoz"
    NODE_DISPLAY_NAME = "Flux DeGuidance"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "guidance": (
                    "FLOAT",
                    {"default": 3.5, "min": -100.0, "max": 100.0, "step": 0.1},
                ),
            }
        }
