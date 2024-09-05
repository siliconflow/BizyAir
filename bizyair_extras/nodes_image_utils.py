import os
import urllib.request

import folder_paths

from bizyair import BizyAirBaseNode
from bizyair.image_utils import encode_data
from nodes import LoadImage


class LoadImageURL(BizyAirBaseNode):
    # https://mei-xia.imgbb.com
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": (
                    "STRING",
                    {
                        "multiline": True,  # True if you want the field to look like the one on the ClipTextEncode node
                        "default": "url or path",
                        "lazy": True,
                    },
                ),
            },
        }

    CATEGORY = "image_utils"
    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "apply"
    NODE_DISPLAY_NAME = "Load Image (URL)"

    def apply(self, url: str):
        url = url.strip()
        input_dir = folder_paths.get_input_directory()
        filename = os.path.basename(url)
        file_path = os.path.join(input_dir, filename)

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"File {filename} already exists, skipping download.")
        else:
            # Download the image
            urllib.request.urlretrieve(url, file_path)
            print(f"Image successfully downloaded and saved as {filename}.")
        return LoadImage().load_image(filename)


class Image_Encode(BizyAirBaseNode):
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

    CATEGORY = "image_utils"
    FUNCTION = "apply"
    RETURN_TYPES = ("IMAGE",)
    NODE_DISPLAY_NAME = "Image Encode"

    def apply(self, image, lossless=False):
        out = encode_data(image, lossless=lossless)
        return (out,)
