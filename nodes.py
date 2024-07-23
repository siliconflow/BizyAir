import os
from typing import List
import comfy
import folder_paths
from .register import BizyAirBaseNode
from .image_utils import (
    create_node_data,
    BizyAirNodeIO,
)
from . import data_types

LOGO = "☁️"
PREFIX = f"{LOGO}BizyAir"
take_off_emojis = "🛫"
landing_emojis = "🛬"
url = "http://0.0.0.0:8000/supernode/diffusers-v1-comfy-server-demo"
headers = {"Content-Type": "application/json"}


class BizyAir_KSampler(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF},),
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
    RETURN_NAMES = (f"LATENT{landing_emojis}",)
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

        return new_model.send_request(url=url, headers=headers)


class BizyAir_CheckpointLoaderSimple(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (["Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",],),
            }
        }

    RETURN_TYPES = (data_types.MODEL, data_types.CLIP, data_types.VAE)
    FUNCTION = "load_checkpoint"
    CATEGORY = f"{PREFIX}/loaders"
    RETURN_NAMES = (
        f"model{take_off_emojis}",
        f"clip{take_off_emojis}",
        f"vae{take_off_emojis}",
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
        current_directory = os.path.dirname(__file__)
        config_file = os.path.join(current_directory, "config", "sdxl_config.yaml")
        assigned_id = self.assigned_id
        outs = [
            BizyAirNodeIO(assigned_id, {assigned_id: data}, config_file=config_file,)
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
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True},),
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
            inputs={"text": text, "clip": clip,},
            outputs={"slot_index": 0},
        )
        return (new_clip,)


class BizyAir_VAEDecode(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"samples": ("LATENT",), "vae": (data_types.VAE,)}}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (f"IMAGE{landing_emojis}",)
    FUNCTION = "decode"

    CATEGORY = f"{PREFIX}/latent"

    def decode(self, vae, samples):
        new_vae: BizyAirNodeIO = vae.copy(self.assigned_id)
        new_vae.add_node_data(
            class_type="VAEDecode",
            inputs={"samples": samples, "vae": vae,},
            outputs={"slot_index": 0},
        )
        return new_vae.send_request(url=url, headers=headers)


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
    RETURN_NAMES = (f"LATENT{landing_emojis}",)
    FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent"

    def encode(self, vae, pixels):
        new_vae: BizyAirNodeIO = vae.copy(self.assigned_id)
        new_vae.add_node_data(
            class_type="VAEEncode",
            inputs={"vae": vae, "pixels": pixels,},
            outputs={"slot_index": 0},
        )
        return new_vae.send_request(url=url, headers=headers)


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
    RETURN_NAMES = (f"LATENT{landing_emojis}",)
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
        return new_vae.send_request(url, headers)


class BizyAir_ControlNetLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_name": (["diffusion_pytorch_model_promax.safetensors"],)
            }
        }

    RETURN_TYPES = (data_types.CONTROL_NET,)
    RETURN_NAMES = ("CONTROL_NET",)
    FUNCTION = "load_controlnet"

    CATEGORY = f"{PREFIX}/loaders"

    def load_controlnet(self, control_net_name):

        node_data = create_node_data(
            class_type="ControlNetLoader",
            inputs={"control_net_name": control_net_name,},
            outputs={"slot_index": 0},
        )
        assigned_id = self.assigned_id
        node = BizyAirNodeIO(assigned_id, {assigned_id: node_data})
        return (node,)


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
    RETURN_NAMES = ("CONTROL_NET",)
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
            "required": {"clip_name": (folder_paths.get_filename_list("clip_vision"),),}
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
