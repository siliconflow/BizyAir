import copy
import glob
import hashlib
import json
import math
import os
from enum import Enum
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

import comfy.model_management
import cv2
import folder_paths
import groundingdino.datasets.transforms as T
import numpy as np
import torch
from groundingdino.models import build_model as local_groundingdino_build_model
from groundingdino.util.inference import predict
from groundingdino.util.slconfig import SLConfig as local_groundingdino_SLConfig
from groundingdino.util.utils import (
    clean_state_dict as local_groundingdino_clean_state_dict,
)
from PIL import Image, ImageOps, ImageSequence
from segment_anything_hq import SamPredictor, sam_model_registry
from torch.hub import download_url_to_file

from bizyair.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyair.image_utils import decode_base64_to_np, encode_image_to_base64
from nodes import LoadImage

from .route_sam import SAM_COORDINATE
from .utils import get_api_key, send_post_request

try:
    from cv2.ximgproc import guidedFilter
except ImportError:
    # print(e)
    print(
        f"Cannot import name 'guidedFilter' from 'cv2.ximgproc'"
        f"\nA few nodes cannot works properly, while most nodes are not affected. Please REINSTALL package 'opencv-contrib-python'."
        f"\nFor detail refer to \033[4mhttps://github.com/chflame163/ComfyUI_LayerStyle/issues/5\033[0m"
    )

sam_model_dir_name = "sams"
sam_model_list = {
    "sam_vit_h (2.56GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    },
    "sam_vit_l (1.25GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    },
    "sam_vit_b (375MB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    },
    "sam_hq_vit_h (2.57GB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth"
    },
    "sam_hq_vit_l (1.25GB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_l.pth"
    },
    "sam_hq_vit_b (379MB)": {
        "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_b.pth"
    },
    "mobile_sam(39MB)": {
        "model_url": "https://github.com/ChaoningZhang/MobileSAM/blob/master/weights/mobile_sam.pt"
    },
}

groundingdino_model_dir_name = "grounding-dino"
groundingdino_model_list = {
    "GroundingDINO_SwinT_OGC (694MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinT_OGC.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth",
    },
    "GroundingDINO_SwinB (938MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinB.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swinb_cogcoor.pth",
    },
}


class INFER_MODE(Enum):
    auto = 0
    text = 1
    points_box = 2
    batched_boxes = 3


class EDIT_MODE(Enum):
    box = 0
    point = 1


def get_bert_base_uncased_model_path():
    comfy_bert_model_base = os.path.join(folder_paths.models_dir, "bert-base-uncased")
    if glob.glob(
        os.path.join(comfy_bert_model_base, "**/model.safetensors"), recursive=True
    ):
        print("grounding-dino is using models/bert-base-uncased")
        return comfy_bert_model_base
    return "bert-base-uncased"


def save_masks(outmasks, image):
    if len(outmasks) == 0:
        return
    print("why masks: ", outmasks)
    if len(outmasks.shape) > 3:
        outmasks = outmasks.permute(1, 0, 2, 3)
        outmasks = (
            outmasks.view(outmasks.shape[1], outmasks.shape[2], outmasks.shape[3])
            .cpu()
            .numpy()
        )

    image_height, image_width, _ = image.shape

    img = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    mask_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    for mask in outmasks:
        non_zero_positions = np.nonzero(mask)
        # 使用非零值位置从原始图像中提取实例部分
        instance_part = image[non_zero_positions]
        # 将提取的实例部分应用到合并图像中对应的位置
        img[non_zero_positions] = instance_part

        mask_image[non_zero_positions] = 255  # 标记为白色
    print("why ahahahah")
    return img, mask_image


def list_sam_model():
    return list(sam_model_list.keys())


def load_sam_model(model_name):
    sam_checkpoint_path = get_local_filepath(
        sam_model_list[model_name]["model_url"], sam_model_dir_name
    )
    model_file_name = os.path.basename(sam_checkpoint_path)
    model_type = model_file_name.split(".")[0]
    if "hq" not in model_type and "mobile" not in model_type:
        model_type = "_".join(model_type.split("_")[1:-1])
    print("why model_type: ", model_type)
    print("path:", sam_checkpoint_path)
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
    sam_device = comfy.model_management.get_torch_device()
    sam.to(device=sam_device)
    sam.eval()
    sam.model_name = model_file_name
    predictor = SamPredictor(sam)
    return (sam, predictor)


def sam_predict(
    predictor, image, input_points, input_label, input_boxes, multimask_output
):
    predictor.set_image(image)
    masks, scores, logits = predictor.predict(
        point_coords=input_points,
        point_labels=input_label,
        box=input_boxes,
        multimask_output=multimask_output,
    )
    return masks, scores, logits


def sam_predict_torch(
    predictor, image_np, input_points, input_boxes, input_label, multimask_output
):

    image_np_rgb = image_np[..., :3]
    predictor.set_image(image_np_rgb)

    transformed_boxes = predictor.transform.apply_boxes_torch(
        input_boxes, image_np.shape[:2]
    )

    masks, scores, logits = predictor.predict_torch(
        point_coords=input_points,
        point_labels=input_label,
        boxes=transformed_boxes,
        multimask_output=multimask_output,
    )

    return masks, scores, logits


def get_local_filepath(url, dirname, local_file_name=None):
    if not local_file_name:
        parsed_url = urlparse(url)
        local_file_name = os.path.basename(parsed_url.path)

    destination = folder_paths.get_full_path(dirname, local_file_name)
    if destination:
        return destination

    folder = os.path.join(folder_paths.models_dir, dirname)
    if not os.path.exists(folder):
        os.makedirs(folder)

    destination = os.path.join(folder, local_file_name)
    if not os.path.exists(destination):
        download_url_to_file(url, destination)
    return destination


def load_groundingdino_model(model_name):
    dino_model_args = local_groundingdino_SLConfig.fromfile(
        get_local_filepath(
            groundingdino_model_list[model_name]["config_url"],
            groundingdino_model_dir_name,
        ),
    )

    if dino_model_args.text_encoder_type == "bert-base-uncased":
        dino_model_args.text_encoder_type = get_bert_base_uncased_model_path()

    dino = local_groundingdino_build_model(dino_model_args)
    checkpoint = torch.load(
        get_local_filepath(
            groundingdino_model_list[model_name]["model_url"],
            groundingdino_model_dir_name,
        ),
    )
    dino.load_state_dict(
        local_groundingdino_clean_state_dict(checkpoint["model"]), strict=False
    )
    device = comfy.model_management.get_torch_device()
    dino.to(device=device)
    dino.eval()
    return dino


def list_groundingdino_model():
    return list(groundingdino_model_list.keys())


def load_image(image_pil):
    transform = T.Compose(
        [
            T.RandomResize([800], max_size=1333),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    image_transformed, _ = transform(image_pil, None)
    return image_transformed


def guided_filter_alpha(
    image: torch.Tensor, mask: torch.Tensor, filter_radius: int
) -> torch.Tensor:
    sigma = 0.15
    d = filter_radius + 1
    mask = pil2tensor(tensor2pil(mask).convert("RGB"))
    if not bool(d % 2):
        d += 1
    s = sigma / 10
    i_dup = copy.deepcopy(image.cpu().numpy())
    a_dup = copy.deepcopy(mask.cpu().numpy())
    for index, image in enumerate(i_dup):
        alpha_work = a_dup[index]
        i_dup[index] = guidedFilter(image, alpha_work, d, s)
    return torch.from_numpy(i_dup)


def histogram_remap(
    image: torch.Tensor, blackpoint: float, whitepoint: float
) -> torch.Tensor:
    bp = min(blackpoint, whitepoint - 0.001)
    scale = 1 / (whitepoint - bp)
    i_dup = copy.deepcopy(image.cpu().numpy())
    i_dup = np.clip((i_dup - bp) * scale, 0.0, 1.0)
    return torch.from_numpy(i_dup)


def mask_edge_detail(
    image: torch.Tensor,
    mask: torch.Tensor,
    detail_range: int = 8,
    black_point: float = 0.01,
    white_point: float = 0.99,
) -> torch.Tensor:
    from pymatting import estimate_alpha_cf, fix_trimap

    d = detail_range * 5 + 1
    mask = pil2tensor(tensor2pil(mask).convert("RGB"))
    if not bool(d % 2):
        d += 1
    i_dup = copy.deepcopy(image.cpu().numpy().astype(np.float64))
    a_dup = copy.deepcopy(mask.cpu().numpy().astype(np.float64))
    for index, img in enumerate(i_dup):
        trimap = a_dup[index][:, :, 0]  # convert to single channel
        if detail_range > 0:
            trimap = cv2.GaussianBlur(trimap, (d, d), 0)
        trimap = fix_trimap(trimap, black_point, white_point)
        alpha = estimate_alpha_cf(
            img, trimap, laplacian_kwargs={"epsilon": 1e-6}, cg_kwargs={"maxiter": 500}
        )
        a_dup[index] = np.stack([alpha, alpha, alpha], axis=-1)  # convert back to rgb
    return torch.from_numpy(a_dup.astype(np.float32))


def generate_VITMatte_trimap(
    mask: torch.Tensor, erode_kernel_size: int, dilate_kernel_size: int
) -> Image:
    def g_trimap(mask, erode_kernel_size=10, dilate_kernel_size=10):
        erode_kernel = np.ones((erode_kernel_size, erode_kernel_size), np.uint8)
        dilate_kernel = np.ones((dilate_kernel_size, dilate_kernel_size), np.uint8)
        eroded = cv2.erode(mask, erode_kernel, iterations=5)
        dilated = cv2.dilate(mask, dilate_kernel, iterations=5)
        trimap = np.zeros_like(mask)
        trimap[dilated == 255] = 128
        trimap[eroded == 255] = 255
        return trimap

    mask = mask.squeeze(0).cpu().detach().numpy().astype(np.uint8) * 255
    trimap = g_trimap(mask, erode_kernel_size, dilate_kernel_size).astype(np.float32)
    trimap[trimap == 128] = 0.5
    trimap[trimap == 255] = 1
    trimap = torch.from_numpy(trimap).unsqueeze(0)

    return tensor2pil(trimap).convert("L")


def generate_VITMatte(
    image: Image,
    trimap: Image,
    local_files_only: bool = False,
    device: str = "cpu",
    max_megapixels: float = 2.0,
) -> Image:
    if image.mode != "RGB":
        image = image.convert("RGB")
    if trimap.mode != "L":
        trimap = trimap.convert("L")
    max_megapixels *= 1048576
    width, height = image.size
    ratio = width / height
    target_width = math.sqrt(ratio * max_megapixels)
    target_height = target_width / ratio
    target_width = int(target_width)
    target_height = int(target_height)
    if width * height > max_megapixels:
        image = image.resize((target_width, target_height), Image.BILINEAR)
        trimap = trimap.resize((target_width, target_height), Image.BILINEAR)
        print(
            f"vitmatte image size {width}x{height} too large, resize to {target_width}x{target_height} for processing."
        )
    model_name = "hustvl/vitmatte-small-composition-1k"
    if device == "cpu":
        device = torch.device("cpu")
    else:
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            print(
                "vitmatte device is set to cuda, but not available, using cpu instead."
            )
            device = torch.device("cpu")
    vit_matte_model = load_VITMatte_model(
        model_name=model_name, local_files_only=local_files_only
    )
    vit_matte_model.model.to(device)
    print(
        f"vitmatte processing, image size = {image.width}x{image.height}, device = {device}."
    )
    inputs = vit_matte_model.processor(
        images=image, trimaps=trimap, return_tensors="pt"
    )
    with torch.no_grad():
        inputs = {k: v.to(device) for k, v in inputs.items()}
        predictions = vit_matte_model.model(**inputs).alphas
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    mask = tensor2pil(predictions).convert("L")
    mask = mask.crop(
        (0, 0, image.width, image.height)
    )  # remove padding that the prediction appends (works in 32px tiles)
    if width * height > max_megapixels:
        mask = mask.resize((width, height), Image.BILINEAR)
    return mask


class VITMatteModel:
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor


def load_VITMatte_model(model_name: str, local_files_only: bool = False) -> object:
    # if local_files_only:
    #     model_name = Path(os.path.join(folder_paths.models_dir, "vitmatte"))
    model_name = Path(os.path.join(folder_paths.models_dir, "vitmatte"))
    from transformers import VitMatteForImageMatting, VitMatteImageProcessor

    model = VitMatteForImageMatting.from_pretrained(
        model_name, local_files_only=local_files_only
    )
    processor = VitMatteImageProcessor.from_pretrained(
        model_name, local_files_only=local_files_only
    )
    vitmatte = VITMatteModel(model, processor)
    return vitmatte


def pil2tensor(image: Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def tensor2pil(t_image: torch.Tensor) -> Image:
    return Image.fromarray(
        np.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
    )


def tensor2np(tensor: torch.Tensor) -> List[np.ndarray]:
    if len(tensor.shape) == 3:  # Single image
        return np.clip(255.0 * tensor.cpu().numpy(), 0, 255).astype(np.uint8)
    else:  # Batch of images
        return [
            np.clip(255.0 * t.cpu().numpy(), 0, 255).astype(np.uint8) for t in tensor
        ]


def mask2image(mask: torch.Tensor) -> Image:
    masks = tensor2np(mask)
    for m in masks:
        _mask = Image.fromarray(m).convert("L")
        _image = Image.new("RGBA", _mask.size, color="white")
        _image = Image.composite(
            _image, Image.new("RGBA", _mask.size, color="black"), _mask
        )
    return _image


def image2mask(image: Image) -> torch.Tensor:
    _image = image.convert("RGBA")
    alpha = _image.split()[0]
    bg = Image.new("L", _image.size)
    _image = Image.merge("RGBA", (bg, bg, bg, alpha))
    ret_mask = torch.tensor([pil2tensor(_image)[0, :, :, 3].tolist()])
    return ret_mask


def RGB2RGBA(image: Image, mask: Image) -> Image:
    (R, G, B) = image.convert("RGB").split()
    return Image.merge("RGBA", (R, G, B, mask.convert("L")))


def groundingdino_predict(dino_model, image_pil, prompt, box_threshold, text_threshold):
    image = load_image(image_pil)

    boxes, logits, phrases = predict(
        model=dino_model,
        image=image,
        caption=prompt,
        box_threshold=box_threshold,
        text_threshold=text_threshold,
    )

    filt_mask = logits > box_threshold
    boxes_filt = boxes.clone()
    boxes_filt = boxes_filt[filt_mask]
    H, W = image_pil.size[1], image_pil.size[0]
    for i in range(boxes_filt.size(0)):
        boxes_filt[i] = boxes_filt[i] * torch.Tensor([W, H, W, H])
        boxes_filt[i][:2] -= boxes_filt[i][2:] / 2
        boxes_filt[i][2:] += boxes_filt[i][:2]
    return boxes_filt


class BizyAirSegmentAnythingText:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
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

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "text_sam"

    CATEGORY = "☁️BizyAir/segment-anything"

    def text_sam(self, image, prompt, box_threshold, text_threshold):
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536
        device = image.device
        _, w, h, c = image.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        payload = {
            "image": None,
            "mode": 1,  # 文本分割模式
            "params": {
                "prompt": prompt,
                "box_threshold": box_threshold,
                "text_threshold": text_threshold,
            },
        }
        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        image = image.squeeze(0).numpy()
        image_pil = Image.fromarray((image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image

        ret: str = send_post_request(self.API_URL, payload=payload, headers=headers)
        ret = json.loads(ret)

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        if ret["status"] == "error":
            raise Exception(ret["message"])

        msg = ret["data"]
        if msg["type"] not in ("bizyair",):
            raise Exception(f"Unexpected response type: {msg}")

        if "error" in msg:
            raise Exception(f"Error happens: {msg}")

        img = msg["image"]
        mask_image = msg["mask_image"]

        img = (
            (torch.from_numpy(decode_base64_to_np(img)).float() / 255.0)
            .unsqueeze(0)
            .to(device)
        )
        img_mask = (
            torch.from_numpy(decode_base64_to_np(mask_image)).float() / 255.0
        ).to(device)
        img_mask = img_mask.mean(dim=-1)
        img_mask = img_mask.unsqueeze(0)

        return (img, img_mask)


class BizyAirSegmentAnythingPointBox:
    API_URL = f"{BIZYAIR_SERVER_ADDRESS}/supernode/sam"

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "is_point": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("processed_image", "mask", "original_image")
    FUNCTION = "apply"

    CATEGORY = "☁️BizyAir/segment-anything"

    def apply(self, image, is_point):
        API_KEY = get_api_key()
        SIZE_LIMIT = 1536

        # 加载原始图像
        original_image, _ = LoadImage().load_image(image)
        # 直接克隆原始图像用于处理和透传
        image_to_process = original_image.clone()

        device = image_to_process.device
        _, w, h, c = image_to_process.shape
        assert (
            w <= SIZE_LIMIT and h <= SIZE_LIMIT
        ), f"width and height must be less than {SIZE_LIMIT}x{SIZE_LIMIT}, but got {w} and {h}"

        if is_point:
            coordinates = [
                eval(SAM_COORDINATE["point_coords"][key])
                for key in SAM_COORDINATE["point_coords"]
            ]

            input_points = [
                [float(coord["startx"]), float(coord["starty"])]
                for coord in coordinates
            ]

            input_label = [coord["pointType"] for coord in coordinates]
            payload = {
                "image": None,
                "mode": INFER_MODE.points_box.value,
                "params": {
                    "input_points": json.dumps(input_points),
                    "input_label": json.dumps(input_label),
                    "input_boxes": None,
                },
            }
        else:
            coordinates = [
                eval(SAM_COORDINATE["box_coords"][key])
                for key in SAM_COORDINATE["box_coords"]
            ]
            input_box = [
                [
                    float(coord["startx"]),
                    float(coord["starty"]),
                    float(coord["endx"]),
                    float(coord["endy"]),
                ]
                for coord in coordinates
            ]

            payload = {
                "image": None,
                "mode": INFER_MODE.batched_boxes.value,
                "params": {
                    "input_points": None,
                    "input_label": None,
                    "input_boxes": json.dumps(input_box),
                },
            }

        auth = f"Bearer {API_KEY}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": auth,
        }
        # 处理用于API的图像
        api_image = image_to_process.squeeze(0).numpy()
        image_pil = Image.fromarray((api_image * 255).astype(np.uint8))
        input_image = encode_image_to_base64(image_pil, format="webp")
        payload["image"] = input_image

        ret: str = send_post_request(self.API_URL, payload=payload, headers=headers)
        ret = json.loads(ret)

        try:
            if "result" in ret:
                ret = json.loads(ret["result"])
        except Exception as e:
            raise Exception(f"Unexpected response: {ret} {e=}")

        if ret["status"] == "error":
            raise Exception(ret["message"])

        msg = ret["data"]
        if msg["type"] not in ("bizyair",):
            raise Exception(f"Unexpected response type: {msg}")

        if "error" in msg:
            raise Exception(f"Error happens: {msg}")

        img = msg["image"]
        mask_image = msg["mask_image"]

        processed_img = (
            (torch.from_numpy(decode_base64_to_np(img)).float() / 255.0)
            .unsqueeze(0)
            .to(device)
        )
        img_mask = (
            torch.from_numpy(decode_base64_to_np(mask_image)).float() / 255.0
        ).to(device)
        img_mask = img_mask.mean(dim=-1)
        img_mask = img_mask.unsqueeze(0)

        # 直接返回克隆的原始图像,无需转换
        return (processed_img, img_mask, image_to_process)

    @classmethod
    def IS_CHANGED(s, image, is_point):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image, is_point):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


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
    RETURN_TYPES = (
        "SAM_MODEL",
        "SAM_PREDICTOR",
    )

    def main(self, model_name):
        sam_model, sam_predictor = load_sam_model(model_name)
        return (
            sam_model,
            sam_predictor,
        )


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


class BizyAirGroundingDinoSAMSegment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sam_model": ("SAM_MODEL", {}),
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
        sam_model,
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
            print("why image.type", type(outimage))
            print("why mask_image.type", type(mask_image))
            images = (torch.from_numpy(outimage).float() / 255.0).unsqueeze(0)
            masks = (torch.from_numpy(mask_image).float() / 255.0).unsqueeze(0)
            print("1111")
            print("why images.shape: ", images.shape)
            res_images.append(images)
            res_masks.append(masks)
        if len(res_images) > 1:
            output_image = torch.cat(res_images, dim=0)
            output_mask = torch.cat(res_masks, dim=0)
        else:
            output_image = res_images[0]
            output_mask = res_masks[0]
        print("why outPUt: ", output_image.shape)
        print("why outPUt: ", output_mask.shape)
        return (output_image, output_mask)
        # return (image, torch.cat(res_masks, dim=0))


class BizyAirTrimapGenerate:
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
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )

    def main(
        self,
        image,
        mask,
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
                print("why trimap")
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
        )


NODE_CLASS_MAPPINGS = {
    "BizyAirSegmentAnythingText": BizyAirSegmentAnythingText,
    "BizyAirSegmentAnythingPointBox": BizyAirSegmentAnythingPointBox,
    "BizyAirGroundingDinoModelLoader": BizyAirGroundingDinoModelLoader,
    "BizyAirSAMModelLoader": BizyAirSAMModelLoader,
    "BizyAirGroundingDinoSAMSegment": BizyAirGroundingDinoSAMSegment,
    "BizyAirTrimapGenerate": BizyAirTrimapGenerate,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirSegmentAnythingText": "☁️BizyAir Text Guided SAM",
    "BizyAirSegmentAnythingPointBox": "☁️BizyAir Point-Box Guided SAM",
    "BizyAirGroundingDinoModelLoader": "☁️BizyAir Load GroundingDino Model",
    "BizyAirSAMModelLoader": "☁️BizyAir Load SAM Model",
    "BizyAirGroundingDinoSAMSegment": "☁️BizyAir GroundingDinoSAMSegment",
    "BizyAirTrimapGenerate": "☁️BizyAir Trimap Generate",
}
