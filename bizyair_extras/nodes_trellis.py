import os

import folder_paths
import requests
import torch

from bizyair import BizyAirBaseNode


class BizyAir_IF_TrellisCheckpointLoader(BizyAirBaseNode):
    """
    Node to manage the loading of the TRELLIS model.
    Follows ComfyUI conventions for model management.
    """

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types with device-specific options."""
        device_options = []
        if torch.cuda.is_available():
            device_options.append("cuda")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device_options.append("mps")
        device_options.append("cpu")

        return {
            "required": {
                "model_name": (["TRELLIS-image-large"],),
                "dinov2_model": (
                    ["dinov2_vitl14_reg", "dinov2_vitg14_reg"],
                    {
                        "default": "dinov2_vitl14_reg",
                        "tooltip": "Select the Dinov2 model to use for the image to 3D conversion. Smaller models work but better results with larger models.",
                    },
                ),
                "use_fp16": ("BOOLEAN", {"default": True}),
                "attn_backend": (
                    ["sage", "xformers", "flash_attn", "sdpa", "naive"],
                    {
                        "default": "sage",
                        "tooltip": "Select the attention backend to use for the image to 3D conversion. Sage is experimental but faster",
                    },
                ),
                "smooth_k": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Smooth k for sage attention. This is a hyperparameter that controls the smoothness of the attention distribution. It is a boolean value that determines whether to use smooth k or not. Smooth k is a hyperparameter that controls the smoothness of the attention distribution. It is a boolean value that determines whether to use smooth k or not.",
                    },
                ),
                "spconv_algo": (
                    ["implicit_gemm", "native"],
                    {
                        "default": "implicit_gemm",
                        "tooltip": "Select the spconv algorithm to use for the image to 3D conversion. Implicit gemm is the best but slower. Native is the fastest but less accurate.",
                    },
                ),
                "main_device": (device_options, {"default": device_options[0]}),
            },
        }

    RETURN_TYPES = ("TRELLIS_MODEL",)
    RETURN_NAMES = ("model",)
    CATEGORY = "☁️BizyAir/Trellis"
    NODE_DISPLAY_NAME = "☁️BizyAir Load Trellis"


class BizyAir_IF_TrellisImageTo3D(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("TRELLIS_MODEL",),
                "mode": (
                    ["single", "multi"],
                    {
                        "default": "single",
                        "tooltip": "Mode. single is a single image. with multi you can provide multiple reference angles for the 3D model",
                    },
                ),
                "images": ("IMAGE", {"list": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0x7FFFFFFF}),
                "ss_guidance_strength": (
                    "FLOAT",
                    {"default": 7.5, "min": 0.0, "max": 12.0, "step": 0.1},
                ),
                "ss_sampling_steps": ("INT", {"default": 12, "min": 1, "max": 100}),
                "slat_guidance_strength": (
                    "FLOAT",
                    {"default": 3.0, "min": 0.0, "max": 12.0, "step": 0.1},
                ),
                "slat_sampling_steps": ("INT", {"default": 12, "min": 1, "max": 100}),
                "multimode": (
                    ["stochastic", "multidiffusion"],
                    {"default": "stochastic"},
                ),
            },
            "optional": {
                "masks": ("MASK", {"list": True}),
            },
        }

    RETURN_TYPES = (
        "trellis_gaussian",
        "trellis_mesh",
    )
    CATEGORY = "☁️BizyAir/Trellis"
    NODE_DISPLAY_NAME = "☁️BizyAir Trellis Predict"
    OUTPUT_NODE = True


class BizyAir_Trans3D2Video(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trellis_gaussian": ("trellis_gaussian", {"forceInput": True}),
                "trellis_mesh": ("trellis_mesh", {"forceInput": True}),
                "fps": (
                    "INT",
                    {
                        "default": 15,
                        "min": 1,
                        "max": 60,
                        "tooltip": "FPS. the higher the value the smoother the video will be",
                    },
                ),
                "render_video": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Render a video"},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/Trellis"
    NODE_DISPLAY_NAME = "☁️BizyAir Render Video With Trellis"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)


class BizyAir_Trans3D2GlbFile(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trellis_gaussian": ("trellis_gaussian", {"forceInput": True}),
                "trellis_mesh": ("trellis_mesh", {"forceInput": True}),
                "mesh_simplify": (
                    "FLOAT",
                    {
                        "default": 0.95,
                        "min": 0.9,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Simplify the mesh. the lower the value more polygons the mesh will have",
                    },
                ),
                "texture_size": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 512,
                        "max": 2048,
                        "step": 512,
                        "tooltip": "Texture size. the higher the value the more detailed the texture will be",
                    },
                ),
                "texture_mode": (
                    ["blank", "fast", "opt"],
                    {
                        "default": "fast",
                        "tooltip": "Texture mode. blank is no texture. fast is a fast texture. opt is a high quality texture",
                    },
                ),
                "save_glb": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Save the GLB file this is the 3D model",
                    },
                ),
                "save_texture": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Save the texture file"},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/Trellis"
    NODE_DISPLAY_NAME = "☁️BizyAir Generate Glb With Trellis"
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("url", "texture_image")


class BizyAir_Trans3D2Gaussian(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trellis_gaussian": ("trellis_gaussian", {"forceInput": True}),
                "save_gaussian": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Save the Gaussian file this is a ply file of the 3D model",
                    },
                ),
            }
        }

    CATEGORY = "☁️BizyAir/Trellis"
    NODE_DISPLAY_NAME = "☁️BizyAir Generate Gaussian With Trellis"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)


class BizyAirDownloadFile(BizyAirBaseNode):
    NODE_DISPLAY_NAME = "☁️BizyAir Download File"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
                "project_name": ("STRING", {"default": "trellis_output"}),
            }
        }

    CATEGORY = "☁️BizyAir/Trellis"
    FUNCTION = "main"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (False,)
    # RETURN_NAMES = ("gaussian_path",)

    def main(self, url, project_name):
        assert url is not None
        print(f"why (chuan) url: {url}")
        file_name = os.path.basename(url)
        out_dir = os.path.join(folder_paths.get_output_directory(), project_name)
        os.makedirs(out_dir, exist_ok=True)
        local_path = os.path.join(out_dir, file_name)
        output = os.path.join(project_name, file_name)
        print("why download: ", local_path)
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_path, "wb") as file:
                file.write(response.content)
            print("download finished!")
        else:
            print(f"download error: {response.status_code}")
        print("output: ", output)
        return (output,)
