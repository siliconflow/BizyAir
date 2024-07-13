import io
import base64
from typing import Union, List
from PIL import Image
import imageio.v2 as imageio
import numpy as np
import torch


def convert_image_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def encode_image_to_base64(
    image: Image.Image, format: str = "WEBP", quality: int = 100
) -> str:
    image = convert_image_to_rgb(image)
    with io.BytesIO() as output:
        imageio.imwrite(output, image, format=format, quality=quality)
        output.seek(0)
        img_bytes = output.getvalue()
        print(f"encode_image_to_base64: {format_bytes(len(img_bytes))}")
    return base64.b64encode(img_bytes).decode("utf-8")


def decode_base64_to_np(img_data: str, format: str = "WEBP") -> np.ndarray:
    img_bytes = base64.b64decode(img_data)
    print(f"decode_base64_to_np: {format_bytes(len(img_bytes))}")
    with io.BytesIO(img_bytes) as input_buffer:
        img = imageio.imread(input_buffer, format=format)
    return img


def decode_base64_to_image(img_data: str, format: str = "WEBP") -> Image.Image:
    return Image.fromarray(decode_base64_to_np(img_data, format))


def format_bytes(num_bytes: int) -> str:
    """
    Converts a number of bytes to a human-readable string with units (B, KB, or MB).

    :param num_bytes: The number of bytes to convert.
    :return: A string representing the number of bytes in a human-readable format.
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KB"
    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"


def encode_comfy_image(image: torch.Tensor, image_format="png") -> str:
    input_image = image.cpu().detach().numpy()
    i = 255.0 * input_image[0]
    input_image = np.clip(i, 0, 255).astype(np.uint8)
    base64ed_image = encode_image_to_base64(
        Image.fromarray(input_image), format=image_format
    )
    return base64ed_image


def decode_comfy_image(img_data: Union[List, str], image_format="png") -> torch.tensor:
    if isinstance(img_data, List):
        decoded_imgs = [decode_comfy_image(x) for x in img_data]

        combined_imgs = torch.cat(decoded_imgs, dim=0)
        return combined_imgs

    out = decode_base64_to_np(img_data, format=image_format)
    out = np.array(out).astype(np.float32) / 255.0
    output = torch.from_numpy(out)[
        None,
    ]
    return output


# Example usage:
# encoded_image = encode_image_to_base64(some_image_object)
# decoded_image = decode_base64_to_image(encoded_image)
