import os
from ...register import BizyAirBaseNode
from ...data_types import MODEL, CLIP, CONDITIONING
from ...image_utils import BizyAirNodeIO, create_node_data

AUTHOR_NAME = "MinusZone"
CATEGORY_NAME = f"{AUTHOR_NAME} - Kolors"

class MZ_KolorsUNETLoaderV2(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                "unet_name": (["kolors/kolors-unet.safetensors"], ),
                }}

    RETURN_TYPES = (MODEL,)
    RETURN_NAMES = ("model",)

    FUNCTION = "load_unet"

    CATEGORY = CATEGORY_NAME
    NODE_DISPLAY_NAME = f"{AUTHOR_NAME} - KolorsUNETLoaderV2"

    def load_unet(self, **kwargs):
        current_directory = os.path.dirname(__file__)
        config_file = os.path.join(current_directory, "config", "kolors_config.yaml")
    
        node_data = create_node_data(
            class_type="MZ_KolorsUNETLoaderV2",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        out = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
        return (out,)


class MZ_IPAdapterModelLoaderKolors(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "ipadapter_file": (["kolors/ip_adapter_plus_general.bin"], )}}

    RETURN_TYPES = ("IPADAPTER",)
    FUNCTION = "load_ipadapter_model"
    CATEGORY = "ipadapter/loaders"
    NODE_DISPLAY_NAME = f"IPAdapterModelLoader(kolors) - Legacy"
    def load_ipadapter_model(self, **kwargs):
        node_data = create_node_data(
            class_type="MZ_IPAdapterModelLoaderKolors",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        out = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
        return (out,)

WEIGHT_TYPES = ["linear", "ease in", "ease out", 'ease in-out', 'reverse in-out', 'weak input', 'weak output', 'weak middle', 'strong middle', 'style transfer', 'composition', 'strong style transfer', 'style and composition', 'style transfer precise', 'composition precise']


class MZ_IPAdapterAdvancedKolors(BizyAirBaseNode):
    def __init__(self):
        super().__init__()
        self.unfold_batch = False

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (MODEL, ),
                "ipadapter": ("IPADAPTER", ),
                "image": ("IMAGE",),
                "weight": ("FLOAT", { "default": 1.0, "min": -1, "max": 5, "step": 0.05 }),
                "weight_type": (WEIGHT_TYPES, ),
                "combine_embeds": (["concat", "add", "subtract", "average", "norm average"],),
                "start_at": ("FLOAT", { "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001 }),
                "end_at": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001 }),
                "embeds_scaling": (['V only', 'K+V', 'K+V w/ C penalty', 'K+mean(V) w/ C penalty'], ),
            },
            "optional": {
                "image_negative": ("IMAGE",),
                "attn_mask": ("MASK",),
                "clip_vision": ("CLIP_VISION",),
            }
        }

    RETURN_TYPES = (MODEL,)
    RETURN_NAMES = ("model",)
    FUNCTION = "apply_ipadapter"
    CATEGORY = f"ipadapter"
    NODE_DISPLAY_NAME = f"IPAdapterAdvanced(kolors) - Legacy"
    def apply_ipadapter(self, **kwargs):
        node_data = create_node_data(
            class_type="MZ_IPAdapterAdvancedKolors",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        out = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
        return (out,)

