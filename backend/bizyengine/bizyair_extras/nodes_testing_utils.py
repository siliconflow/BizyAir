"""
pip install numpy scikit-image pillow

"""

import os
import random

import folder_paths
import numpy as np
from bizyengine.core import NODE_CLASS_MAPPINGS
from bizyengine.core.image_utils import decode_data, encode_data
from PIL import Image


class ImagesTest:
    # https://docs.comfy.org/essentials/custom_node_images_and_masks#images
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + "".join(
            random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5)
        )

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images1": ("IMAGE",),
                "images2": ("IMAGE",),
                "ssim_threshold": ("STRING", {"default": "0.9"}),
                "raise_if_diff": (["enable", "disable"],),
                "image_id": ("STRING", {"default": "ComfyUI"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "images_test"

    def save_images(
        self,
        images1,
        images2,
        ssim_threshold: float,
        raise_if_diff: str,
        image_id="ComfyUI",
        prompt=None,
        extra_pnginfo=None,
    ):
        from skimage.metrics import structural_similarity as ssim

        assert len(images1) == len(images2)
        filename_prefix = image_id[:]
        filename_prefix += self.prefix_append
        (
            full_output_folder,
            filename,
            counter,
            subfolder,
            filename_prefix,
        ) = folder_paths.get_save_image_path(
            filename_prefix,
            self.output_dir,
            images1[0].shape[1],
            images1[0].shape[0],
        )
        results = list()
        for image1, image2 in zip(images1, images2):

            # image diff
            image = image1.cpu() - image2.cpu()

            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            file = f"{filename}_{counter:05}_.png"
            img.save(
                os.path.join(full_output_folder, file),
                pnginfo=metadata,
                compress_level=4,
            )
            results.append(
                {"filename": file, "subfolder": subfolder, "type": self.type}
            )
            counter += 1

            max_diff = image.abs().max().item()

            img1 = self.image_to_numpy(image1)
            img2 = self.image_to_numpy(image2)
            ssim = ssim(img1, img2, channel_axis=2)

            print(
                "\033[91m"
                f"[ShowImageDiff {image_id}] Max value of diff is {max_diff}, image simularity is {ssim:.6f}"
                + "\033[0m"
            )

            if raise_if_diff == "enable":
                assert ssim > float(
                    ssim_threshold
                ), f"Image diff is too large, ssim is {ssim}, "

        return {"ui": {"images": results}}

    def image_to_numpy(self, image):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return np.array(img)


class ImageEncodeDecodeTest:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"image": ("IMAGE",)},
            "optional": {
                "lossless": (
                    "BOOLEAN",
                    {"default": False, "label_on": "yes", "label_off": "no"},
                ),
            },
        }

    CATEGORY = "images_test"
    FUNCTION = "test"
    RETURN_TYPES = ("IMAGE",)

    def test(self, image, lossless=False):
        return (decode_data(encode_data(image, lossless=lossless)),)


NODE_CLASS_MAPPINGS["Tools_ImagesTest"] = ImagesTest
NODE_CLASS_MAPPINGS["Tools_ImageEncodeDecodeTest"] = ImageEncodeDecodeTest
