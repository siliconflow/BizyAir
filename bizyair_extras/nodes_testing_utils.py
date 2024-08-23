"""
pip install numpy scikit-image pillow

"""

import numpy as np
import torch
import torch.nn.functional as F
from bizyair import NODE_CLASS_MAPPINGS
from PIL import Image


class ImagesTest:
    # https://docs.comfy.org/essentials/custom_node_images_and_masks#images
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {"images_a": ("*", {}), "images_b": ("*", {})},
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    CATEGORY = "images_test"
    FUNCTION = "test"

    def test(self, images_a: torch.Tensor, images_b: torch.Tensor):
        print(f"{torch.allclose(images_a, images_b, rtol=0.1, atol=0.1)=}")  # True
        from skimage.metrics import structural_similarity as ssim

        for image_a, image_b in zip(images_a, images_b):
            if image_a.shape != image_b.shape:
                raise ValueError(
                    f"Images must have the same dimensions, {image_a.shape=} {image_b.shape=}"
                )
            mse = F.mse_loss(image_a, image_b)
            print(f"MSE value: {mse}")  # MSE value: 3.59503501385916e-05
            i = 255.0 * image_a.cpu().numpy()
            img1 = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            i = 255.0 * image_b.cpu().numpy()
            img2 = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            ssim_value = ssim(np.array(img1), np.array(img2), channel_axis=2)
            print(f"SSIM value: {ssim_value}")  # SSIM value: 0.9909630031265833

        return (None,)


NODE_CLASS_MAPPINGS["Tools_ImagesTest"] = ImagesTest
