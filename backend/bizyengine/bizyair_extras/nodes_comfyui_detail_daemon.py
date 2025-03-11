"""
Reference: https://github.com/Jonseed/ComfyUI-Detail-Daemon
"""

from bizyengine.core import BizyAirBaseNode


class DetailDaemonSamplerNode(BizyAirBaseNode):
    DESCRIPTION = "This sampler wrapper works by adjusting the sigma passed to the model, while the rest of sampling stays the same."
    CATEGORY = "sampling/custom_sampling/samplers"
    RETURN_TYPES = ("SAMPLER",)
    # FUNCTION = "go"

    NODE_DISPLAY_NAME = "Detail Daemon Sampler"

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "sampler": ("SAMPLER",),
                "detail_amount": (
                    "FLOAT",
                    {"default": 0.1, "min": -5.0, "max": 5.0, "step": 0.01},
                ),
                "start": (
                    "FLOAT",
                    {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "end": (
                    "FLOAT",
                    {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "bias": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "exponent": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05},
                ),
                "start_offset": (
                    "FLOAT",
                    {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},
                ),
                "end_offset": (
                    "FLOAT",
                    {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},
                ),
                "fade": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "smooth": ("BOOLEAN", {"default": True}),
                "cfg_scale_override": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.5,
                        "round": 0.01,
                        "tooltip": "If set to 0, the sampler will automatically determine the CFG scale (if possible). Set to some other value to override.",
                    },
                ),
            },
        }


class MultiplySigmas(BizyAirBaseNode):
    # FUNCTION = "simple_output"
    RETURN_TYPES = ("SIGMAS",)
    CATEGORY = "sampling/custom_sampling/sigmas"
    NODE_DISPLAY_NAME = "Multiply Sigmas (stateless)"

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "sigmas": ("SIGMAS", {"forceInput": True}),
                "factor": (
                    "FLOAT",
                    {"default": 1, "min": 0, "max": 100, "step": 0.001},
                ),
                "start": ("FLOAT", {"default": 0, "min": 0, "max": 1, "step": 0.001}),
                "end": ("FLOAT", {"default": 1, "min": 0, "max": 1, "step": 0.001}),
            }
        }


class LyingSigmaSampler(BizyAirBaseNode):
    CATEGORY = "sampling/custom_sampling"
    RETURN_TYPES = ("SAMPLER",)
    NODE_DISPLAY_NAME = "Lying Sigma Sampler"
    # FUNCTION = "go"

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "sampler": ("SAMPLER",),
                "dishonesty_factor": (
                    "FLOAT",
                    {
                        "default": -0.05,
                        "min": -0.999,
                        "step": 0.01,
                        "tooltip": "Multiplier for sigmas passed to the model. -0.05 means we reduce the sigma by 5%.",
                    },
                ),
            },
            "optional": {
                "start_percent": (
                    "FLOAT",
                    {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "end_percent": (
                    "FLOAT",
                    {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }


class DetailDaemonGraphSigmasNode(BizyAirBaseNode):
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = "sampling/custom_sampling/sigmas"
    NODE_DISPLAY_NAME = "Detail Daemon Graph Sigmas"
    # FUNCTION = "make_graph"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sigmas": ("SIGMAS", {"forceInput": True}),
                "detail_amount": (
                    "FLOAT",
                    {"default": 0.1, "min": -5.0, "max": 5.0, "step": 0.01},
                ),
                "start": (
                    "FLOAT",
                    {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "end": (
                    "FLOAT",
                    {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "bias": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "exponent": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05},
                ),
                "start_offset": (
                    "FLOAT",
                    {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},
                ),
                "end_offset": (
                    "FLOAT",
                    {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},
                ),
                "fade": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "smooth": ("BOOLEAN", {"default": True}),
                "cfg_scale": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.5,
                        "round": 0.01,
                    },
                ),
            },
        }
