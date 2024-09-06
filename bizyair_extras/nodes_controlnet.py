from comfy.cldm.control_types import UNION_CONTROLNET_TYPES

from bizyair import BizyAirBaseNode, data_types


class SetUnionControlNetType(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net": (data_types.CONTROL_NET,),
                "type": (["auto"] + list(UNION_CONTROLNET_TYPES.keys()),),
            }
        }

    CATEGORY = "conditioning/controlnet"
    RETURN_TYPES = (data_types.CONTROL_NET,)

    # FUNCTION = "set_controlnet_type"
