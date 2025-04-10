import os

from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, create_node_data
from bizyengine.core import path_utils as folder_paths
from bizyengine.core.configs.conf import config_manager
from bizyengine.core.data_types import CLIP, CONDITIONING, CONTROL_NET, MODEL

AUTHOR_NAME = "MinusZone"
CATEGORY_NAME = f"Kolors"


class MZ_KolorsUNETLoaderV2(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("unet"),),
                # "unet_name": (
                #     [
                #         "to choose",
                #     ],
                # ),
                # "model_version_id": (
                #     "STRING",
                #     {
                #         "default": "",
                #     },
                # ),
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

    # @classmethod
    # def VALIDATE_INPUTS(cls, unet_name):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if unet_name == "" or unet_name is None:
    #         return False
    #     return True

    # def load_unet(self, **kwargs):
    #     model_version_id = kwargs.get("model_version_id", "")
    #     if model_version_id != "":
    #         # use model version id as lora name
    #         unet_name = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
    #         )
    #         kwargs["unet_name"] = unet_name
    #     node_data = create_node_data(
    #         class_type="MZ_KolorsUNETLoaderV2",
    #         inputs=kwargs,
    #         outputs={"slot_index": 0},
    #     )
    #     config_file = folder_paths.guess_config(unet_name=kwargs["unet_name"])
    #     out = BizyAirNodeIO(
    #         self.assigned_id, {self.assigned_id: node_data}, config_file=config_file
    #     )
    #     return (out,)


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
