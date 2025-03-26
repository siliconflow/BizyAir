"""
Reference: https://github.com/logtd/ComfyUI-Fluxtapoz
"""

# from bizyair import BizyAirBaseNode, data_types
import folder_paths
import nodes
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, create_node_data, data_types


class BizyAir_OutFluxModelSamplingPred(BizyAirBaseNode):
    DESCRIPTION = ""
    RETURN_TYPES = (data_types.MODEL,)
    NODE_DISPLAY_NAME = "☁️BizyAir Outverse Flux Model Pred"
    CATEGORY = "☁️BizyAir/sampling/custom_sampling/samplers"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "max_shift": (
                    "FLOAT",
                    {"default": 1.15, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "base_shift": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "width": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
                "reverse_ode": ("BOOLEAN", {"default": False}),
            }
        }


class BizyAir_InFluxModelSamplingPred(BizyAirBaseNode):
    RETURN_TYPES = (data_types.MODEL,)
    CATEGORY = "☁️BizyAir/sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "☁️BizyAir Inverse Flux Model Pred"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "max_shift": (
                    "FLOAT",
                    {"default": 1.15, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "base_shift": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "width": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 8,
                    },
                ),
            }
        }


class BizyAir_FluxForwardODESampler(BizyAirBaseNode):
    RETURN_TYPES = ("SAMPLER",)
    # FUNCTION = "build"
    CATEGORY = "☁️BizyAir/sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "☁️BizyAir Flux Forward ODE Sampler"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "gamma": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
        }


class BizyAir_FluxReverseODESampler(BizyAirBaseNode):
    RETURN_TYPES = ("SAMPLER",)
    # FUNCTION = "build"
    CATEGORY = "☁️BizyAir/sampling/custom_sampling/samplers"
    NODE_DISPLAY_NAME = "☁️BizyAir Flux Reverse ODE Sampler"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (data_types.MODEL,),
                "latent_image": ("LATENT",),
                "eta": (
                    "FLOAT",
                    {"default": 0.8, "min": 0.0, "max": 100.0, "step": 0.01},
                ),
                "start_step": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "end_step": ("INT", {"default": 5, "min": 0, "max": 1000, "step": 1}),
            },
            "optional": {
                "eta_trend": (["constant", "linear_increase", "linear_decrease"],)
            },
        }


class BizyAir_FluxDeGuidance(BizyAirBaseNode):

    RETURN_TYPES = (data_types.CONDITIONING,)
    # FUNCTION = "append"

    CATEGORY = "☁️BizyAir/fluxtapoz"
    NODE_DISPLAY_NAME = "☁️BizyAir Flux DeGuidance"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": (data_types.CONDITIONING,),
                "guidance": (
                    "FLOAT",
                    {"default": 3.5, "min": -100.0, "max": 100.0, "step": 0.1},
                ),
            }
        }


class BizyAir_QuantizeDualCLIPLoaderOffline(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip_name1": (folder_paths.get_filename_list("clip"),),
                "clip_name2": (folder_paths.get_filename_list("clip"),),
                "type": (["flux"],),
            }
        }

    RETURN_TYPES = (data_types.CLIP,)
    FUNCTION = "load_clip"

    CATEGORY = "advanced/loaders"

    def load_clip(self, clip_name1, clip_name2, type):

        node_data = create_node_data(
            class_type="QuantizeDualCLIPLoaderOffline",
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
            # config_file=folder_paths.guess_config(clip_name=clip_name1),
        )
        return (model,)


class OneDiffLoadOptimizedDiffusionModel(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("diffusion_models"),),
                "max_num_loras": (
                    "INT",
                    {
                        "default": 3,
                        "step": 1,
                        "min": 0,
                        "max": 4,
                        "display": "number",
                    },
                ),
                "max_ranks": (
                    "INT",
                    {
                        "default": 32,
                        "step": 32,
                        "min": 32,
                        "max": 128,
                        "display": "number",
                    },
                ),
            }
        }

    RETURN_TYPES = (data_types.MODEL, "LORA_MANAGER")
    # RETURN_TYPES = (data_types.MODEL, )
    FUNCTION = "load_unet"
    CATEGORY = "☁️BizyAir/OneDiffEnterprise"
    # NODE_DISPLAY_NAME = "☁️BizyAir OneDiffLoadOptimizedDiffusionModel"

    def load_unet(self, unet_name, max_num_loras, max_ranks):
        print("why : ", folder_paths.get_filename_list("diffusion_models"))
        node_data = create_node_data(
            class_type="OneDiffLoadOptimizedDiffusionModel",
            inputs={
                "unet_name": unet_name,
                "max_num_loras": max_num_loras,
                "max_ranks": max_ranks,
            },
            outputs={"slot_index": 0},
        )
        # model = BizyAirNodeIO(
        #     self.assigned_id,
        #     {self.assigned_id: node_data},
        #     config_file=folder_paths.guess_config(unet_name=unet_name),
        # )
        model = BizyAirNodeIO(
            self.assigned_id,
            {self.assigned_id: node_data},
        )
        return (model,)


# class VAELoader1(BizyAirBaseNode):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {"required": {"vae_name": (folder_paths.get_filename_list("vae"),)}}

#     RETURN_TYPES = (data_types.VAE,)
#     RETURN_NAMES = ("vae",)
#     FUNCTION = "load_vae"

#     CATEGORY = "loaders"

#     def load_vae(self, vae_name):
#         node_data = create_node_data(
#             class_type="VAELoader",
#             inputs={"vae_name": vae_name},
#             outputs={"slot_index": 0},
#         )
#         vae = BizyAirNodeIO(
#             self.assigned_id,
#             {self.assigned_id: node_data},
#             # config_file=folder_paths.guess_config(vae_name=vae_name),
#         )
#         return (vae,)
