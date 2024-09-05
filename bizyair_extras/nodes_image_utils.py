from bizyair import BizyAirBaseNode
from bizyair.image_utils import encode_data


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
