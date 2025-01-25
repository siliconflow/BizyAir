import io

import matplotlib.pyplot as plt

import bizyair.path_utils as folder_paths
from bizyair import BizyAirBaseNode, BizyAirNodeIO


class FluxTrainModelSelect(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "transformer": (folder_paths.get_filename_list("unet"),),
                "vae": (folder_paths.get_filename_list("vae"),),
                "clip_l": (folder_paths.get_filename_list("clip"),),
                "t5": (folder_paths.get_filename_list("clip"),),
            },
            "optional": {
                "lora_path": (
                    "STRING",
                    {
                        "multiline": True,
                        "forceInput": True,
                        "default": "",
                        "tooltip": "pre-trained LoRA path to load (network_weights)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("TRAIN_FLUX_MODELS",)
    RETURN_NAMES = ("flux_models",)
    # FUNCTION = "loadmodel"
    CATEGORY = "FluxTrainer"


class TrainDatasetGeneralConfig(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "color_aug": ("BOOLEAN",{"default": False, "tooltip": "enable weak color augmentation"}),
            "flip_aug": ("BOOLEAN",{"default": False, "tooltip": "enable horizontal flip augmentation"}),
            "shuffle_caption": ("BOOLEAN",{"default": False, "tooltip": "shuffle caption"}),
            "caption_dropout_rate": ("FLOAT",{"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01,"tooltip": "tag dropout rate"}),
            "alpha_mask": ("BOOLEAN",{"default": False, "tooltip": "use alpha channel as mask for training"}),
            },
            "optional": {
                "reset_on_queue": ("BOOLEAN",{"default": False, "tooltip": "Force refresh of everything for cleaner queueing"}),
                "caption_extension": ("STRING",{"default": ".txt", "tooltip": "extension for caption files"}),
            }
        }


    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("dataset_general",)
    # FUNCTION = "create_config"
    CATEGORY = "FluxTrainer"


class StringConstantMultiline(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
                "strip_newlines": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "stringify"
    CATEGORY = "KJNodes/constants"
    NODE_DISPLAY_NAME = "String Constant Multiline"

    def stringify(self, string, strip_newlines):
        new_string = []
        for line in io.StringIO(string):
            if not line.strip().startswith("\n") and strip_newlines:
                line = line.replace("\n", "")
            new_string.append(line)
        new_string = "\n".join(new_string)

        return (new_string,)


class OptimizerConfig(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "optimizer_type": (
                    ["adamw8bit", "adamw", "prodigy", "CAME", "Lion8bit", "Lion"],
                    {"default": "adamw8bit", "tooltip": "optimizer type"},
                ),
                "max_grad_norm": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "tooltip": "gradient clipping"},
                ),
                "lr_scheduler": (
                    [
                        "constant",
                        "cosine",
                        "cosine_with_restarts",
                        "polynomial",
                        "constant_with_warmup",
                    ],
                    {"default": "constant", "tooltip": "learning rate scheduler"},
                ),
                "lr_warmup_steps": (
                    "INT",
                    {"default": 0, "min": 0, "tooltip": "learning rate warmup steps"},
                ),
                "lr_scheduler_num_cycles": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "tooltip": "learning rate scheduler num cycles",
                    },
                ),
                "lr_scheduler_power": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "tooltip": "learning rate scheduler power",
                    },
                ),
                "min_snr_gamma": (
                    "FLOAT",
                    {
                        "default": 5.0,
                        "min": 0.0,
                        "step": 0.01,
                        "tooltip": "gamma for reducing the weight of high loss timesteps. Lower numbers have stronger effect. 5 is recommended by the paper",
                    },
                ),
                "extra_optimizer_args": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "additional optimizer args",
                    },
                ),
            },
        }

    RETURN_TYPES = ("ARGS",)
    RETURN_NAMES = ("optimizer_settings",)
    # FUNCTION = "create_config"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Optimizer Config"


class FluxTrainValidationSettings(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": (
                    "INT",
                    {
                        "default": 20,
                        "min": 1,
                        "max": 256,
                        "step": 1,
                        "tooltip": "sampling steps",
                    },
                ),
                "width": (
                    "INT",
                    {
                        "default": 512,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "image width",
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 512,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "image height",
                    },
                ),
                "guidance_scale": (
                    "FLOAT",
                    {
                        "default": 3.5,
                        "min": 1.0,
                        "max": 32.0,
                        "step": 0.05,
                        "tooltip": "guidance scale",
                    },
                ),
                "seed": (
                    "INT",
                    {"default": 42, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1},
                ),
                "shift": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "shift the schedule to favor high timesteps for higher signal images",
                    },
                ),
                "base_shift": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "max_shift": (
                    "FLOAT",
                    {"default": 1.15, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = ("VALSETTINGS",)
    RETURN_NAMES = ("validation_settings",)
    # FUNCTION = "set"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Flux Train Validation Settings"

    # def set(self, **kwargs):
    #     validation_settings = kwargs
    #     print(validation_settings)

    #     return (validation_settings,)


class TrainDatasetAdd(BizyAirBaseNode):
    def __init__(self):
        super().__init__()
        self.previous_dataset_signature = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "dataset_config": ("JSON",),
                "width": (
                    "INT",
                    {"min": 64, "default": 1024, "tooltip": "base resolution width"},
                ),
                "height": (
                    "INT",
                    {"min": 64, "default": 1024, "tooltip": "base resolution height"},
                ),
                "batch_size": (
                    "INT",
                    {
                        "min": 1,
                        "default": 2,
                        "tooltip": "Higher batch size uses more memory and generalizes the training more",
                    },
                ),
                "dataset_path": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "path to dataset, root is the 'ComfyUI' folder, with windows portable 'ComfyUI_windows_portable'",
                    },
                ),
                "class_tokens": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "aka trigger word, if specified, will be added to the start of each caption, if no captions exist, will be used on it's own",
                    },
                ),
                "enable_bucket": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "enable buckets for multi aspect ratio training",
                    },
                ),
                "bucket_no_upscale": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "don't allow upscaling when bucketing",
                    },
                ),
                "num_repeats": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "tooltip": "number of times to repeat dataset for an epoch",
                    },
                ),
                "min_bucket_reso": (
                    "INT",
                    {
                        "default": 256,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "min bucket resolution",
                    },
                ),
                "max_bucket_reso": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "max bucket resolution",
                    },
                ),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("dataset",)
    # FUNCTION = "create_config"
    CATEGORY = "FluxTrainer"


class InitFluxLoRATraining(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "flux_models": ("TRAIN_FLUX_MODELS",),
            "dataset": ("JSON",),
            "optimizer_settings": ("ARGS",),
            "output_name": ("STRING", {"default": "flux_lora", "multiline": False}),
            "output_dir": ("STRING", {"default": "flux_trainer_output", "multiline": False, "tooltip": "path to dataset, root is the 'ComfyUI' folder, with windows portable 'ComfyUI_windows_portable'"}),
            "network_dim": ("INT", {"default": 4, "min": 1, "max": 2048, "step": 1, "tooltip": "network dim"}),
            "network_alpha": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2048.0, "step": 0.01, "tooltip": "network alpha"}),
            "learning_rate": ("FLOAT", {"default": 4e-4, "min": 0.0, "max": 10.0, "step": 0.000001, "tooltip": "learning rate"}),
            "max_train_steps": ("INT", {"default": 1500, "min": 1, "max": 100000, "step": 1, "tooltip": "max number of training steps"}),
            "apply_t5_attn_mask": ("BOOLEAN", {"default": True, "tooltip": "apply t5 attention mask"}),
            "cache_latents": (["disk", "memory", "disabled"], {"tooltip": "caches text encoder outputs"}),
            "cache_text_encoder_outputs": (["disk", "memory", "disabled"], {"tooltip": "caches text encoder outputs"}),
            "blocks_to_swap": ("INT", {"default": 0, "tooltip": "Previously known as split_mode, number of blocks to swap to save memory, default to enable is 18"}),
            "weighting_scheme": (["logit_normal", "sigma_sqrt", "mode", "cosmap", "none"],),
            "logit_mean": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "mean to use when using the logit_normal weighting scheme"}),
            "logit_std": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01,"tooltip": "std to use when using the logit_normal weighting scheme"}),
            "mode_scale": ("FLOAT", {"default": 1.29, "min": 0.0, "max": 10.0, "step": 0.01, "tooltip": "Scale of mode weighting scheme. Only effective when using the mode as the weighting_scheme"}),
            "timestep_sampling": (["sigmoid", "uniform", "sigma", "shift", "flux_shift"], {"tooltip": "Method to sample timesteps: sigma-based, uniform random, sigmoid of random normal and shift of sigmoid (recommend value of 3.1582 for discrete_flow_shift)"}),
            "sigmoid_scale": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1, "tooltip": "Scale factor for sigmoid timestep sampling (only used when timestep-sampling is sigmoid"}),
            "model_prediction_type": (["raw", "additive", "sigma_scaled"], {"tooltip": "How to interpret and process the model prediction: raw (use as is), additive (add to noisy input), sigma_scaled (apply sigma scaling)."}),
            "guidance_scale": ("FLOAT", {"default": 1.0, "min": 1.0, "max": 32.0, "step": 0.01, "tooltip": "guidance scale, for Flux training should be 1.0"}),
            "discrete_flow_shift": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.0001, "tooltip": "for the Euler Discrete Scheduler, default is 3.0"}),
            "highvram": ("BOOLEAN", {"default": False, "tooltip": "memory mode"}),
            "fp8_base": ("BOOLEAN", {"default": True, "tooltip": "use fp8 for base model"}),
            "gradient_dtype": (["fp32", "fp16", "bf16"], {"default": "fp32", "tooltip": "the actual dtype training uses"}),
            "save_dtype": (["fp32", "fp16", "bf16", "fp8_e4m3fn", "fp8_e5m2"], {"default": "bf16", "tooltip": "the dtype to save checkpoints as"}),
            "attention_mode": (["sdpa", "xformers", "disabled"], {"default": "sdpa", "tooltip": "memory efficient attention mode"}),
            "sample_prompts": ("STRING", {"multiline": True, "default": "illustration of a kitten | photograph of a turtle", "tooltip": "validation sample prompts, for multiple prompts, separate by `|`"}),
            },
            "optional": {
                "additional_args": ("STRING", {"multiline": True, "default": "", "tooltip": "additional args to pass to the training command"}),
                "resume_args": ("ARGS", {"default": "", "tooltip": "resume args to pass to the training command"}),
                "train_text_encoder": (['disabled', 'clip_l', 'clip_l_fp8', 'clip_l+T5', 'clip_l+T5_fp8'], {"default": 'disabled', "tooltip": "also train the selected text encoders using specified dtype, T5 can not be trained without clip_l"}),
                "clip_l_lr": ("FLOAT", {"default": 0, "min": 0.0, "max": 10.0, "step": 0.000001, "tooltip": "text encoder learning rate"}),
                "T5_lr": ("FLOAT", {"default": 0, "min": 0.0, "max": 10.0, "step": 0.000001, "tooltip": "text encoder learning rate"}),
                "block_args": ("ARGS", {"default": "", "tooltip": "limit the blocks used in the LoRA"}),
                "gradient_checkpointing": (["enabled", "enabled_with_cpu_offloading", "disabled"], {"default": "enabled", "tooltip": "use gradient checkpointing"}),
                "loss_args": ("ARGS", {"default": "", "tooltip": "loss args"}),
            },
            # "hidden": {
            #     "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            # },
        }

    RETURN_TYPES = (
        "NETWORKTRAINER",
        "INT",
        "KOHYA_ARGS",
    )
    RETURN_NAMES = (
        "network_trainer",
        "epochs_count",
        "args",
    )
    # FUNCTION = "init_training"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Init Flux LoRA Training"


class FluxTrainLoop(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "network_trainer": ("NETWORKTRAINER",),
                "steps": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 10000,
                        "step": 1,
                        "tooltip": "the step point in training to validate/save",
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "NETWORKTRAINER",
        "INT",
    )
    RETURN_NAMES = (
        "network_trainer",
        "steps",
    )
    # FUNCTION = "train"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Flux Train Loop"


class FluxTrainSave(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "network_trainer": ("NETWORKTRAINER",),
                "save_state": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "save the whole model state as well"},
                ),
                "copy_to_comfy_lora_folder": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "copy the lora model to the comfy lora folder",
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "NETWORKTRAINER",
        "STRING",
        "INT",
    )
    RETURN_NAMES = (
        "network_trainer",
        "lora_path",
        "steps",
    )
    # FUNCTION = "save"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Flux Train Save LoRA"


class VisualizeLoss(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "network_trainer": ("NETWORKTRAINER",),
                "plot_style": (
                    plt.style.available,
                    {"default": "default", "tooltip": "matplotlib plot style"},
                ),
                "window_size": (
                    "INT",
                    {
                        "default": 100,
                        "min": 0,
                        "max": 10000,
                        "step": 1,
                        "tooltip": "the window size of the moving average",
                    },
                ),
                "normalize_y": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "normalize the y-axis to 0"},
                ),
                "width": (
                    "INT",
                    {
                        "default": 768,
                        "min": 256,
                        "max": 4096,
                        "step": 2,
                        "tooltip": "width of the plot in pixels",
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 512,
                        "min": 256,
                        "max": 4096,
                        "step": 2,
                        "tooltip": "height of the plot in pixels",
                    },
                ),
                "log_scale": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "use log scale on the y-axis"},
                ),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "FLOAT",
    )
    RETURN_NAMES = (
        "plot",
        "loss_list",
    )
    # FUNCTION = "draw"
    CATEGORY = "FluxTrainer"


class FluxTrainEnd(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "network_trainer": ("NETWORKTRAINER",),
                "save_state": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
    )
    RETURN_NAMES = (
        "lora_name",
        "metadata",
        "lora_path",
    )
    # FUNCTION = "endtrain"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Flux LoRA Train End"


class BizyAir_FluxTrainValidate(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "network_trainer": ("NETWORKTRAINER",),
            },
            "optional": {
                "validation_settings": ("VALSETTINGS",),
            },
        }

    RETURN_TYPES = (
        "NETWORKTRAINER",
        "IMAGE",
    )
    RETURN_NAMES = (
        "network_trainer",
        "validation_images",
    )
    # FUNCTION = "validate"
    CATEGORY = "FluxTrainer"
    NODE_DISPLAY_NAME = "Flux Train Validate"



class FluxLoraUploadToBizyair(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                "network_trainer": ("NETWORKTRAINER",),},
                "optional": {
                    "token": ("STRING", {"default": "","tooltip":""}),
                }
            }
    RETURN_TYPES = ("NETWORKTRAINER", "STRING",)
    RETURN_NAMES = ("network_trainer","status",)
    # FUNCTION = "upload"
    CATEGORY = "FluxTrainer"