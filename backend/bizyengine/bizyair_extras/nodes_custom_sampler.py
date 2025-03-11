from bizyengine.core import BizyAirBaseNode, data_types


class DisableNoise(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}}

    RETURN_TYPES = ("NOISE",)
    CATEGORY = "sampling/custom_sampling/noise"


class VPScheduler(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "beta_d": (
                    "FLOAT",
                    {
                        "default": 19.9,
                        "min": 0.0,
                        "max": 5000.0,
                        "step": 0.01,
                        "round": False,
                    },
                ),  # TODO: fix default values
                "beta_min": (
                    "FLOAT",
                    {
                        "default": 0.1,
                        "min": 0.0,
                        "max": 5000.0,
                        "step": 0.01,
                        "round": False,
                    },
                ),
                "eps_s": (
                    "FLOAT",
                    {
                        "default": 0.001,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.0001,
                        "round": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    CATEGORY = "sampling/custom_sampling/schedulers"


class SplitSigmas(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sigmas": ("SIGMAS",),
                "step": ("INT", {"default": 0, "min": 0, "max": 10000}),
            }
        }

    RETURN_TYPES = ("SIGMAS", "SIGMAS")
    RETURN_NAMES = ("high_sigmas", "low_sigmas")
    CATEGORY = "sampling/custom_sampling/sigmas"


class SplitSigmasDenoise(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sigmas": ("SIGMAS",),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("SIGMAS", "SIGMAS")
    RETURN_NAMES = ("high_sigmas", "low_sigmas")
    CATEGORY = "sampling/custom_sampling/sigmas"

    # FUNCTION = "get_sigmas"


class FlipSigmas(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sigmas": ("SIGMAS",),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    CATEGORY = "sampling/custom_sampling/sigmas"

    # FUNCTION = "get_sigmas"


class CFGGuider(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 8.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
            }
        }

    RETURN_TYPES = ("GUIDER",)

    # FUNCTION = "get_guider"
    CATEGORY = "sampling/custom_sampling/guiders"
