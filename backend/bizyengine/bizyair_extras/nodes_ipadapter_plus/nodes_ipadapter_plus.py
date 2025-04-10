import math
import os

import folder_paths
import torch
from bizyengine.core import BizyAirBaseNode, BizyAirNodeIO, create_node_data
from bizyengine.core.configs.conf import config_manager
from bizyengine.core.data_types import CLIP, CONDITIONING, MODEL

# set the models directory
if "ipadapter" not in folder_paths.folder_names_and_paths:
    current_paths = [os.path.join(folder_paths.models_dir, "ipadapter")]
else:
    current_paths, _ = folder_paths.folder_names_and_paths["ipadapter"]
folder_paths.folder_names_and_paths["ipadapter"] = (
    current_paths,
    folder_paths.supported_pt_extensions,
)

WEIGHT_TYPES = [
    "linear",
    "ease in",
    "ease out",
    "ease in-out",
    "reverse in-out",
    "weak input",
    "weak output",
    "weak middle",
    "strong middle",
    "style transfer",
    "composition",
    "strong style transfer",
    "style and composition",
    "style transfer precise",
    "composition precise",
]


# """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Loaders
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# """


class IPAdapterUnifiedLoader(BizyAirBaseNode):
    def __init__(self):
        super().__init__()
        self.lora = None
        self.clipvision = {"file": None, "model": None}
        self.ipadapter = {"file": None, "model": None}
        self.insightface = {"provider": None, "model": None}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (MODEL,),
                "preset": (
                    [
                        # "LIGHT - SD1.5 only (low strength)",
                        # "STANDARD (medium strength)",
                        # "VIT-G (medium strength)",
                        "PLUS (high strength)",
                        "PLUS FACE (portraits)",
                        # "FULL FACE - SD1.5 only (portraits stronger)",
                    ],
                ),
            },
            "optional": {
                "ipadapter": ("IPADAPTER",),
            },
        }

    NODE_DISPLAY_NAME = "IPAdapter Unified Loader"
    RETURN_TYPES = (
        MODEL,
        "IPADAPTER",
    )
    RETURN_NAMES = (
        "model",
        "ipadapter",
    )
    FUNCTION = "load_models"
    CATEGORY = "ipadapter"

    def load_models(self, **kwargs):
        assert kwargs.get("ipadapter", None) is None, "TODO"

        new_model: BizyAirNodeIO = kwargs["model"].copy(self.assigned_id)
        new_model.add_node_data(
            class_type="IPAdapterUnifiedLoader",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        ipadapter: BizyAirNodeIO = kwargs["model"].copy(self.assigned_id)
        ipadapter.add_node_data(
            class_type="IPAdapterUnifiedLoader",
            inputs=kwargs,
            outputs={"slot_index": 1},
        )
        return (
            new_model,
            ipadapter,
        )


# class IPAdapterUnifiedLoaderFaceID(IPAdapterUnifiedLoader):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "preset": (
#                     [
#                         "FACEID",
#                         "FACEID PLUS - SD1.5 only",
#                         "FACEID PLUS V2",
#                         "FACEID PORTRAIT (style transfer)",
#                         "FACEID PORTRAIT UNNORM - SDXL only (strong)",
#                     ],
#                 ),
#                 "lora_strength": (
#                     "FLOAT",
#                     {"default": 0.6, "min": 0, "max": 1, "step": 0.01},
#                 ),
#                 "provider": (
#                     ["CPU", "CUDA", "ROCM", "DirectML", "OpenVINO", "CoreML"],
#                 ),
#             },
#             "optional": {
#                 "ipadapter": ("IPADAPTER",),
#             },
#         }

#     RETURN_NAMES = (
#         "MODEL",
#         "ipadapter",
#     )
#     CATEGORY = "ipadapter/faceid"


# class IPAdapterUnifiedLoaderCommunity(IPAdapterUnifiedLoader):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "preset": (["Composition", "Kolors"],),
#             },
#             "optional": {
#                 "ipadapter": ("IPADAPTER",),
#             },
#         }

#     CATEGORY = "ipadapter/loaders"


class IPAdapterModelLoader(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"ipadapter_file": (["kolors/ip_adapter_plus_general.bin"],)}
            # "required": {
            #     "ipadapter_file": (
            #         [
            #             "to choose",
            #         ],
            #     ),
            #     "model_version_id": (
            #         "STRING",
            #         {
            #             "default": "",
            #         },
            #     ),
            # }
        }

    RETURN_TYPES = ("IPADAPTER",)
    FUNCTION = "load_ipadapter_model"
    CATEGORY = "ipadapter/loaders"

    def load_ipadapter_model(self, **kwargs):
        node_data = create_node_data(
            class_type="IPAdapterModelLoader",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        return (BizyAirNodeIO(self.assigned_id, nodes={self.assigned_id: node_data}),)

    # @classmethod
    # def VALIDATE_INPUTS(cls, ipadapter_file):
    #     # TODO
    #     import warnings

    #     warnings.warn(message=f"TODO fix {cls}VALIDATE_INPUTS")
    #     if ipadapter_file == "" or ipadapter_file is None:
    #         return False
    #     return True

    # def load_ipadapter_model(self, **kwargs):
    #     model_version_id = kwargs.get("model_version_id", "")
    #     if model_version_id != "":
    #         # use model version id as lora name
    #         ipadapter_file = (
    #             f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
    #         )
    #         kwargs["ipadapter_file"] = ipadapter_file
    #     node_data = create_node_data(
    #         class_type="IPAdapterModelLoader",
    #         inputs=kwargs,
    #         outputs={"slot_index": 0},
    #     )
    #     return (BizyAirNodeIO(self.assigned_id, nodes={self.assigned_id: node_data}),)


# class IPAdapterInsightFaceLoader:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "provider": (["CPU", "CUDA", "ROCM"],),
#             },
#         }

#     RETURN_TYPES = ("INSIGHTFACE",)
#     FUNCTION = "load_insightface"
#     CATEGORY = "ipadapter/loaders"


# """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Main Apply Nodes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# """


class IPAdapterSimple(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (MODEL,),
                "ipadapter": ("IPADAPTER",),
                "image": ("IMAGE",),
                "weight": (
                    "FLOAT",
                    {"default": 1.0, "min": -1, "max": 3, "step": 0.05},
                ),
                "start_at": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_at": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "weight_type": (
                    ["standard", "prompt is more important", "style transfer"],
                ),
            },
            "optional": {
                "attn_mask": ("MASK",),
            },
        }

    NODE_DISPLAY_NAME = "IPAdapter"
    RETURN_TYPES = (MODEL,)
    RETURN_NAMES = "model"
    FUNCTION = "apply_ipadapter"
    CATEGORY = "ipadapter"

    def apply_ipadapter(self, **kwargs):
        new_model: BizyAirNodeIO = kwargs["model"].copy(self.assigned_id)
        new_model.add_node_data(
            class_type="IPAdapter",
            inputs=kwargs,
            outputs={"slot_index": 0},
        )
        return (new_model,)


class IPAdapterAdvanced(BizyAirBaseNode):
    def __init__(self):
        super().__init__()
        self.unfold_batch = False

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (MODEL,),
                "ipadapter": ("IPADAPTER",),
                "image": ("IMAGE",),
                "weight": (
                    "FLOAT",
                    {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
                ),
                "weight_type": (WEIGHT_TYPES,),
                "combine_embeds": (
                    ["concat", "add", "subtract", "average", "norm average"],
                ),
                "start_at": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_at": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "embeds_scaling": (
                    ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
                ),
            },
            "optional": {
                "image_negative": ("IMAGE",),
                "attn_mask": ("MASK",),
                "clip_vision": ("CLIP_VISION",),
            },
        }

    RETURN_TYPES = (MODEL,)
    RETURN_NAMES = ("model",)
    FUNCTION = "apply_ipadapter"
    CATEGORY = "ipadapter"

    def apply_ipadapter(self, **kwargs):
        new_model: BizyAirNodeIO = kwargs["model"].copy(self.assigned_id)
        new_model.add_node_data(
            class_type=self.__class__.__name__, inputs=kwargs, outputs={"slot_index": 0}
        )
        return (new_model,)


# class IPAdapterBatch(IPAdapterAdvanced):
#     def __init__(self):
#         super().__init__()
#         self.unfold_batch = True

#     NODE_DISPLAY_NAME = "IPAdapter Batch (Adv.)"

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#                 "encode_batch_size": ("INT", {"default": 0, "min": 0, "max": 4096}),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }


class IPAdapterStyleComposition(IPAdapterAdvanced):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (MODEL,),
                "ipadapter": ("IPADAPTER",),
                "image_style": ("IMAGE",),
                "image_composition": ("IMAGE",),
                "weight_style": (
                    "FLOAT",
                    {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
                ),
                "weight_composition": (
                    "FLOAT",
                    {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
                ),
                "expand_style": ("BOOLEAN", {"default": False}),
                "combine_embeds": (
                    ["concat", "add", "subtract", "average", "norm average"],
                    {"default": "average"},
                ),
                "start_at": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_at": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "embeds_scaling": (
                    ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
                ),
            },
            "optional": {
                "image_negative": ("IMAGE",),
                "attn_mask": ("MASK",),
                "clip_vision": ("CLIP_VISION",),
            },
        }

    CATEGORY = "ipadapter/style_composition"


# class IPAdapterStyleCompositionBatch(IPAdapterStyleComposition):
#     def __init__(self):
#         super().__init__()
#         self.unfold_batch = True

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image_style": ("IMAGE",),
#                 "image_composition": ("IMAGE",),
#                 "weight_style": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "weight_composition": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "expand_style": ("BOOLEAN", {"default": False}),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     NODE_DISPLAY_NAME = "IPAdapter Style & Composition Batch SDXL"


# class IPAdapterFaceID(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 3, "step": 0.05},
#                 ),
#                 "weight_faceidv2": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5.0, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#                 "insightface": ("INSIGHTFACE",),
#             },
#         }

#     CATEGORY = "ipadapter/faceid"
#     RETURN_TYPES = (
#         "MODEL",
#         "IMAGE",
#     )
#     RETURN_NAMES = (
#         "MODEL",
#         "face_image",
#     )
#     NODE_DISPLAY_NAME = "IPAdapter FaceID"


# class IPAAdapterFaceIDBatch(IPAdapterFaceID):
#     def __init__(self):
#         super().__init__()
#         self.unfold_batch = True

#     NODE_DISPLAY_NAME = "IPAdapter FaceID Batch"


# class IPAdapterTiled:
#     def __init__(self):
#         self.unfold_batch = False

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 3, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "sharpening": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     RETURN_TYPES = (
#         "MODEL",
#         "IMAGE",
#         "MASK",
#     )
#     RETURN_NAMES = (
#         "MODEL",
#         "tiles",
#         "masks",
#     )
#     FUNCTION = "apply_tiled"
#     CATEGORY = "ipadapter/tiled"

#     def apply_tiled(
#         self,
#         model,
#         ipadapter,
#         image,
#         weight,
#         weight_type,
#         start_at,
#         end_at,
#         sharpening,
#         combine_embeds="concat",
#         image_negative=None,
#         attn_mask=None,
#         clip_vision=None,
#         embeds_scaling="V only",
#         encode_batch_size=0,
#     ):
#         # 1. Select the models
#         if "ipadapter" in ipadapter:
#             ipadapter_model = ipadapter["ipadapter"]["model"]
#             clip_vision = (
#                 clip_vision
#                 if clip_vision is not None
#                 else ipadapter["clipvision"]["model"]
#             )
#         else:
#             ipadapter_model = ipadapter
#             clip_vision = clip_vision

#         if clip_vision is None:
#             raise Exception("Missing CLIPVision model.")

#         del ipadapter

#         # 2. Extract the tiles
#         tile_size = 256  # I'm using 256 instead of 224 as it is more likely divisible by the latent size, it will be downscaled to 224 by the clip vision encoder
#         _, oh, ow, _ = image.shape
#         if attn_mask is None:
#             attn_mask = torch.ones([1, oh, ow], dtype=image.dtype, device=image.device)

#         image = image.permute([0, 3, 1, 2])
#         attn_mask = attn_mask.unsqueeze(1)
#         # the mask should have the same proportions as the reference image and the latent
#         attn_mask = T.Resize(
#             (oh, ow), interpolation=T.InterpolationMode.BICUBIC, antialias=True
#         )(attn_mask)

#         # if the image is almost a square, we crop it to a square
#         if oh / ow > 0.75 and oh / ow < 1.33:
#             # crop the image to a square
#             image = T.CenterCrop(min(oh, ow))(image)
#             resize = (tile_size * 2, tile_size * 2)

#             attn_mask = T.CenterCrop(min(oh, ow))(attn_mask)
#         # otherwise resize the smallest side and the other proportionally
#         else:
#             resize = (
#                 (int(tile_size * ow / oh), tile_size)
#                 if oh < ow
#                 else (tile_size, int(tile_size * oh / ow))
#             )

#         # using PIL for better results
#         imgs = []
#         for img in image:
#             img = T.ToPILImage()(img)
#             img = img.resize(resize, resample=Image.Resampling["LANCZOS"])
#             imgs.append(T.ToTensor()(img))
#         image = torch.stack(imgs)
#         del imgs, img

#         # we don't need a high quality resize for the mask
#         attn_mask = T.Resize(
#             resize[::-1], interpolation=T.InterpolationMode.BICUBIC, antialias=True
#         )(attn_mask)

#         # we allow a maximum of 4 tiles
#         if oh / ow > 4 or oh / ow < 0.25:
#             crop = (tile_size, tile_size * 4) if oh < ow else (tile_size * 4, tile_size)
#             image = T.CenterCrop(crop)(image)
#             attn_mask = T.CenterCrop(crop)(attn_mask)

#         attn_mask = attn_mask.squeeze(1)

#         if sharpening > 0:
#             image = contrast_adaptive_sharpening(image, sharpening)

#         image = image.permute([0, 2, 3, 1])

#         _, oh, ow, _ = image.shape

#         # find the number of tiles for each side
#         tiles_x = math.ceil(ow / tile_size)
#         tiles_y = math.ceil(oh / tile_size)
#         overlap_x = max(
#             0, (tiles_x * tile_size - ow) / (tiles_x - 1 if tiles_x > 1 else 1)
#         )
#         overlap_y = max(
#             0, (tiles_y * tile_size - oh) / (tiles_y - 1 if tiles_y > 1 else 1)
#         )

#         base_mask = torch.zeros(
#             [attn_mask.shape[0], oh, ow], dtype=image.dtype, device=image.device
#         )

#         # extract all the tiles from the image and create the masks
#         tiles = []
#         masks = []
#         for y in range(tiles_y):
#             for x in range(tiles_x):
#                 start_x = int(x * (tile_size - overlap_x))
#                 start_y = int(y * (tile_size - overlap_y))
#                 tiles.append(
#                     image[
#                         :,
#                         start_y : start_y + tile_size,
#                         start_x : start_x + tile_size,
#                         :,
#                     ]
#                 )
#                 mask = base_mask.clone()
#                 mask[
#                     :, start_y : start_y + tile_size, start_x : start_x + tile_size
#                 ] = attn_mask[
#                     :, start_y : start_y + tile_size, start_x : start_x + tile_size
#                 ]
#                 masks.append(mask)
#         del mask

#         # 3. Apply the ipadapter to each group of tiles
#         model = model.clone()
#         for i in range(len(tiles)):
#             ipa_args = {
#                 "image": tiles[i],
#                 "image_negative": image_negative,
#                 "weight": weight,
#                 "weight_type": weight_type,
#                 "combine_embeds": combine_embeds,
#                 "start_at": start_at,
#                 "end_at": end_at,
#                 "attn_mask": masks[i],
#                 "unfold_batch": self.unfold_batch,
#                 "embeds_scaling": embeds_scaling,
#                 "encode_batch_size": encode_batch_size,
#             }
#             # apply the ipadapter to the model without cloning it
#             model, _ = ipadapter_execute(
#                 model, ipadapter_model, clip_vision, **ipa_args
#             )

#         return (
#             model,
#             torch.cat(tiles),
#             torch.cat(masks),
#         )


# class IPAdapterTiledBatch(IPAdapterTiled):
#     def __init__(self):
#         self.unfold_batch = True

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 3, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "sharpening": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#                 "encode_batch_size": ("INT", {"default": 0, "min": 0, "max": 4096}),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }


# class IPAdapterEmbeds:
#     def __init__(self):
#         self.unfold_batch = False

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "pos_embed": ("EMBEDS",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 3, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "neg_embed": ("EMBEDS",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     RETURN_TYPES = ("MODEL",)
#     FUNCTION = "apply_ipadapter"
#     CATEGORY = "ipadapter/embeds"

#     def apply_ipadapter(
#         self,
#         model,
#         ipadapter,
#         pos_embed,
#         weight,
#         weight_type,
#         start_at,
#         end_at,
#         neg_embed=None,
#         attn_mask=None,
#         clip_vision=None,
#         embeds_scaling="V only",
#     ):
#         ipa_args = {
#             "pos_embed": pos_embed,
#             "neg_embed": neg_embed,
#             "weight": weight,
#             "weight_type": weight_type,
#             "start_at": start_at,
#             "end_at": end_at,
#             "attn_mask": attn_mask,
#             "embeds_scaling": embeds_scaling,
#             "unfold_batch": self.unfold_batch,
#         }

#         if "ipadapter" in ipadapter:
#             ipadapter_model = ipadapter["ipadapter"]["model"]
#             clip_vision = (
#                 clip_vision
#                 if clip_vision is not None
#                 else ipadapter["clipvision"]["model"]
#             )
#         else:
#             ipadapter_model = ipadapter
#             clip_vision = clip_vision

#         if clip_vision is None and neg_embed is None:
#             raise Exception("Missing CLIPVision model.")

#         del ipadapter

#         return ipadapter_execute(
#             model.clone(), ipadapter_model, clip_vision, **ipa_args
#         )


# class IPAdapterEmbedsBatch(IPAdapterEmbeds):
#     def __init__(self):
#         self.unfold_batch = True


# class IPAdapterMS(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "weight_faceidv2": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5.0, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#                 "layer_weights": ("STRING", {"default": "", "multiline": True}),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#                 "insightface": ("INSIGHTFACE",),
#             },
#         }

#     CATEGORY = "ipadapter/dev"


# class IPAdapterClipVisionEnhancer(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#                 "enhance_tiles": ("INT", {"default": 2, "min": 1, "max": 16}),
#                 "enhance_ratio": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05},
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     CATEGORY = "ipadapter/dev"


# class IPAdapterFromParams(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "ipadapter_params": ("IPADAPTER_PARAMS",),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     CATEGORY = "ipadapter/params"


# class IPAdapterPreciseStyleTransfer(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "style_boost": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -5, "max": 5, "step": 0.05},
#                 ),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }


# class IPAdapterPreciseStyleTransferBatch(IPAdapterPreciseStyleTransfer):
#     def __init__(self):
#         self.unfold_batch = True


# class IPAdapterPreciseComposition(IPAdapterAdvanced):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "model": ("MODEL",),
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1, "max": 5, "step": 0.05},
#                 ),
#                 "composition_boost": (
#                     "FLOAT",
#                     {"default": 0.0, "min": -5, "max": 5, "step": 0.05},
#                 ),
#                 "combine_embeds": (
#                     ["concat", "add", "subtract", "average", "norm average"],
#                 ),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "embeds_scaling": (
#                     ["V only", "K+V", "K+V w/ C penalty", "K+mean(V) w/ C penalty"],
#                 ),
#             },
#             "optional": {
#                 "image_negative": ("IMAGE",),
#                 "attn_mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }


# class IPAdapterPreciseCompositionBatch(IPAdapterPreciseComposition):
#     def __init__(self):
#         self.unfold_batch = True


# """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Helpers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# """


# class IPAdapterEncoder:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "ipadapter": ("IPADAPTER",),
#                 "image": ("IMAGE",),
#                 "weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1.0, "max": 3.0, "step": 0.01},
#                 ),
#             },
#             "optional": {
#                 "mask": ("MASK",),
#                 "clip_vision": ("CLIP_VISION",),
#             },
#         }

#     RETURN_TYPES = (
#         "EMBEDS",
#         "EMBEDS",
#     )
#     RETURN_NAMES = (
#         "pos_embed",
#         "neg_embed",
#     )
#     FUNCTION = "encode"
#     CATEGORY = "ipadapter/embeds"


# class IPAdapterCombineEmbeds:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "embed1": ("EMBEDS",),
#                 "method": (
#                     [
#                         "concat",
#                         "add",
#                         "subtract",
#                         "average",
#                         "norm average",
#                         "max",
#                         "min",
#                     ],
#                 ),
#             },
#             "optional": {
#                 "embed2": ("EMBEDS",),
#                 "embed3": ("EMBEDS",),
#                 "embed4": ("EMBEDS",),
#                 "embed5": ("EMBEDS",),
#             },
#         }

#     RETURN_TYPES = ("EMBEDS",)
#     FUNCTION = "batch"
#     CATEGORY = "ipadapter/embeds"

#     def batch(self, embed1, method, embed2=None, embed3=None, embed4=None, embed5=None):
#         if (
#             method == "concat"
#             and embed2 is None
#             and embed3 is None
#             and embed4 is None
#             and embed5 is None
#         ):
#             return (embed1,)

#         embeds = [embed1, embed2, embed3, embed4, embed5]
#         embeds = [embed for embed in embeds if embed is not None]
#         embeds = torch.cat(embeds, dim=0)

#         if method == "add":
#             embeds = torch.sum(embeds, dim=0).unsqueeze(0)
#         elif method == "subtract":
#             embeds = embeds[0] - torch.mean(embeds[1:], dim=0)
#             embeds = embeds.unsqueeze(0)
#         elif method == "average":
#             embeds = torch.mean(embeds, dim=0).unsqueeze(0)
#         elif method == "norm average":
#             embeds = torch.mean(
#                 embeds / torch.norm(embeds, dim=0, keepdim=True), dim=0
#             ).unsqueeze(0)
#         elif method == "max":
#             embeds = torch.max(embeds, dim=0).values.unsqueeze(0)
#         elif method == "min":
#             embeds = torch.min(embeds, dim=0).values.unsqueeze(0)

#         return (embeds,)


# class IPAdapterNoise:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "type": (["fade", "dissolve", "gaussian", "shuffle"],),
#                 "strength": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0, "max": 1, "step": 0.05},
#                 ),
#                 "blur": ("INT", {"default": 0, "min": 0, "max": 32, "step": 1}),
#             },
#             "optional": {
#                 "image_optional": ("IMAGE",),
#             },
#         }

#     RETURN_TYPES = ("IMAGE",)
#     FUNCTION = "make_noise"
#     CATEGORY = "ipadapter/utils"

#     def make_noise(self, type, strength, blur, image_optional=None):
#         if image_optional is None:
#             image = torch.zeros([1, 224, 224, 3])
#         else:
#             transforms = T.Compose(
#                 [
#                     T.CenterCrop(min(image_optional.shape[1], image_optional.shape[2])),
#                     T.Resize(
#                         (224, 224),
#                         interpolation=T.InterpolationMode.BICUBIC,
#                         antialias=True,
#                     ),
#                 ]
#             )
#             image = transforms(image_optional.permute([0, 3, 1, 2])).permute(
#                 [0, 2, 3, 1]
#             )

#         seed = (
#             int(torch.sum(image).item()) % 1000000007
#         )  # hash the image to get a seed, grants predictability
#         torch.manual_seed(seed)

#         if type == "fade":
#             noise = torch.rand_like(image)
#             noise = image * (1 - strength) + noise * strength
#         elif type == "dissolve":
#             mask = (torch.rand_like(image) < strength).float()
#             noise = torch.rand_like(image)
#             noise = image * (1 - mask) + noise * mask
#         elif type == "gaussian":
#             noise = torch.randn_like(image) * strength
#             noise = image + noise
#         elif type == "shuffle":
#             transforms = T.Compose(
#                 [
#                     T.ElasticTransform(alpha=75.0, sigma=(1 - strength) * 3.5),
#                     T.RandomVerticalFlip(p=1.0),
#                     T.RandomHorizontalFlip(p=1.0),
#                 ]
#             )
#             image = transforms(image.permute([0, 3, 1, 2])).permute([0, 2, 3, 1])
#             noise = torch.randn_like(image) * (strength * 0.75)
#             noise = image * (1 - noise) + noise

#         del image
#         noise = torch.clamp(noise, 0, 1)

#         if blur > 0:
#             if blur % 2 == 0:
#                 blur += 1
#             noise = T.functional.gaussian_blur(
#                 noise.permute([0, 3, 1, 2]), blur
#             ).permute([0, 2, 3, 1])

#         return (noise,)


# class PrepImageForClipVision:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "image": ("IMAGE",),
#                 "interpolation": (
#                     ["LANCZOS", "BICUBIC", "HAMMING", "BILINEAR", "BOX", "NEAREST"],
#                 ),
#                 "crop_position": (["top", "bottom", "left", "right", "center", "pad"],),
#                 "sharpening": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0, "max": 1, "step": 0.05},
#                 ),
#             },
#         }

#     RETURN_TYPES = ("IMAGE",)
#     FUNCTION = "prep_image"

#     CATEGORY = "ipadapter/utils"

#     def prep_image(
#         self, image, interpolation="LANCZOS", crop_position="center", sharpening=0.0
#     ):
#         size = (224, 224)
#         _, oh, ow, _ = image.shape
#         output = image.permute([0, 3, 1, 2])

#         if crop_position == "pad":
#             if oh != ow:
#                 if oh > ow:
#                     pad = (oh - ow) // 2
#                     pad = (pad, 0, pad, 0)
#                 elif ow > oh:
#                     pad = (ow - oh) // 2
#                     pad = (0, pad, 0, pad)
#                 output = T.functional.pad(output, pad, fill=0)
#         else:
#             crop_size = min(oh, ow)
#             x = (ow - crop_size) // 2
#             y = (oh - crop_size) // 2
#             if "top" in crop_position:
#                 y = 0
#             elif "bottom" in crop_position:
#                 y = oh - crop_size
#             elif "left" in crop_position:
#                 x = 0
#             elif "right" in crop_position:
#                 x = ow - crop_size

#             x2 = x + crop_size
#             y2 = y + crop_size

#             output = output[:, :, y:y2, x:x2]

#         imgs = []
#         for img in output:
#             img = T.ToPILImage()(img)  # using PIL for better results
#             img = img.resize(size, resample=Image.Resampling[interpolation])
#             imgs.append(T.ToTensor()(img))
#         output = torch.stack(imgs, dim=0)
#         del imgs, img

#         if sharpening > 0:
#             output = contrast_adaptive_sharpening(output, sharpening)

#         output = output.permute([0, 2, 3, 1])

#         return (output,)


# class IPAdapterSaveEmbeds:
#     def __init__(self):
#         self.output_dir = folder_paths.get_output_directory()

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "embeds": ("EMBEDS",),
#                 "filename_prefix": ("STRING", {"default": "IP_embeds"}),
#             },
#         }

#     RETURN_TYPES = ()
#     FUNCTION = "save"
#     OUTPUT_NODE = True
#     CATEGORY = "ipadapter/embeds"

#     def save(self, embeds, filename_prefix):
#         (
#             full_output_folder,
#             filename,
#             counter,
#             subfolder,
#             filename_prefix,
#         ) = folder_paths.get_save_image_path(filename_prefix, self.output_dir)
#         file = f"{filename}_{counter:05}.ipadpt"
#         file = os.path.join(full_output_folder, file)

#         torch.save(embeds, file)
#         return (None,)


# class IPAdapterLoadEmbeds:
#     @classmethod
#     def INPUT_TYPES(s):
#         input_dir = folder_paths.get_input_directory()
#         files = [
#             os.path.relpath(os.path.join(root, file), input_dir)
#             for root, dirs, files in os.walk(input_dir)
#             for file in files
#             if file.endswith(".ipadpt")
#         ]
#         return {
#             "required": {
#                 "embeds": [
#                     sorted(files),
#                 ]
#             },
#         }

#     RETURN_TYPES = ("EMBEDS",)
#     FUNCTION = "load"
#     CATEGORY = "ipadapter/embeds"

#     def load(self, embeds):
#         path = folder_paths.get_annotated_filepath(embeds)
#         return (torch.load(path).cpu(),)


# class IPAdapterWeights:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "weights": ("STRING", {"default": "1.0, 0.0", "multiline": True}),
#                 "timing": (
#                     [
#                         "custom",
#                         "linear",
#                         "ease_in_out",
#                         "ease_in",
#                         "ease_out",
#                         "random",
#                     ],
#                     {"default": "linear"},
#                 ),
#                 "frames": ("INT", {"default": 0, "min": 0, "max": 9999, "step": 1}),
#                 "start_frame": (
#                     "INT",
#                     {"default": 0, "min": 0, "max": 9999, "step": 1},
#                 ),
#                 "end_frame": (
#                     "INT",
#                     {"default": 9999, "min": 0, "max": 9999, "step": 1},
#                 ),
#                 "add_starting_frames": (
#                     "INT",
#                     {"default": 0, "min": 0, "max": 9999, "step": 1},
#                 ),
#                 "add_ending_frames": (
#                     "INT",
#                     {"default": 0, "min": 0, "max": 9999, "step": 1},
#                 ),
#                 "method": (
#                     ["full batch", "shift batches", "alternate batches"],
#                     {"default": "full batch"},
#                 ),
#             },
#             "optional": {
#                 "image": ("IMAGE",),
#             },
#         }

#     RETURN_TYPES = ("FLOAT", "FLOAT", "INT", "IMAGE", "IMAGE", "WEIGHTS_STRATEGY")
#     RETURN_NAMES = (
#         "weights",
#         "weights_invert",
#         "total_frames",
#         "image_1",
#         "image_2",
#         "weights_strategy",
#     )
#     FUNCTION = "weights"
#     CATEGORY = "ipadapter/weights"


# class IPAdapterWeightsFromStrategy(IPAdapterWeights):
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "weights_strategy": ("WEIGHTS_STRATEGY",),
#             },
#             "optional": {
#                 "image": ("IMAGE",),
#             },
#         }


# class IPAdapterPromptScheduleFromWeightsStrategy:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "weights_strategy": ("WEIGHTS_STRATEGY",),
#                 "prompt": ("STRING", {"default": "", "multiline": True}),
#             }
#         }

#     RETURN_TYPES = ("STRING",)
#     RETURN_NAMES = ("prompt_schedule",)
#     FUNCTION = "prompt_schedule"
#     CATEGORY = "ipadapter/weights"


# class IPAdapterCombineWeights:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "weights_1": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
#                 ),
#                 "weights_2": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},
#                 ),
#             }
#         }

#     RETURN_TYPES = ("FLOAT", "INT")
#     RETURN_NAMES = ("weights", "count")
#     FUNCTION = "combine"
#     CATEGORY = "ipadapter/utils"


# class IPAdapterRegionalConditioning:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 # "set_cond_area": (["default", "mask bounds"],),
#                 "image": ("IMAGE",),
#                 "image_weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": -1.0, "max": 3.0, "step": 0.05},
#                 ),
#                 "prompt_weight": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05},
#                 ),
#                 "weight_type": (WEIGHT_TYPES,),
#                 "start_at": (
#                     "FLOAT",
#                     {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#                 "end_at": (
#                     "FLOAT",
#                     {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
#                 ),
#             },
#             "optional": {
#                 "mask": ("MASK",),
#                 "positive": ("CONDITIONING",),
#                 "negative": ("CONDITIONING",),
#             },
#         }

#     RETURN_TYPES = (
#         "IPADAPTER_PARAMS",
#         "CONDITIONING",
#         "CONDITIONING",
#     )
#     RETURN_NAMES = ("IPADAPTER_PARAMS", "POSITIVE", "NEGATIVE")
#     FUNCTION = "conditioning"

#     CATEGORY = "ipadapter/params"


# class IPAdapterCombineParams:
#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "params_1": ("IPADAPTER_PARAMS",),
#                 "params_2": ("IPADAPTER_PARAMS",),
#             },
#             "optional": {
#                 "params_3": ("IPADAPTER_PARAMS",),
#                 "params_4": ("IPADAPTER_PARAMS",),
#                 "params_5": ("IPADAPTER_PARAMS",),
#             },
#         }

#     RETURN_TYPES = ("IPADAPTER_PARAMS",)
#     FUNCTION = "combine"
#     CATEGORY = "ipadapter/params"


# """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Register
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# """

# NODE_CLASS_MAPPINGS = {
#     # Main Apply Nodes
#     "IPAdapter": IPAdapterSimple,
#     "IPAdapterAdvanced": IPAdapterAdvanced,
#     "IPAdapterBatch": IPAdapterBatch,
#     "IPAdapterFaceID": IPAdapterFaceID,
#     "IPAAdapterFaceIDBatch": IPAAdapterFaceIDBatch,
#     "IPAdapterTiled": IPAdapterTiled,
#     "IPAdapterTiledBatch": IPAdapterTiledBatch,
#     "IPAdapterEmbeds": IPAdapterEmbeds,
#     "IPAdapterEmbedsBatch": IPAdapterEmbedsBatch,
#     "IPAdapterStyleComposition": IPAdapterStyleComposition,
#     "IPAdapterStyleCompositionBatch": IPAdapterStyleCompositionBatch,
#     "IPAdapterMS": IPAdapterMS,
#     "IPAdapterClipVisionEnhancer": IPAdapterClipVisionEnhancer,
#     "IPAdapterFromParams": IPAdapterFromParams,
#     "IPAdapterPreciseStyleTransfer": IPAdapterPreciseStyleTransfer,
#     "IPAdapterPreciseStyleTransferBatch": IPAdapterPreciseStyleTransferBatch,
#     "IPAdapterPreciseComposition": IPAdapterPreciseComposition,
#     "IPAdapterPreciseCompositionBatch": IPAdapterPreciseCompositionBatch,
#     # Loaders
#     "IPAdapterUnifiedLoader": IPAdapterUnifiedLoader,
#     "IPAdapterUnifiedLoaderFaceID": IPAdapterUnifiedLoaderFaceID,
#     "IPAdapterModelLoader": IPAdapterModelLoader,
#     "IPAdapterInsightFaceLoader": IPAdapterInsightFaceLoader,
#     "IPAdapterUnifiedLoaderCommunity": IPAdapterUnifiedLoaderCommunity,
#     # Helpers
#     "IPAdapterEncoder": IPAdapterEncoder,
#     "IPAdapterCombineEmbeds": IPAdapterCombineEmbeds,
#     "IPAdapterNoise": IPAdapterNoise,
#     "PrepImageForClipVision": PrepImageForClipVision,
#     "IPAdapterSaveEmbeds": IPAdapterSaveEmbeds,
#     "IPAdapterLoadEmbeds": IPAdapterLoadEmbeds,
#     "IPAdapterWeights": IPAdapterWeights,
#     "IPAdapterCombineWeights": IPAdapterCombineWeights,
#     "IPAdapterWeightsFromStrategy": IPAdapterWeightsFromStrategy,
#     "IPAdapterPromptScheduleFromWeightsStrategy": IPAdapterPromptScheduleFromWeightsStrategy,
#     "IPAdapterRegionalConditioning": IPAdapterRegionalConditioning,
#     "IPAdapterCombineParams": IPAdapterCombineParams,
# }

# NODE_DISPLAY_NAME_MAPPINGS = {
#     # Main Apply Nodes
#     "IPAdapter": "IPAdapter",
#     "IPAdapterAdvanced": "IPAdapter Advanced",
#     "IPAdapterBatch": "IPAdapter Batch (Adv.)",
#     "IPAdapterFaceID": "IPAdapter FaceID",
#     "IPAAdapterFaceIDBatch": "IPAdapter FaceID Batch",
#     "IPAdapterTiled": "IPAdapter Tiled",
#     "IPAdapterTiledBatch": "IPAdapter Tiled Batch",
#     "IPAdapterEmbeds": "IPAdapter Embeds",
#     "IPAdapterEmbedsBatch": "IPAdapter Embeds Batch",
#     "IPAdapterStyleComposition": "IPAdapter Style & Composition SDXL",
#     "IPAdapterStyleCompositionBatch": "IPAdapter Style & Composition Batch SDXL",
#     "IPAdapterMS": "IPAdapter Mad Scientist",
#     "IPAdapterClipVisionEnhancer": "IPAdapter ClipVision Enhancer",
#     "IPAdapterFromParams": "IPAdapter from Params",
#     "IPAdapterPreciseStyleTransfer": "IPAdapter Precise Style Transfer",
#     "IPAdapterPreciseStyleTransferBatch": "IPAdapter Precise Style Transfer Batch",
#     "IPAdapterPreciseComposition": "IPAdapter Precise Composition",
#     "IPAdapterPreciseCompositionBatch": "IPAdapter Precise Composition Batch",
#     # Loaders
#     "IPAdapterUnifiedLoader": "IPAdapter Unified Loader",
#     "IPAdapterUnifiedLoaderFaceID": "IPAdapter Unified Loader FaceID",
#     "IPAdapterModelLoader": "IPAdapter Model Loader",
#     "IPAdapterInsightFaceLoader": "IPAdapter InsightFace Loader",
#     "IPAdapterUnifiedLoaderCommunity": "IPAdapter Unified Loader Community",
#     # Helpers
#     "IPAdapterEncoder": "IPAdapter Encoder",
#     "IPAdapterCombineEmbeds": "IPAdapter Combine Embeds",
#     "IPAdapterNoise": "IPAdapter Noise",
#     "PrepImageForClipVision": "Prep Image For ClipVision",
#     "IPAdapterSaveEmbeds": "IPAdapter Save Embeds",
#     "IPAdapterLoadEmbeds": "IPAdapter Load Embeds",
#     "IPAdapterWeights": "IPAdapter Weights",
#     "IPAdapterWeightsFromStrategy": "IPAdapter Weights From Strategy",
#     "IPAdapterPromptScheduleFromWeightsStrategy": "Prompt Schedule From Weights Strategy",
#     "IPAdapterCombineWeights": "IPAdapter Combine Weights",
#     "IPAdapterRegionalConditioning": "IPAdapter Regional Conditioning",
#     "IPAdapterCombineParams": "IPAdapter Combine Params",
# }
