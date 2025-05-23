from bizyengine.core import BizyAirBaseNode, data_types
from bizyengine.core.nodes_io import BizyAirNodeIO


class CLIPTextEncodeFlux(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": (data_types.CLIP,),
                "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "guidance": (
                    "FLOAT",
                    {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    RETURN_NAMES = ("conditioning",)
    # FUNCTION = "encode"

    CATEGORY = "advanced/conditioning/flux"

    # def encode(self, clip: BizyAirNodeIO, clip_l: str, t5xxl: str, guidance: float):
    #     new_clip = clip.copy(self.assigned_id)
    #     new_clip.add_node_data(
    #         class_type="CLIPTextEncodeFlux",
    #         inputs={
    #             "clip": clip,
    #             "clip_l": clip_l,
    #             "t5xxl": t5xxl,
    #             "guidance": guidance,
    #         },
    #         outputs={"slot_index": 0},
    #     )
    #     return (new_clip,)


class FluxGuidance(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "guidance": (
                    "FLOAT",
                    {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    FUNCTION = "append"

    CATEGORY = "advanced/conditioning/flux"

    def append(self, conditioning: BizyAirNodeIO, guidance, **kwargs):
        new_conditioning = conditioning.copy(self.assigned_id)
        new_conditioning.add_node_data(
            class_type="FluxGuidance",
            inputs={
                "conditioning": conditioning,
                "guidance": guidance,
            },
            outputs={"slot_index": 0},
        )
        return (new_conditioning,)
