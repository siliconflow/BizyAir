import requests
import comfy
import folder_paths
from .register import register_node
from .image_utils import (
    encode_data,
    decode_data,
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


@register_node()
class BizyAir_KSampler:
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
        new_model: BizyAirNodeIO = model.copy()
        node_data = create_node_data(
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

        node_data = encode_data(node_data)
        new_model.nodes.update(**{new_model.node_id: node_data})
        if isinstance(positive, BizyAirNodeIO):
            new_model.nodes.update(**positive.nodes)
        if isinstance(negative, BizyAirNodeIO):
            new_model.nodes.update(**negative.nodes)

        if new_model.request_mode == "batch":
            return (new_model,)

        response = requests.post(
            url,
            headers=headers,
            json={"workflow": new_model.nodes, "last_link_id": new_model.node_id,},
        )
        out = response.json()["data"]["payload"]
        real_out = decode_data(out)
        return real_out[0]


@register_node(f"{PREFIX} Load Checkpoint")
class BizyAir_CheckpointLoaderSimple:
    @classmethod
    def INPUT_TYPES(s):  # TODO fix ckpt_name
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
                "request_mode": (["batch", "instant"],),
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

    def load_checkpoint(self, ckpt_name, request_mode="batch"):
        #  request_mode: A tuple containing the modes of data processing.
        #  "batch" for processing all data at once,
        #  "instant" for processing data as it comes.

        node_datas = [
            create_node_data(
                class_type="CheckpointLoaderSimple",
                inputs={"ckpt_name": ckpt_name},
                outputs={"slot_index": slot_index},
            )
            for slot_index in range(3)
        ]
        outs = [
            BizyAirNodeIO("0", {"0": data}, request_mode=request_mode)
            for data in node_datas
        ]

        return (
            outs[0],
            outs[1],
            outs[2],
        )


@register_node(f"{PREFIX} CLIP Text Encode (Prompt)")
class BizyAir_CLIPTextEncode:
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
        new_clip = clip.copy()

        node_data = create_node_data(
            class_type="CLIPTextEncode",
            inputs={"text": text, "clip": clip,},
            outputs={"slot_index": 0},
        )

        node_data = encode_data(node_data)
        new_clip.nodes.update(**{new_clip.node_id: node_data})
        return (new_clip,)


@register_node()
class BizyAir_VAEDecode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"samples": ("LATENT",), "vae": (data_types.VAE,)}}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = (f"IMAGE{landing_emojis}",)
    FUNCTION = "decode"

    CATEGORY = f"{PREFIX}/latent"

    def decode(self, vae, samples):
        new_vae: BizyAirNodeIO = vae.copy()

        node_data = create_node_data(
            class_type="VAEDecode",
            inputs={"samples": samples, "vae": vae,},
            outputs={"slot_index": 0},
        )
        node_data = encode_data(node_data)
        new_vae.nodes.update(**{new_vae.node_id: node_data})
        if isinstance(samples, BizyAirNodeIO):
            new_vae.nodes.update(**samples.nodes)

        response = requests.post(
            url,
            headers=headers,
            json={"workflow": new_vae.nodes, "last_link_id": new_vae.node_id},
        )
        # local
        out = response.json()["data"]["payload"]
        real_out = decode_data(out)
        return real_out[0]


@register_node()
class BizyAir_LoraLoader:
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
        new_model: BizyAirNodeIO = model.copy()
        new_clip: BizyAirNodeIO = clip.copy(new_model.node_id)
        model_node_data, clip_node_data = [
            create_node_data(
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
            for slot_index in range(2)
        ]
        model_node_data, clip_node_data = (
            encode_data(model_node_data),
            encode_data(clip_node_data),
        )
        new_clip.nodes.update(**{new_clip.node_id: clip_node_data})
        new_model.nodes.update(**{new_model.node_id: model_node_data})
        return (
            new_model,
            new_clip,
        )


@register_node()
class BizyAir_VAEEncode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"pixels": ("IMAGE",), "vae": (data_types.VAE,)}}

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = (f"LATENT{landing_emojis}",)
    FUNCTION = "encode"
    CATEGORY = f"{PREFIX}/latent"

    def encode(self, vae, pixels):
        new_vae: BizyAirNodeIO = vae.copy()
        node_data = create_node_data(
            class_type="VAEEncode",
            inputs={"vae": vae, "pixels": pixels,},
            outputs={"slot_index": 0},
        )
        node_data = encode_data(node_data)

        new_vae.nodes.update(**{new_vae.node_id: node_data})

        response = requests.post(
            url,
            headers=headers,
            json={"workflow": new_vae.nodes, "last_link_id": new_vae.node_id},
        )
        # local
        out = response.json()["data"]["payload"]
        real_out = decode_data(out)
        return real_out[0]


@register_node()
class BizyAir_VAEEncodeForInpaint:
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
        new_vae: BizyAirNodeIO = vae.copy()
        node_data = create_node_data(
            class_type="VAEEncodeForInpaint",
            inputs={
                "vae": vae,
                "pixels": pixels,
                "mask": mask,
                "grow_mask_by": grow_mask_by,
            },
            outputs={"slot_index": 0},
        )
        node_data = encode_data(node_data)

        new_vae.nodes.update(**{new_vae.node_id: node_data})

        response = requests.post(
            url,
            headers=headers,
            json={"workflow": new_vae.nodes, "last_link_id": new_vae.node_id},
        )
        # local
        out = response.json()["data"]["payload"]
        real_out = decode_data(out)
        return real_out[0]


@register_node()
class BizyAir_ControlNetLoader:
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
            inputs={"control_net_name": control_net_name,},
            outputs={"slot_index": 0},
        )
        node = BizyAirNodeIO("1", {"1": node_data})
        return (node,)


@register_node(f"{PREFIX} Apply ControlNet")
class BizyAir_ControlNetApply:
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
        new_cond: BizyAirNodeIO = conditioning.copy()
        node_data = create_node_data(
            class_type="ControlNetApply",
            inputs={
                "conditioning": conditioning,
                "control_net": control_net,
                "image": image,
                "strength": strength,
            },
            outputs={"slot_index": 0},
        )
        node_data = encode_data(node_data)

        new_cond.nodes.update(**control_net.nodes)
        new_cond.nodes.update(**{new_cond.node_id: node_data})
        return (new_cond,)
