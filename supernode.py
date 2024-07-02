import os

from .utils import decode_and_deserialize, send_post_request, serialize_and_encode

COMFYAIR_SERVER_ADDRESS = os.getenv(
    "COMFYAIR_SERVER_ADDRESS", "https://api.siliconflow.cn"
)


class SuperResolution:
    API_URL = f"{COMFYAIR_SERVER_ADDRESS}/supernode/superresolution"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),
                "scale": (["2x", "4x"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "super_resolution"

    CATEGORY = "ComfyAir"

    def super_resolution(self, image, scale="2x", API_KEY=""):
        _, w, h, c = image.shape
        assert (
            w <= 512 and h <= 512
        ), f"width and height must be less than 512, but got {w} and {h}"

        # support RGB mode only now
        image = image[:, :, :, :3]

        payload = {
            "scale": scale,
            "is_compress": True,
            "image": None,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image, compress = serialize_and_encode(image, compress=True)
        payload["image"] = input_image
        payload["is_compress"] = compress

        response = send_post_request(self.API_URL, payload=payload, headers=headers)
        image = decode_and_deserialize(response.text)

        return (image,)


class RemoveBackground:
    API_URL = f"{COMFYAIR_SERVER_ADDRESS}/supernode/removebg"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "remove_background"

    CATEGORY = "ComfyAir"

    def remove_background(self, image, API_KEY=""):
        _, w, h, _ = image.shape
        assert (
            w <= 1024 and h <= 1024
        ), f"width and height must be less than 1024, but got {w} and {h}"

        payload = {
            "is_compress": True,
            "image": None,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        input_image, compress = serialize_and_encode(image, compress=True)
        payload["image"] = input_image
        payload["is_compress"] = compress

        response = send_post_request(self.API_URL, payload=payload, headers=headers)
        tensors = decode_and_deserialize(response.text)

        return (tensors["images"], tensors["mask"])


class GenerateLightningImage:
    API_URL = f"{COMFYAIR_SERVER_ADDRESS}/supernode/realvis4lightning"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "seed": ("INT", {"default": 1, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "width": ("INT", {"default": 1024, "min": 16, "max": 1024, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 16, "max": 1024, "step": 8}),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 1.5,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
                "API_KEY": ("STRING", {"default": "YOUR_API_KEY"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    CATEGORY = "ComfyAir"

    def generate_image(self, prompt, seed, width, height, cfg, batch_size, API_KEY=""):
        assert (
            width <= 1024 and height <= 1024
        ), f"width and height must be less than 1024, but got {width} and {height}"

        payload = {
            "batch_size": batch_size,
            "width": width,
            "height": height,
            "prompt": prompt,
            "cfg": cfg,
            "seed": seed,
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }

        response = send_post_request(self.API_URL, payload=payload, headers=headers)
        tensors = decode_and_deserialize(response.text)

        return (tensors,)


NODE_CLASS_MAPPINGS = {
    "ComfyAirSuperResolution": SuperResolution,
    "ComfyAirRemoveBackground": RemoveBackground,
    "ComfyAirGenerateLightningImage": GenerateLightningImage,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyAirSuperResolution": "ComfyAir Super Resolution",
    "ComfyAirRemoveBackground": "ComfyAir Remove Background",
    "ComfyAirGenerateLightningImage": "Generate Lightning Image",
}
