from bizyengine.core import BizyAirBaseNode, data_types


class DifferentialDiffusion(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "apply"
    CATEGORY = "_for_testing"
    INIT = False
