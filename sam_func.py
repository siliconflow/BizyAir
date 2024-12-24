import copy
import glob
import math
import os
from typing import List
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
from PIL import Image
from torch.hub import download_url_to_file

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
    return img, mask_image


def list_sam_model():
    return list(sam_model_list.keys())


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
    vit_matte_model,
    vitmatte_predictor,
    image: Image,
    trimap: Image,
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

    print(
        f"vitmatte processing, image size = {image.width}x{image.height}, device = {device}."
    )
    inputs = vitmatte_predictor(images=image, trimaps=trimap, return_tensors="pt")
    with torch.no_grad():
        inputs = {k: v.to(device) for k, v in inputs.items()}
        predictions = vit_matte_model(**inputs).alphas
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
