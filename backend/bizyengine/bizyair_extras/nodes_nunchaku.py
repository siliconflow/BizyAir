from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, data_types
from bizyengine.core.configs.conf import config_manager
from bizyengine.core.path_utils import path_manager as folder_paths


class NunchakuFluxDiTLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        attention_options = ["nunchaku-fp16"]
        dtype_options = ["bfloat16"]
        return {
            "required": {
                "model_path": (
                    ["svdq-int4-flux.1-dev"],
                    {"tooltip": "The SVDQuant quantized FLUX.1 models."},
                ),
                "cache_threshold": (
                    "FLOAT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 1,
                        "step": 0.001,
                        "tooltip": "Adjusts the caching tolerance like `residual_diff_threshold` in WaveSpeed. "
                        "Increasing the value enhances speed at the cost of quality. "
                        "A typical setting is 0.12. Setting it to 0 disables the effect.",
                    },
                ),
                "attention": (
                    attention_options,
                    {
                        "default": attention_options[0],
                        "tooltip": "Attention implementation. The default implementation is `flash-attention2`. "
                        "`nunchaku-fp16` use FP16 attention, offering ~1.2× speedup. "
                        "Note that 20-series GPUs can only use `nunchaku-fp16`.",
                    },
                ),
                "cpu_offload": (
                    ["disable"],
                    {
                        "default": "auto",
                        "tooltip": "Whether to enable CPU offload for the transformer model."
                        "auto' will enable it if the GPU memory is less than 14G.",
                    },
                ),
                "device_id": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0,
                        "step": 1,
                        "display": "number",
                        "lazy": True,
                        "tooltip": "The GPU device ID to use for the model.",
                    },
                ),
                "data_type": (
                    dtype_options,
                    {
                        "default": dtype_options[0],
                        "tooltip": "Specifies the model's data type. Default is `bfloat16`. "
                        "For 20-series GPUs, which do not support `bfloat16`, use `float16` instead.",
                    },
                ),
            },
            "optional": {
                "i2f_mode": (
                    ["enabled", "always"],
                    {
                        "default": "enabled",
                        "tooltip": "The GEMM implementation for 20-series GPUs"
                        "— this option is only applicable to these GPUs.",
                    },
                )
            },
        }

    RETURN_TYPES = (data_types.MODEL,)
    CATEGORY = "Nunchaku"
    NODE_DISPLAY_NAME = "Nunchaku FLUX DiT Loader"


class NunchakuTextEncoderLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_type": (["flux"],),
                "text_encoder1": (folder_paths.get_filename_list("text_encoders"),),
                "text_encoder2": (folder_paths.get_filename_list("text_encoders"),),
                "t5_min_length": (
                    "INT",
                    {
                        "default": 512,
                        "min": 256,
                        "max": 1024,
                        "step": 128,
                        "display": "number",
                        "lazy": True,
                    },
                ),
                "use_4bit_t5": (["disable"],),
                "int4_model": (
                    ["none"],
                    {"tooltip": "The name of the 4-bit T5 model."},
                ),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    # FUNCTION = "load_text_encoder"
    CATEGORY = "Nunchaku"
    NODE_DISPLAY_NAME = "Nunchaku Text Encoder Loader"


class NunchakuFluxLoraLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (
                    data_types.MODEL,
                    {"tooltip": "The diffusion model the LoRA will be applied to."},
                ),
                "lora_name": (
                    [
                        "to choose",
                    ],
                    {"tooltip": "The name of the LoRA."},
                ),
                "lora_strength": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -100.0,
                        "max": 100.0,
                        "step": 0.01,
                        "tooltip": "How strongly to modify the diffusion model. This value can be negative.",
                    },
                ),
                "model_version_id": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    OUTPUT_TOOLTIPS = ("The modified diffusion model.",)
    FUNCTION = "load_lora"
    NODE_DISPLAY_NAME = "Nunchaku FLUX.1 LoRA Loader"

    CATEGORY = "Nunchaku"
    DESCRIPTION = (
        "LoRAs are used to modify the diffusion model, "
        "altering the way in which latents are denoised such as applying styles. "
        "You can link multiple LoRA nodes."
    )

    @classmethod
    def VALIDATE_INPUTS(cls, lora_name, **kwargs):
        if lora_name == "" or lora_name is None:
            return False
        return True

    def load_lora(
        self, model, lora_name, lora_strength, model_version_id: str = None, **kwargs
    ):
        assigned_id = self.assigned_id
        new_model: BizyAirNodeIO = model.copy(assigned_id)

        if model_version_id is not None and model_version_id != "":
            # use model version id as lora name
            lora_name = (
                f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
            )
        new_model.add_node_data(
            class_type="NunchakuFluxLoraLoader",
            inputs={
                "model": model,
                "lora_name": lora_name,
                "lora_strength": lora_strength,
            },
            outputs={"slot_index": 0},
        )
        return (new_model,)


class NunchakuPulidApply(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pulid": ("BIZYAIR_PULID", {"tooltip": "from Nunchaku Pulid Loader"}),
                "image": ("IMAGE", {"tooltip": "The image to encode"}),
                "model": (data_types.MODEL, {"tooltip": "The nunchaku model."}),
                "ip_weight": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "tooltip": "ip_weight",
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "apply"
    CATEGORY = "Nunchaku"
    TITLE = "Nunchaku Pulid Apply"


class NunchakuPulidLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL, {"tooltip": "The nunchaku model."}),
            }
        }

    RETURN_TYPES = (
        data_types.MODEL,
        "BIZYAIR_PULID",
    )
    # FUNCTION = "load"
    CATEGORY = "Nunchaku"
    TITLE = "Nunchaku Pulid Loader"
