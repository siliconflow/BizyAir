import copy
from typing import List

import numpy as np
import torch
from PIL import Image
from scipy.ndimage import gaussian_filter

sam_model_dir_name = "sams"
sam_model_list = {
    "sam_vit_h (2.56GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    },
    # "sam_vit_l (1.25GB)": {
    #     "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    # },
    # "sam_vit_b (375MB)": {
    #     "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    # },
    # "sam_hq_vit_h (2.57GB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth"
    # },
    # "sam_hq_vit_l (1.25GB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_l.pth"
    # },
    # "sam_hq_vit_b (379MB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_b.pth"
    # },
    # "mobile_sam(39MB)": {
    #     "model_url": "https://github.com/ChaoningZhang/MobileSAM/blob/master/weights/mobile_sam.pt"
    # },
}

groundingdino_model_dir_name = "grounding-dino"
groundingdino_model_list = {
    "GroundingDINO_SwinT_OGC (694MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinT_OGC.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth",
    },
    # "GroundingDINO_SwinB (938MB)": {
    #     "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinB.cfg.py",
    #     "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swinb_cogcoor.pth",
    # },
}


def list_sam_model():
    return list(sam_model_list.keys())


def list_groundingdino_model():
    return list(groundingdino_model_list.keys())


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
            # trimap = cv2.GaussianBlur(trimap, (d, d), 0)
            trimap = gaussian_filter(trimap, sigma=d / 2)
        trimap = fix_trimap(trimap, black_point, white_point)
        alpha = estimate_alpha_cf(
            img, trimap, laplacian_kwargs={"epsilon": 1e-6}, cg_kwargs={"maxiter": 500}
        )
        a_dup[index] = np.stack([alpha, alpha, alpha], axis=-1)  # convert back to rgb
    return torch.from_numpy(a_dup.astype(np.float32))


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
