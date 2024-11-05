import os
import urllib.request
import base64
import time
import re

import folder_paths

from bizyair import BizyAirBaseNode
from bizyair.image_utils import encode_data
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

    def apply(self, url: str):
        url = url.strip()
        input_dir = folder_paths.get_input_directory()
        
        # check if it's a base64 encoded image
        base64_pattern = r'^data:image/([a-zA-Z]+);base64,'
        match = re.match(base64_pattern, url)
        
        if match:
            # get image format
            image_format = match.group(1)
            # generate a file name with timestamp
            timestamp = int(time.time() * 1000)  # precise to milliseconds
            filename = f"base64-{timestamp}.{image_format}"
            file_path = os.path.join(input_dir, filename)
            
            # decode base64 data and save file
            image_data = url.split(',')[1]
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            print(f"Base64 image saved as {filename}")
        else:
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
