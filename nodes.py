import os
from typing import List

import comfy
from bizyair import BizyAirBaseNode, BizyAirNodeIO, create_node_data, data_types
from bizyair.path_utils import path_manager as folder_paths

LOGO = "☁️"
PREFIX = f"{LOGO}BizyAir"


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
    FUNCTION = "sample"
    RETURN_NAMES = (f"LATENT",)
    CATEGORY = f"{PREFIX}/sampling"

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
    FUNCTION = "sample"

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
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
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

    def load_checkpoint(self, ckpt_name):
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
    FUNCTION = "encode"

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
    FUNCTION = "decode"

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
        if isinstance(samples, BizyAirNodeIO) and samples.configs:
            new_vae.configs = samples.configs
        return new_vae.send_request()


class BizyAir_LoraLoader(BizyAirBaseNode):
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

    def load_lora(self, model, clip, lora_name, strength_model, strength_clip):
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
    FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent"

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
    FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent/inpaint"

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
                "control_net_name": (folder_paths.get_filename_list("controlnet"),)
            }
        }

    RETURN_TYPES = (data_types.CONTROL_NET,)
    RETURN_NAMES = ("CONTROL_NET",)
    FUNCTION = "load_controlnet"

    CATEGORY = f"{PREFIX}/loaders"

    def load_controlnet(self, control_net_name):

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
    FUNCTION = "apply_controlnet"

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
    FUNCTION = "apply_controlnet"

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
            }
        }

    RETURN_TYPES = ("CLIP_VISION",)
    FUNCTION = "load_clip"

    CATEGORY = "loaders"

    def load_clip(self, clip_name):
        node_data = create_node_data(
            class_type="CLIPVisionLoader",
            inputs={"clip_name": clip_name},
            outputs={"slot_index": 0},
        )
        clip_vision = BizyAirNodeIO(self.assigned_id, {self.assigned_id: node_data})
        return (clip_vision,)


class VAELoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"vae_name": (folder_paths.get_filename_list("vae"),)}}

    RETURN_TYPES = (data_types.VAE,)
    RETURN_NAMES = ("vae",)
    FUNCTION = "load_vae"

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


class UNETLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("unet"),),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e5m2"],),
            }
        }

    RETURN_TYPES = (data_types.MODEL,)
    FUNCTION = "load_unet"

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

    FUNCTION = "sample"

    CATEGORY = "sampling/custom_sampling"

    def sample(self, **kwargs):
        guider: BizyAirNodeIO = kwargs["guider"].copy(self.assigned_id)
        guider.add_node_data(
            class_type="SamplerCustomAdvanced",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        return (guider, None)


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

    FUNCTION = "get_guider"
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

    FUNCTION = "get_sigmas"

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
                "type": (["sdxl", "sd3", "flux"],),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    FUNCTION = "load_clip"

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

    FUNCTION = "get_sampler"

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
    FUNCTION = "get_noise"
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
    FUNCTION = "set_last_layer"

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

    def append(self, conditioning: BizyAirNodeIO, guidance):
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
