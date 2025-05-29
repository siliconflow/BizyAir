import os
from typing import List

import comfy
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, create_node_data, data_types
from bizyengine.core.configs.conf import config_manager
from bizyengine.core.path_utils import path_manager as folder_paths

LOGO = "☁️"
PREFIX = f"{LOGO}BizyAir"

MAX_RESOLUTION = 16384  # https://github.com/comfyanonymous/ComfyUI/blob/7390ff3b1ec2e15017ba4a52d6eaabc4aa4636e3/nodes.py#L45


class ProgressCallback:
    def __init__(self, total=None) -> None:
        comfy.model_management.throw_exception_if_processing_interrupted()
        self.pbar = comfy.utils.ProgressBar(None)

    def __call__(self, value, total=None, preview=None):
        self.pbar.update_absolute(value, total, preview)


class BizyAir_KSampler(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 50}),
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
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "latent_image": ("LATENT",),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    # FUNCTION = "sample"
    RETURN_NAMES = (f"LATENT",)
    CATEGORY = f"{PREFIX}/sampling"

    # deprecated
    def sample(
        self,
        model,
        seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        positive,
        negative,
        latent_image,
        denoise=1,
    ):
        new_model: BizyAirNodeIO = model.copy(self.assigned_id)
        new_model.add_node_data(
            class_type="KSampler",
            inputs={
                "model": model,
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "positive": positive,
                "negative": negative,
                "latent_image": latent_image,
                "denoise": denoise,
            },
            outputs={"slot_index": 0},
        )
        progress_callback = ProgressCallback()
        return new_model.send_request(progress_callback=progress_callback)


class KSamplerAdvanced(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "add_noise": (["enable", "disable"],),
                "noise_seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
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
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "latent_image": ("LATENT",),
                "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                "return_with_leftover_noise": (["disable", "enable"],),
            }
        }

    RETURN_TYPES = ("LATENT",)
    # FUNCTION = "sample"

    CATEGORY = "sampling"

    def sample(self, model, **kwargs):
        new_model: BizyAirNodeIO = model.copy(self.assigned_id)
        kwargs["model"] = model
        new_model.add_node_data(class_type="KSamplerAdvanced", inputs=kwargs)
        progress_callback = ProgressCallback()
        return new_model.send_request(progress_callback=progress_callback)


class BizyAir_CheckpointLoaderSimple(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (
                    [
                        "to choose",
                    ],
                ),
                "model_version_id": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP, data_types.VAE)
    FUNCTION = "load_checkpoint"
    CATEGORY = f"{PREFIX}/loaders"
    RETURN_NAMES = (
        f"model",
        f"clip",
        f"vae",
    )

    @classmethod
    def VALIDATE_INPUTS(cls, ckpt_name):
        # TODO
        import warnings

        warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
        if ckpt_name == "" or ckpt_name is None:
            return False
        return True

    def load_checkpoint(self, ckpt_name, model_version_id="", **kwargs):
        if model_version_id != "":
            # use model version id as lora name
            ckpt_name = (
                f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
            )
        node_datas = [
            create_node_data(
                class_type="CheckpointLoaderSimple",
                inputs={"ckpt_name": ckpt_name},
                outputs={"slot_index": slot_index},
            )
            for slot_index in range(3)
        ]
        config_file = folder_paths.guess_config(ckpt_name=ckpt_name)
        assigned_id = self.assigned_id
        outs = [
            BizyAirNodeIO(
                assigned_id,
                {assigned_id: data},
                config_file=config_file,
            )
            for data in node_datas
        ]

        return (
            outs[0],
            outs[1],
            outs[2],
        )


class BizyAir_CLIPTextEncode(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": (
                    "STRING",
                    {"multiline": True, "dynamicPrompts": True},
                ),
                "clip": (data_types.CLIP,),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    RETURN_NAMES = ("CONDITIONING",)
    # FUNCTION = "encode"

    CATEGORY = f"{PREFIX}/conditioning"

    def encode(self, clip, text):
        new_clip: BizyAirNodeIO = clip.copy(self.assigned_id)

        new_clip.add_node_data(
            class_type="CLIPTextEncode",
            inputs={
                "text": text,
                "clip": clip,
            },
            outputs={"slot_index": 0},
        )
        return (new_clip,)


class BizyAir_VAEDecode(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"samples": ("LATENT",), "vae": (data_types.VAE,)}}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (f"IMAGE",)
    # FUNCTION = "decode"

    CATEGORY = f"{PREFIX}/latent"

    def decode(self, vae, samples):
        new_vae: BizyAirNodeIO = vae.copy(self.assigned_id)
        new_vae.add_node_data(
            class_type="VAEDecode",
            inputs={
                "samples": samples,
                "vae": vae,
            },
            outputs={"slot_index": 0},
        )
        return new_vae.send_request()


class BizyAir_LoraLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "clip": (data_types.CLIP,),
                "lora_name": (
                    [
                        "to choose",
                    ],
                ),
                "strength_model": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
                "strength_clip": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
                "model_version_id": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP)
    RETURN_NAMES = ("MODEL", "CLIP")

    # 不能使用default_function
    FUNCTION = "load_lora"
    CATEGORY = f"{PREFIX}/loaders"

    def load_lora(
        self,
        model,
        clip,
        lora_name,
        strength_model,
        strength_clip,
        model_version_id: str = None,
        **kwargs,
    ):
        assigned_id = self.assigned_id
        new_model: BizyAirNodeIO = model.copy(assigned_id)
        new_clip: BizyAirNodeIO = clip.copy(assigned_id)
        instances: List[BizyAirNodeIO] = [new_model, new_clip]

        if model_version_id is not None and model_version_id != "":
            # use model version id as lora name
            lora_name = (
                f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
            )

        for slot_index, ins in zip(range(2), instances):
            ins.add_node_data(
                class_type="LoraLoader",
                inputs={
                    "model": model,
                    "clip": clip,
                    "lora_name": lora_name,
                    "strength_model": strength_model,
                    "strength_clip": strength_clip,
                },
                outputs={"slot_index": slot_index},
            )
        return (
            new_model,
            new_clip,
        )

    @classmethod
    def VALIDATE_INPUTS(cls, lora_name):
        if lora_name == "" or lora_name is None:
            return False
        return True


class BizyAir_LoraLoader_Legacy(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "clip": (data_types.CLIP,),
                "lora_name": (folder_paths.get_filename_list("loras"),),
                "strength_model": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
                "strength_clip": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP)
    RETURN_NAMES = ("MODEL", "CLIP")

    FUNCTION = "load_lora"

    CATEGORY = f"{PREFIX}/loaders"

    def load_lora(
        self, model, clip, lora_name, strength_model, strength_clip, **kwargs
    ):
        assigned_id = self.assigned_id
        new_model: BizyAirNodeIO = model.copy(assigned_id)
        new_clip: BizyAirNodeIO = clip.copy(assigned_id)
        instances: List[BizyAirNodeIO] = [new_model, new_clip]
        for slot_index, ins in zip(range(2), instances):
            ins.add_node_data(
                class_type="LoraLoader",
                inputs={
                    "model": model,
                    "clip": clip,
                    "lora_name": lora_name,
                    "strength_model": strength_model,
                    "strength_clip": strength_clip,
                },
                outputs={"slot_index": slot_index},
            )
        return (
            new_model,
            new_clip,
        )


class BizyAir_VAEEncode(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"pixels": ("IMAGE",), "vae": (data_types.VAE,)}}

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = (f"LATENT",)
    # FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent"

    # deprecated
    def encode(self, vae, pixels):
        new_vae: BizyAirNodeIO = vae.copy(self.assigned_id)
        new_vae.add_node_data(
            class_type="VAEEncode",
            inputs={
                "vae": vae,
                "pixels": pixels,
            },
            outputs={"slot_index": 0},
        )
        return new_vae.send_request()


class BizyAir_VAEEncodeForInpaint(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pixels": ("IMAGE",),
                "vae": (data_types.VAE,),
                "mask": ("MASK",),
                "grow_mask_by": ("INT", {"default": 6, "min": 0, "max": 64, "step": 1}),
            }
        }

    RETURN_TYPES = (f"LATENT",)
    RETURN_NAMES = (f"LATENT",)
    # FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent/inpaint"

    # deprecated
    def encode(self, vae, pixels, mask, grow_mask_by=6):
        new_vae: BizyAirNodeIO = vae.copy(self.assigned_id)
        new_vae.add_node_data(
            class_type="VAEEncodeForInpaint",
            inputs={
                "vae": vae,
                "pixels": pixels,
                "mask": mask,
                "grow_mask_by": grow_mask_by,
            },
            outputs={"slot_index": 0},
        )
        return new_vae.send_request()


class BizyAir_ControlNetLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_name": (
                    [
                        "to choose",
                    ],
                ),
                "model_version_id": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = (data_types.CONTROL_NET,)
    RETURN_NAMES = ("CONTROL_NET",)
    FUNCTION = "load_controlnet"

    CATEGORY = f"{PREFIX}/loaders"

    @classmethod
    def VALIDATE_INPUTS(cls, control_net_name, model_version_id):
        if control_net_name == "to choose":
            return False
        if model_version_id is not None and model_version_id != "":
            return True
        return True

    def load_controlnet(self, control_net_name, model_version_id, **kwargs):
        if model_version_id is not None and model_version_id != "":
            control_net_name = (
                f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
            )

        node_data = create_node_data(
            class_type="ControlNetLoader",
            inputs={
                "control_net_name": control_net_name,
            },
            outputs={"slot_index": 0},
        )
        assigned_id = self.assigned_id
        node = BizyAirNodeIO(assigned_id, {assigned_id: node_data})
        return (node,)


class BizyAir_ControlNetLoader_Legacy(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_name": (folder_paths.get_filename_list("controlnet"),)
            }
        }

    RETURN_TYPES = (data_types.CONTROL_NET,)
    RETURN_NAMES = ("CONTROL_NET",)
    # 似乎不能用default实现
    FUNCTION = "load_controlnet"

    CATEGORY = f"{PREFIX}/loaders"

    def load_controlnet(self, control_net_name, **kwargs):

        node_data = create_node_data(
            class_type="ControlNetLoader",
            inputs={
                "control_net_name": control_net_name,
            },
            outputs={"slot_index": 0},
        )
        assigned_id = self.assigned_id
        node = BizyAirNodeIO(assigned_id, {assigned_id: node_data})
        return (node,)


class BizyAir_ControlNetApplyAdvanced(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "control_net": (data_types.CONTROL_NET,),
                "image": ("IMAGE",),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "start_percent": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_percent": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING, data_types.CONDITIONING)
    RETURN_NAMES = ("positive", "negative")
    # FUNCTION = "apply_controlnet"

    CATEGORY = "conditioning"

    def apply_controlnet(self, **kwargs):
        new_positive = kwargs["positive"].copy(self.assigned_id)
        new_negative = kwargs["negative"].copy(self.assigned_id)
        outs = [
            new_positive,
            new_negative,
        ]
        for slot_index, out in zip(range(0, 2), outs):
            out.add_node_data(
                class_type="ControlNetApplyAdvanced",
                inputs=kwargs,
                outputs={"slot_index": slot_index},
            )
        return outs


class BizyAir_ControlNetApply(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "control_net": (data_types.CONTROL_NET,),
                "image": ("IMAGE",),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    RETURN_NAMES = ("CONDITIONING",)
    # FUNCTION = "apply_controlnet"

    CATEGORY = f"{PREFIX}/conditioning/controlnet"

    def apply_controlnet(
        self, conditioning, control_net: BizyAirNodeIO, image, strength
    ):
        new_cond: BizyAirNodeIO = conditioning.copy(self.assigned_id)
        new_cond.add_node_data(
            class_type="ControlNetApply",
            inputs={
                "conditioning": conditioning,
                "control_net": control_net,
                "image": image,
                "strength": strength,
            },
            outputs={"slot_index": 0},
        )
        return (new_cond,)


class BizyAir_CLIPVisionLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip_name": (folder_paths.get_filename_list("clip_vision"),),
                # "clip_name": (
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

    RETURN_TYPES = ("CLIP_VISION",)
    # FUNCTION = "load_clip"

    CATEGORY = "loaders"

    def load_clip(self, clip_name):
        node_data = create_node_data(
            class_type="CLIPVisionLoader",
            inputs={"clip_name": clip_name},
            outputs={"slot_index": 0},
        )
        clip_vision = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
        return (clip_vision,)

    # @classmethod
    # def VALIDATE_INPUTS(cls, clip_name):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if clip_name == "" or clip_name is None:
    #         return False
    #     return True

    # def load_clip(self, clip_name, model_version_id=""):
    #     if model_version_id != "":
    #         # use model version id as lora name
    #         clip_name = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
    #         )
    #     node_data = create_node_data(
    #         class_type="CLIPVisionLoader",
    #         inputs={"clip_name": clip_name},
    #         outputs={"slot_index": 0},
    #     )
    #     clip_vision = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
    #     return (clip_vision,)


class VAELoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"vae_name": (folder_paths.get_filename_list("vae"),)}}
        # return {
        #     "required": {
        #         "vae_name": (
        #             [
        #                 "to choose",
        #             ],
        #         ),
        #         "model_version_id": (
        #             "STRING",
        #             {
        #                 "default": "",
        #             },
        #         ),
        #     }
        # }

    RETURN_TYPES = (data_types.VAE,)
    RETURN_NAMES = ("vae",)
    # FUNCTION = "load_vae"

    CATEGORY = "loaders"

    def load_vae(self, vae_name):
        node_data = create_node_data(
            class_type="VAELoader",
            inputs={"vae_name": vae_name},
            outputs={"slot_index": 0},
        )
        vae = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
            config_file=folder_paths.guess_config(vae_name=vae_name),
        )
        return (vae,)

    # @classmethod
    # def VALIDATE_INPUTS(cls, vae_name):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if vae_name == "" or vae_name is None:
    #         return False
    #     return True

    # def load_vae(self, vae_name, model_version_id):
    #     if model_version_id != "":
    #         # use model version id as lora name
    #         vae_name = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
    #         )
    #     node_data = create_node_data(
    #         class_type="VAELoader",
    #         inputs={"vae_name": vae_name},
    #         outputs={"slot_index": 0},
    #     )
    #     vae = BizyAirNodeIO(
    #         self.assigned_id,
    #         {self.assigned_id: node_data},
    #         config_file=folder_paths.guess_config(vae_name=vae_name),
    #     )
    #     return (vae,)


class UNETLoader(BizyAirBaseNode):
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
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e5m2"],),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    # FUNCTION = "load_unet"

    CATEGORY = "advanced/loaders"

    def load_unet(self, unet_name, weight_dtype):
        node_data = create_node_data(
            class_type="UNETLoader",
            inputs={
                "unet_name": unet_name,
                "weight_dtype": weight_dtype,
            },
            outputs={"slot_index": 0},
        )
        model = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
            config_file=folder_paths.guess_config(unet_name=unet_name),
        )
        return (model,)

    # @classmethod
    # def VALIDATE_INPUTS(cls, unet_name):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if unet_name == "" or unet_name is None:
    #         return False
    #     return True

    # def load_unet(self, unet_name, model_version_id, weight_dtype):
    #     if model_version_id != "":
    #         # use model version id as lora name
    #         unet_name = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
    #         )
    #     node_data = create_node_data(
    #         class_type="UNETLoader",
    #         inputs={
    #             "unet_name": unet_name,
    #             "weight_dtype": weight_dtype,
    #         },
    #         outputs={"slot_index": 0},
    #     )
    #     model = BizyAirNodeIO(
    #         self.assigned_id,
    #         {self.assigned_id: node_data},
    #         config_file=folder_paths.guess_config(unet_name=unet_name),
    #     )
    #     return (model,)


class SamplerCustomAdvanced(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "noise": ("NOISE",),
                "guider": ("GUIDER",),
                "sampler": ("SAMPLER",),
                "sigmas": ("SIGMAS",),
                "latent_image": ("LATENT",),
            }
        }

    RETURN_TYPES = ("LATENT", "LATENT")
    RETURN_NAMES = ("output", "denoised_output")

    # FUNCTION = "sample"

    CATEGORY = "sampling/custom_sampling"

    # def sample(self, **kwargs):
    #     guider: BizyAirNodeIO = kwargs["guider"].copy(self.assigned_id)
    #     guider.add_node_data(
    #         class_type="SamplerCustomAdvanced",
    #         inputs=kwargs,
    #         outputs={"slot_index": 0},
    #     )
    #     return (guider, None)


class BasicGuider(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "conditioning": (data_types.CONDITIONING,),
            }
        }

    RETURN_TYPES = ("GUIDER",)

    # FUNCTION = "get_guider"
    CATEGORY = "sampling/custom_sampling/guiders"

    def get_guider(self, model: BizyAirNodeIO, conditioning):
        new_model = model.copy(self.assigned_id)
        new_model.add_node_data(
            class_type="BasicGuider",
            inputs={
                "model": model,
                "conditioning": conditioning,
            },
            outputs={"slot_index": 0},
        )
        return (new_model,)


class BasicScheduler(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES,),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    CATEGORY = "sampling/custom_sampling/schedulers"

    # FUNCTION = "get_sigmas"

    def get_sigmas(self, **kwargs):
        new_model: BizyAirNodeIO = kwargs["model"].copy(self.assigned_id)
        new_model.add_node_data(
            class_type="BasicScheduler",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        return (new_model,)


class DualCLIPLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip_name1": (folder_paths.get_filename_list("clip"),),
                "clip_name2": (folder_paths.get_filename_list("clip"),),
                # "clip_name1": (
                #     [
                #         "to choose",
                #     ],
                # ),
                # "model_version_id1": (
                #     "STRING",
                #     {
                #         "default": "",
                #     },
                # ),
                # "clip_name2": (
                #     [
                #         "to choose",
                #     ],
                # ),
                # "model_version_id2": (
                #     "STRING",
                #     {
                #         "default": "",
                #     },
                # ),
                "type": (["sdxl", "sd3", "flux"],),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    # FUNCTION = "load_clip"

    CATEGORY = "advanced/loaders"

    def load_clip(self, clip_name1, clip_name2, type):
        node_data = create_node_data(
            class_type="DualCLIPLoader",
            inputs={
                "clip_name1": clip_name1,
                "clip_name2": clip_name2,
                "type": type,
            },
            outputs={"slot_index": 0},
        )
        model = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
            config_file=folder_paths.guess_config(clip_name=clip_name1),
        )
        return (model,)

    # @classmethod
    # def VALIDATE_INPUTS(cls, ckpt_name):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if ckpt_name == "" or ckpt_name is None:
    #         return False
    #     return True

    # def load_clip(
    #     self, clip_name1, model_version_id1, clip_name2, model_version_id2, type
    # ):
    #     if model_version_id1 != "":
    #         # use model version id as lora name
    #         clip_name1 = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id1}"
    #         )
    #     if model_version_id2 != "":
    #         # use model version id as lora name
    #         clip_name2 = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id2}"
    #         )
    #     node_data = create_node_data(
    #         class_type="DualCLIPLoader",
    #         inputs={
    #             "clip_name1": clip_name1,
    #             "clip_name2": clip_name2,
    #             "type": type,
    #         },
    #         outputs={"slot_index": 0},
    #     )
    #     model = BizyAirNodeIO(
    #         self.assigned_id,
    #         {self.assigned_id: node_data},
    #         config_file=folder_paths.guess_config(clip_name=clip_name1),
    #     )
    #     return (model,)


class KSamplerSelect(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sampler_name": (comfy.samplers.SAMPLER_NAMES,),
            }
        }

    RETURN_TYPES = ("SAMPLER",)
    CATEGORY = "sampling/custom_sampling/samplers"

    # FUNCTION = "get_sampler"

    def get_sampler(self, **kwargs):
        node_data = create_node_data(
            class_type="KSamplerSelect",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        model = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
        )
        return (model,)


class RandomNoise(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "noise_seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},
                ),
            }
        }

    RETURN_TYPES = ("NOISE",)
    # FUNCTION = "get_noise"
    CATEGORY = "sampling/custom_sampling/noise"

    def get_noise(self, noise_seed):
        node_data = create_node_data(
            class_type="RandomNoise",
            inputs={
                "noise_seed": noise_seed,
            },
            outputs={"slot_index": 0},
        )
        model = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
        )
        return (model,)


class CLIPSetLastLayer(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": (data_types.CLIP,),
                "stop_at_clip_layer": (
                    "INT",
                    {"default": -1, "min": -24, "max": -1, "step": 1},
                ),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    # FUNCTION = "set_last_layer"

    CATEGORY = "conditioning"

    def set_last_layer(self, clip: BizyAirNodeIO, stop_at_clip_layer):
        new_clip = clip.copy(new_node_id=self.assigned_id)
        new_clip.add_node_data(
            class_type="CLIPSetLastLayer",
            inputs={
                "stop_at_clip_layer": stop_at_clip_layer,
                "clip": clip,
            },
            outputs={"slot_index": 0},
        )
        return (new_clip,)


class InpaintModelConditioning(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "vae": (data_types.VAE,),
                "pixels": ("IMAGE",),
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING, data_types.CONDITIONING, "LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    # FUNCTION = "encode"

    CATEGORY = "conditioning/inpaint"


#  noise_mask newly added in https://github.com/comfyanonymous/ComfyUI/blob/8f0009aad0591ceee59a147738aa227187b07898/nodes.py#L385
# "noise_mask": ("BOOLEAN", {"default": False, "tooltip": "Add a noise mask to the latent so sampling will only happen within the mask. Might improve results or completely break things depending on the model."}),
class InpaintModelConditioning_v2(InpaintModelConditioning):
    CLASS_TYPE_NAME = "InpaintModelConditioning"

    @classmethod
    def INPUT_TYPES(s):
        ret = super().INPUT_TYPES()
        ret["required"]["noise_mask"] = (
            "BOOLEAN",
            {
                "default": False,
                "tooltip": "Add a noise mask to the latent so sampling will only happen within the mask. Might improve results or completely break things depending on the model.",
            },
        )
        return ret


class SharedLoraLoader(BizyAir_LoraLoader_Legacy):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "share_id": ("STRING", {"default": "share_id"}),
                "lora_name": ([],),
                "model": (data_types.MODEL,),
                "clip": (data_types.CLIP,),
                "strength_model": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
                "strength_clip": (
                    "FLOAT",
                    {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP)
    RETURN_NAMES = ("MODEL", "CLIP")
    # 似乎不能用default实现
    FUNCTION = "shared_load_lora"
    CATEGORY = f"{PREFIX}/loaders"
    NODE_DISPLAY_NAME = "Shared Lora Loader"

    @classmethod
    def VALIDATE_INPUTS(cls, share_id: str, lora_name: str):
        if lora_name in folder_paths.filename_path_mapping.get("loras", {}):
            return True

        outs = folder_paths.get_share_filename_list("loras", share_id=share_id)
        if lora_name not in outs:
            raise ValueError(
                f"Lora {lora_name} not found in share {share_id} with {outs}"
            )
        return True

    def shared_load_lora(
        self, model, clip, lora_name, strength_model, strength_clip, **kwargs
    ):
        resolved_path = folder_paths.filename_path_mapping["loras"][lora_name]
        return super().load_lora(
            model=model,
            clip=clip,
            lora_name=resolved_path,
            strength_model=strength_model,
            strength_clip=strength_clip,
        )


class ConditioningCombine(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_1": (data_types.CONDITIONING,),
                "conditioning_2": (data_types.CONDITIONING,),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "combine"
    NODE_DISPLAY_NAME = "Conditioning (Combine)"
    CATEGORY = "conditioning"


class ConditioningAverage(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_to": (data_types.CONDITIONING,),
                "conditioning_from": (data_types.CONDITIONING,),
                "conditioning_to_strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "addWeighted"
    NODE_DISPLAY_NAME = "Conditioning (Average)"
    CATEGORY = "conditioning"


class ConditioningConcat(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_to": (data_types.CONDITIONING,),
                "conditioning_from": (data_types.CONDITIONING,),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "concat"
    NODE_DISPLAY_NAME = "Conditioning (Concat)"
    CATEGORY = "conditioning"


class ConditioningSetArea(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "width": (
                    "INT",
                    {"default": 64, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "height": (
                    "INT",
                    {"default": 64, "min": 64, "max": MAX_RESOLUTION, "step": 8},
                ),
                "x": (
                    "INT",
                    {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8},
                ),
                "y": (
                    "INT",
                    {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8},
                ),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "append"
    NODE_DISPLAY_NAME = "Conditioning (Set Area)"
    CATEGORY = "conditioning"


class ConditioningSetAreaPercentage(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "width": (
                    "FLOAT",
                    {"default": 1.0, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "height": (
                    "FLOAT",
                    {"default": 1.0, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "x": ("FLOAT", {"default": 0, "min": 0, "max": 1.0, "step": 0.01}),
                "y": ("FLOAT", {"default": 0, "min": 0, "max": 1.0, "step": 0.01}),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "append"
    NODE_DISPLAY_NAME = "Conditioning (Set Area with Percentage)"
    CATEGORY = "conditioning"


class ConditioningSetMask(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "mask": ("MASK",),
                "strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "set_cond_area": (["default", "mask bounds"],),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "append"
    NODE_DISPLAY_NAME = "Conditioning (Set Mask)"
    CATEGORY = "conditioning"


class ConditioningZeroOut(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"conditioning": (data_types.CONDITIONING,)}}

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "zero_out"

    CATEGORY = "advanced/conditioning"


class ConditioningSetTimestepRange(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "start": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "set_range"

    CATEGORY = "advanced/conditioning"


class SharedControlNetLoader(BizyAir_ControlNetLoader_Legacy):
    @classmethod
    def INPUT_TYPES(s):
        ret = super().INPUT_TYPES()
        ret["required"]["share_id"] = ("STRING", {"default": "share_id"})
        return ret

    NODE_DISPLAY_NAME = "Shared Load ControlNet Model"

    @classmethod
    def VALIDATE_INPUTS(cls, share_id: str, control_net_name: str):
        if control_net_name in folder_paths.filename_path_mapping.get("controlnet", {}):
            return True

        outs = folder_paths.get_share_filename_list("controlnet", share_id=share_id)
        if control_net_name not in outs:
            raise ValueError(
                f"ControlNet {control_net_name} not found in share {share_id} with {outs}"
            )

        return True

    def load_controlnet(self, control_net_name, share_id, **kwargs):
        resolved_path = folder_paths.filename_path_mapping["controlnet"][
            control_net_name
        ]
        return super().load_controlnet(control_net_name=resolved_path, **kwargs)


class CLIPVisionEncode(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"clip_vision": ("CLIP_VISION",), "image": ("IMAGE",)}}

    RETURN_TYPES = ("CLIP_VISION_OUTPUT",)
    # FUNCTION = "encode"

    CATEGORY = "conditioning"


class StyleModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "style_model_name": (folder_paths.get_filename_list("style_models"),)
                # "style_model_name": (
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

    RETURN_TYPES = (data_types.STYLE_MODEL,)
    # FUNCTION = "load_style_model"

    CATEGORY = "loaders"


class StyleModelApply(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "style_model": (data_types.STYLE_MODEL,),
                "clip_vision_output": ("CLIP_VISION_OUTPUT",),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "apply_stylemodel"

    CATEGORY = "conditioning/style_model"


# 仅用于使用meta传参，故没有输入输出
class PassParameter(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {}

    RETURN_TYPES = ()

    CATEGORY = "☁️BizyAir"
