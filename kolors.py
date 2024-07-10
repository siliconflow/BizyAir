import copy
import os


import numpy as np
import torch


from .utils import (
    decode_and_deserialize,
    send_post_request,
    serialize_and_encode,
    get_api_key,
)

BIZYAIR_SERVER_ADDRESS = os.getenv(
    "BIZYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


class BizyAirKolorsTextEncode:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/kolorschatglm"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "",}),
                "negative_prompt": ("STRING", {"multiline": True, "default": "",}),
                "num_images_per_prompt": (
                    "INT",
                    {"default": 1, "min": 1, "max": 2, "step": 1},
                ),
            },
        }

    RETURN_TYPES = ("KOLORS_EMBEDS",)
    RETURN_NAMES = ("kolors_embeds",)
    FUNCTION = "encode"
    CATEGORY = "BizyAir/Kolors"

    def encode(self, prompt, negative_prompt, num_images_per_prompt):
        API_KEY = get_api_key()
        split_pos_text = prompt.split("|")
        split_neg_text = negative_prompt.split("|")
        assert (
            len(split_pos_text) <= 2 and len(split_neg_text) <= 2
        ), f"number of prompts must be less than 2, but got {len(split_pos_text)} and {len(split_neg_text)}, reduce the '|' symbol"

        payload = {
            "positive_prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_images_per_prompt": num_images_per_prompt,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        kolors_embeds = decode_and_deserialize(response)
        for k, v in kolors_embeds.items():
            kolors_embeds[k] = torch.from_numpy(v)
        return (kolors_embeds,)


class BizyAirKolorsVAEEncode:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/kolorsvaeencode"

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"pixels": ("IMAGE",),}}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"

    CATEGORY = "BizyAir/Kolors"

    def encode(self, pixels):
        API_KEY = get_api_key()
        device = pixels.device
        payload = {
            "images": None,
            "is_compress": True,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        np_pixels = copy.deepcopy(pixels)
        np_pixels = np_pixels.cpu().detach().numpy()
        images, compress = serialize_and_encode(np_pixels, compress=True)
        payload["images"] = images
        payload["is_compress"] = compress
        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        samples = decode_and_deserialize(response)
        for k, v in samples.items():
            samples[k] = torch.from_numpy(v)
            samples[k] = samples[k].to(device=device)
        print("yaochi debug, what you pass is ", type(samples))
        return (samples,)


class BizyAirKolorsVAEDecode:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/kolorsvaedecode"

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"samples": ("LATENT",),}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"

    CATEGORY = "BizyAir/Kolors"

    def decode(self, samples):
        API_KEY = get_api_key()

        payload = {
            "samples": None,
            "is_compress": True,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        for k, v in samples.items():
            if hasattr(v, "cpu"):
                samples[k] = v.cpu().detach().numpy()
        input_samples, compress = serialize_and_encode(samples, compress=True)
        payload["samples"] = input_samples

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        images = decode_and_deserialize(response)
        return (images,)


class BizyAirKolorsSampler:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/kolorssampler"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "kolors_embeds": ("KOLORS_EMBEDS",),
                "width": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 64}),
                "height": (
                    "INT",
                    {"default": 1024, "min": 64, "max": 2048, "step": 64},
                ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "steps": ("INT", {"default": 25, "min": 1, "max": 35, "step": 1}),
                "cfg": (
                    "FLOAT",
                    {"default": 5.0, "min": 0.0, "max": 20.0, "step": 0.01},
                ),
                "scheduler": (
                    [
                        "EulerDiscreteScheduler",
                        "EulerAncestralDiscreteScheduler",
                        "DPMSolverMultistepScheduler",
                        "DPMSolverMultistepScheduler_SDE_karras",
                        "UniPCMultistepScheduler",
                        "DEISMultistepScheduler",
                    ],
                    {"default": "EulerDiscreteScheduler"},
                ),
            },
            "optional": {
                "latent": ("LATENT",),
                "denoise_strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    FUNCTION = "process"
    CATEGORY = "BizyAir/Kolors"

    def process(
        self,
        kolors_embeds,
        width,
        height,
        seed,
        steps,
        cfg,
        scheduler,
        latent=None,
        denoise_strength=1.0,
    ):
        API_KEY = get_api_key()
        device = None
        for _, v in kolors_embeds.items():
            device = v.device
            break
        API_KEY = get_api_key()

        payload = {
            "width": width,
            "height": height,
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "scheduler": scheduler,
            "denoise_strength": denoise_strength,
            "inputs": None,
            "is_compress": True,
        }

        # convert the tensors to numpy array
        np_kolors_embeds = copy.deepcopy(kolors_embeds)
        np_latent = copy.deepcopy(latent) if latent is not None else None
        for k, v in np_kolors_embeds.items():
            if hasattr(v, "cpu"):
                np_kolors_embeds[k] = v.cpu().detach().numpy()
        if np_latent is not None:
            for k, v in latent.items():
                if hasattr(v, "cpu"):
                    np_latent[k] = v.cpu().detach().numpy()
        inputs_dict, is_compress = serialize_and_encode(
            {"kolors_embeddings": np_kolors_embeds, "latent": np_latent}, compress=True
        )

        payload["inputs"] = inputs_dict
        payload["is_compress"] = is_compress
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }

        response: str = send_post_request(
            self.API_URL, payload=payload, headers=headers
        )
        latent_out = decode_and_deserialize(response)
        for k, v in latent_out.items():
            latent_out[k] = torch.from_numpy(v).to(device=device)

        return (latent_out,)


NODE_CLASS_MAPPINGS = {
    "BizyAirKolorsTextEncode": BizyAirKolorsTextEncode,
    "BizyAirKolorsVAEEncode": BizyAirKolorsVAEEncode,
    "BizyAirKolorsVAEDecode": BizyAirKolorsVAEDecode,
    "BizyAirKolorsSampler": BizyAirKolorsSampler,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirKolorsTextEncode": "☁️BizyAir KolorsTextEncode",
    "BizyAirKolorsVAEEncode": "☁️BizyAir KolorsVAEEecode",
    "BizyAirKolorsVAEDecode": "☁️BizyAir KolorsVAEDecode",
    "BizyAirKolorsSampler": "☁️BizyAir KolorsSampler",
}
