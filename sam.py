import os
from pathlib import Path
from urllib.parse import urlparse

import comfy.model_management
import folder_paths
import groundingdino.datasets.transforms as T
import numpy as np
import torch
from PIL import Image
from segment_anything_hq import SamPredictor, sam_model_registry

from .sam_func import *


class BizyAirSAMModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list_sam_model(),),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = ("SAM_PREDICTOR",)

    def main(self, model_name):
        sam_checkpoint_path = get_local_filepath(
            sam_model_list[model_name]["model_url"], sam_model_dir_name
        )
        model_file_name = os.path.basename(sam_checkpoint_path)
        model_type = model_file_name.split(".")[0]
        if "hq" not in model_type and "mobile" not in model_type:
            model_type = "_".join(model_type.split("_")[1:-1])
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
        sam_device = comfy.model_management.get_torch_device()
        sam.to(device=sam_device)
        sam.eval()
        sam.model_name = model_file_name
        predictor = SamPredictor(sam)

        return (predictor,)


class BizyAirGroundingDinoModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_name": (list_groundingdino_model(),),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = ("GROUNDING_DINO_MODEL",)

    def main(self, model_name):
        dino_model = load_groundingdino_model(model_name)
        return (dino_model,)


class BizyAirVITMatteModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        method_list = [
            "VITMatte",
            "VITMatte(local)",
        ]
        return {
            "required": {
                "detail_method": (method_list,),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = (
        "VitMatte_MODEL",
        "VitMatte_predictor",
    )

    def main(self, detail_method):
        if detail_method == "VITMatte(local)":
            local_files_only = True
        else:
            local_files_only = False

        model_name = Path(os.path.join(folder_paths.models_dir, "vitmatte"))
        from transformers import VitMatteForImageMatting, VitMatteImageProcessor

        device = comfy.model_management.get_torch_device()

        model = VitMatteForImageMatting.from_pretrained(
            model_name, local_files_only=local_files_only
        )
        processor = VitMatteImageProcessor.from_pretrained(
            model_name, local_files_only=local_files_only
        )
        model.to(device)
        return (model, processor)


class BizyAirGroundingDinoSAMSegment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "grounding_dino_model": ("GROUNDING_DINO_MODEL", {}),
                "sam_predictor": ("SAM_PREDICTOR", {}),
                "image": ("IMAGE", {}),
                "prompt": ("STRING", {}),
                "box_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "text_threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = ("IMAGE", "MASK")

    def main(
        self,
        grounding_dino_model,
        sam_predictor,
        image,
        prompt,
        box_threshold,
        text_threshold,
    ):
        res_images = []
        res_masks = []
        multimask_output = False
        for item in image:
            item = Image.fromarray(
                # np.clip(255. * item.cpu().numpy(), 0, 255).astype(np.uint8)).convert('RGBA')
                np.clip(255.0 * item.cpu().numpy(), 0, 255).astype(np.uint8)
            )
            img = np.array(item)

            boxes = groundingdino_predict(
                grounding_dino_model, item, prompt, box_threshold, text_threshold
            )

            if boxes.shape[0] == 0:
                break
            sam_device = comfy.model_management.get_torch_device()
            boxes = boxes.to(sam_device)
            masks, scores, logits = sam_predict_torch(
                sam_predictor,
                img,
                None,
                boxes,
                None,
                multimask_output,
            )
            outimage, mask_image = save_masks(masks, img)
            images = (torch.from_numpy(outimage).float() / 255.0).unsqueeze(0)
            masks = (torch.from_numpy(mask_image).float() / 255.0).unsqueeze(0)
            res_images.append(images)
            res_masks.append(masks)
        if len(res_images) > 1:
            output_image = torch.cat(res_images, dim=0)
            output_mask = torch.cat(res_masks, dim=0)
        else:
            output_image = res_images[0]
            output_mask = res_masks[0]
        return (output_image, output_mask)
        # return (image, torch.cat(res_masks, dim=0))


class BizyAirTrimapGenerate1:
    @classmethod
    def INPUT_TYPES(cls):
        method_list = [
            "VITMatte",
            "VITMatte(local)",
            "PyMatting",
            "GuidedFilter",
        ]
        return {
            "required": {
                "image": ("IMAGE", {}),
                "mask": ("MASK",),
                "detail_method": (method_list,),
                "detail_erode": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "detail_dilate": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "black_point": (
                    "FLOAT",
                    {
                        "default": 0.15,
                        "min": 0.01,
                        "max": 0.98,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "white_point": (
                    "FLOAT",
                    {
                        "default": 0.99,
                        "min": 0.02,
                        "max": 0.99,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "max_megapixels": (
                    "FLOAT",
                    {"default": 2.0, "min": 1, "max": 999, "step": 0.1},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = (
        "IMAGE",
        "MASK",
        "MASK",
    )
    RETURN_NAMES = ("image", "mask", "trimap")

    def main(
        self,
        image,
        mask,
        trimap,
        detail_method,
        detail_erode,
        detail_dilate,
        black_point,
        white_point,
        max_megapixels,
    ):
        if detail_method == "VITMatte(local)":
            local_files_only = True
        else:
            local_files_only = False

        ret_images = []
        ret_masks = []
        device = comfy.model_management.get_torch_device()
        print("image.shape:", image.shape)
        print("image.shape[0]", image.shape[0])
        for i in range(image.shape[0]):
            img = torch.unsqueeze(image[i], 0)
            img = pil2tensor(tensor2pil(img).convert("RGB"))
            _image = tensor2pil(img).convert("RGBA")

            detail_range = detail_erode + detail_dilate
            if detail_method == "GuidedFilter":
                _mask = guided_filter_alpha(img, mask[i], detail_range // 6 + 1)
                _mask = tensor2pil(histogram_remap(_mask, black_point, white_point))
            elif detail_method == "PyMatting":
                _mask = tensor2pil(
                    mask_edge_detail(
                        img, mask[i], detail_range // 8 + 1, black_point, white_point
                    )
                )
            else:
                _trimap = generate_VITMatte_trimap(mask[i], detail_erode, detail_dilate)
                _mask = generate_VITMatte(
                    _image,
                    _trimap,
                    local_files_only=local_files_only,
                    device=device,
                    max_megapixels=max_megapixels,
                )
                _mask = tensor2pil(
                    histogram_remap(pil2tensor(_mask), black_point, white_point)
                )

            # _mask = mask2image(_mask)

            _image = RGB2RGBA(tensor2pil(img).convert("RGB"), _mask.convert("L"))

            ret_images.append(pil2tensor(_image))
            ret_masks.append(image2mask(_mask))
        if len(ret_masks) == 0:
            _, height, width, _ = image.size()
            empty_mask = torch.zeros(
                (1, height, width), dtype=torch.uint8, device="cpu"
            )
            return (empty_mask, empty_mask)

        return (
            torch.cat(ret_images, dim=0),
            torch.cat(ret_masks, dim=0),
            pil2tensor(_trimap),
        )


class BizyAirTrimapGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "detail_erode": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "detail_dilate": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("trimap",)

    def main(
        self,
        mask,
        detail_erode,
        detail_dilate,
    ):

        ret_masks = []

        for i in range(mask.shape[0]):
            _trimap = generate_VITMatte_trimap(mask[i], detail_erode, detail_dilate)
            _trimap_tensor = pil2tensor(_trimap)
            ret_masks.append(_trimap_tensor)

        return (torch.cat(ret_masks, dim=0),)


class BizyAirVITMattePredict:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
                "trimap": ("MASK",),
                "vitmatte_model": ("VitMatte_MODEL", {}),
                "vitmatte_predictor": ("VitMatte_predictor", {}),
                "black_point": (
                    "FLOAT",
                    {
                        "default": 0.15,
                        "min": 0.01,
                        "max": 0.98,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "white_point": (
                    "FLOAT",
                    {
                        "default": 0.99,
                        "min": 0.02,
                        "max": 0.99,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "max_megapixels": (
                    "FLOAT",
                    {"default": 2.0, "min": 1, "max": 999, "step": 0.1},
                ),
            }
        }

    CATEGORY = "☁️BizyAir/segment-anything"
    FUNCTION = "main"
    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )

    def main(
        self,
        image,
        trimap,
        vitmatte_model,
        vitmatte_predictor,
        black_point,
        white_point,
        max_megapixels,
    ):

        ret_images = []
        ret_masks = []
        device = comfy.model_management.get_torch_device()

        for i in range(image.shape[0]):
            img = torch.unsqueeze(image[i], 0)
            img = pil2tensor(tensor2pil(img).convert("RGB"))
            _image = tensor2pil(img).convert("RGBA")
            _mask = generate_VITMatte(
                vitmatte_model,
                vitmatte_predictor,
                _image,
                tensor2pil(trimap[i]),
                device=device,
                max_megapixels=max_megapixels,
            )
            _mask = tensor2pil(
                histogram_remap(pil2tensor(_mask), black_point, white_point)
            )

            _image = RGB2RGBA(tensor2pil(img).convert("RGB"), _mask.convert("L"))

            ret_images.append(pil2tensor(_image))
            ret_masks.append(image2mask(_mask))
        if len(ret_masks) == 0:
            _, height, width, _ = image.size()
            empty_mask = torch.zeros(
                (1, height, width), dtype=torch.uint8, device="cpu"
            )
            return (empty_mask, empty_mask)

        return (
            torch.cat(ret_images, dim=0),
            torch.cat(ret_masks, dim=0),
        )


NODE_CLASS_MAPPINGS = {
    "BizyAirGroundingDinoModelLoader": BizyAirGroundingDinoModelLoader,
    "BizyAirSAMModelLoader": BizyAirSAMModelLoader,
    "BizyAirVITMatteModelLoader": BizyAirVITMatteModelLoader,
    "BizyAirGroundingDinoSAMSegment": BizyAirGroundingDinoSAMSegment,
    "BizyAirTrimapGenerate": BizyAirTrimapGenerate,
    "BizyAirVITMattePredict": BizyAirVITMattePredict,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirGroundingDinoModelLoader": "☁️BizyAir Load GroundingDino Model",
    "BizyAirSAMModelLoader": "☁️BizyAir Load SAM Model",
    "BizyAirVITMatteModelLoader": "☁️BizyAir Load VITMatte Model",
    "BizyAirGroundingDinoSAMSegment": "☁️BizyAir GroundingDinoSAMSegment",
    "BizyAirTrimapGenerate": "☁️BizyAir Trimap Generate",
    "BizyAirVITMattePredict": "☁️BizyAir VITMatte Predict",
}
