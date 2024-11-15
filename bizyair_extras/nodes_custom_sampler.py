from bizyair import BizyAirBaseNode, data_types


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
