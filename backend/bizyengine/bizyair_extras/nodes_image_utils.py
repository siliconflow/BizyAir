import base64
import hashlib
import os
import re
import urllib.request

import folder_paths
from bizyengine.core import BizyAirBaseNode
from bizyengine.core.image_utils import encode_data
from nodes import LoadImage


class LoadImageURL(BizyAirBaseNode):
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

    def apply(self, url: str, **kwargs):
        url = url.strip()
        input_dir = folder_paths.get_input_directory()

        # check if it's a base64 encoded image
        base64_pattern = r"^data:image/([a-zA-Z]+);base64,"
        match = re.match(base64_pattern, url)

        if match:
            # get image format
            image_format = match.group(1)
            image_data = url.split(",")[1]

            # calculate hash of the base64 data
            hash_object = hashlib.md5(image_data.encode())
            hash_value = hash_object.hexdigest()

            filename = f"base64-{hash_value}.{image_format}"
            file_path = os.path.join(input_dir, filename)

            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
                print(f"Base64 image saved as {filename}")
            else:
                print(f"Base64 image {filename} already exists, skipping save.")
        else:
            filename = os.path.basename(url)
            file_path = os.path.join(input_dir, filename)

            if os.path.exists(file_path):
                print(f"File {filename} already exists, skipping download.")
            else:
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

    def apply(self, image, lossless=False, **kwargs):
        out = encode_data(image, lossless=lossless)
        return (out,)
