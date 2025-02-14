import os
import uuid

import folder_paths
import requests
import torch
import trimesh

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
                "ss_sampling_steps": ("INT", {"default": 12, "min": 1, "max": 50}),
                "slat_guidance_strength": (
                    "FLOAT",
                    {"default": 3.0, "min": 0.0, "max": 12.0, "step": 0.1},
                ),
                "slat_sampling_steps": ("INT", {"default": 12, "min": 1, "max": 50}),
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


class BizyAirDownloadFile(BizyAirBaseNode):
    NODE_DISPLAY_NAME = "☁️BizyAir Download File"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
                "filename_prefix": ("STRING", {"default": "default"}),
                "type": (
                    ["glb", "obj"],
                    {
                        "default": "glb",
                        "tooltip": "Mode. single is a single image. with multi you can provide multiple reference angles for the 3D model",
                    },
                ),
            }
        }

    CATEGORY = "☁️BizyAir/Trellis"
    FUNCTION = "main"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (False,)

    def main(self, url, filename_prefix):
        assert url is not None
        # file_glb = file_name + ".glb"
        # file_obj = file_name + ".obj"
        out_glb_dir = os.path.join(
            folder_paths.get_output_directory(), "trellis_output"
        )
        out_obj_dir = os.path.join(out_glb_dir, "obj")
        os.makedirs(out_glb_dir, exist_ok=True)
        os.makedirs(out_obj_dir, exist_ok=True)
        glb_output_folder, _, glb_counter, _, _ = folder_paths.get_save_image_path(
            filename_prefix, out_glb_dir
        )
        obj_output_folder, _, obj_counter, _, _ = folder_paths.get_save_image_path(
            filename_prefix, out_obj_dir
        )
        file_glb = f"{filename_prefix}_{glb_counter:05}_.glb"
        file_obj = f"{filename_prefix}_{obj_counter:05}_.obj"
        local_glb = os.path.join(glb_output_folder, file_glb)
        local_obj = os.path.join(obj_output_folder, file_obj)
        output = os.path.join("trellis_output", file_glb)
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_glb, "wb") as file:
                file.write(response.content)
            print("download finished in {}".format(local_glb))
            # load GLB 文件
            mesh = trimesh.load(local_glb)
            # export OBJ（include .obj 和 .mtl file）
            mesh.export(local_obj, include_texture=True, file_type="obj")

            current_mtl_filename = os.path.join(obj_output_folder, "material.mtl")
            mtl_filename = os.path.join(
                obj_output_folder, f"{filename_prefix}_{glb_counter:05}_.mtl"
            )
            if os.path.exists(current_mtl_filename):
                os.rename(current_mtl_filename, mtl_filename)  # 重命名材质文件

            # 获取纹理文件路径，可能需要重命名它
            current_png_filename = os.path.join(
                obj_output_folder, "material_0.png"
            )  # 默认生成的纹理文件名
            png_filename = os.path.join(
                obj_output_folder, f"{filename_prefix}_{glb_counter:05}_.png"
            )
            if os.path.exists(current_png_filename):
                os.rename(current_png_filename, png_filename)  # 重命名纹理文件

            print(f"Transform success! obj file is stored in {local_obj}")
        else:
            print(f"download error: {response.status_code}")

        return (output,)

    @classmethod
    def IS_CHANGED(self, url, file_name):
        return uuid.uuid4().hex
