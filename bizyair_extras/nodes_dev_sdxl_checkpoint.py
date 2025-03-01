
from bizyair import BizyAirBaseNode
from bizyair import data_types
from bizyair.nodes_io import BizyAirNodeIO, create_node_data
from bizyair.configs.conf import config_manager

class BizyAir_Dev_Model_Loader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": ( "STRING",
                    {"multiline": True,
                     "default": "bizy_model",
                      "dynamicPrompts": True},),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP, data_types.VAE)
    FUNCTION = "load_checkpoint"
    CATEGORY = f"loaders"
    RETURN_NAMES = (
        f"model",
        f"clip",
        f"vae",
    )
    def load_checkpoint(self, ckpt_name):
        ckpt_name = f"{config_manager.get_model_version_id_prefix()}{ckpt_name}"
        node_datas = [
            create_node_data(
                class_type="CheckpointLoaderSimple",
                inputs={"ckpt_name": ckpt_name},
                outputs={"slot_index": slot_index},
            )
            for slot_index in range(3)
        ]
        assigned_id = self.assigned_id
        outs = [
            BizyAirNodeIO(
                assigned_id,
                {assigned_id: data},
            )
            for data in node_datas
        ]
        return (
            outs[0],
            outs[1],
            outs[2],
        )