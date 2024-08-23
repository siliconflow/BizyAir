import os

from bizyair import BizyAirBaseNode
from bizyair import path_utils as folder_paths
from bizyair.data_types import CLIP, CONDITIONING, CONTROL_NET, MODEL
from bizyair.image_utils import BizyAirNodeIO, create_node_data

AUTHOR_NAME = "MinusZone"
CATEGORY_NAME = f"Kolors"


class MZ_KolorsUNETLoaderV2(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("unet"),),
            }
        }

    RETURN_TYPES = (MODEL,)
    RETURN_NAMES = ("model",)

    FUNCTION = "load_unet"

    CATEGORY = CATEGORY_NAME
    NODE_DISPLAY_NAME = f"{AUTHOR_NAME} - KolorsUNETLoaderV2"

    def load_unet(self, **kwargs):

        node_data = create_node_data(
            class_type="MZ_KolorsUNETLoaderV2",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        config_file = folder_paths.guess_config(unet_name=kwargs["unet_name"])
        out = BizyAirNodeIO(
            self.assigned_id, {self.assigned_id: node_data}, config_file=config_file
        )
        return (out,)


WEIGHT_TYPES = [
    "linear",
    "ease in",
    "ease out",
    "ease in-out",
    "reverse in-out",
    "weak input",
    "weak output",
    "weak middle",
    "strong middle",
    "style transfer",
    "composition",
    "strong style transfer",
    "style and composition",
    "style transfer precise",
    "composition precise",
]


class MZ_KolorsControlNetLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_name": (folder_paths.get_filename_list("controlnet"),),
                # "seed": ("INT", {"default": 0, "min": 0, "max": 1000000}),
            }
        }

    RETURN_TYPES = (CONTROL_NET,)
    RETURN_NAMES = ("ControlNet",)
    FUNCTION = "load_controlnet"

    CATEGORY = CATEGORY_NAME
    NODE_DISPLAY_NAME = f"{AUTHOR_NAME} - KolorsControlNetLoader"

    def load_controlnet(self, **kwargs):
        node_data = create_node_data(
            class_type="MZ_KolorsControlNetLoader",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        assigned_id = self.assigned_id
        node = BizyAirNodeIO(assigned_id, {assigned_id: node_data})
        return (node,)
