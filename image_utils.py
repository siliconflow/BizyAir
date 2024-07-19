import base64
import io
import os
import pickle
from functools import singledispatch
from typing import List, Union
import zlib
import copy
import numpy as np
import torch
from PIL import Image

# Marker to identify base64-encoded tensors
TENSOR_MARKER = "TENSOR:"
BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
from typing import Dict


def create_node_data(class_type: str, inputs: dict, outputs: dict):
    assert (
        outputs.get("slot_index", None) is not None
    ), "outputs must contain 'slot_index'"
    assert isinstance(outputs["slot_index"], int), "'slot_index' must be an integer"
    assert isinstance(class_type, str)

    out = {
        "class_type": class_type,
        "inputs": inputs,
        "outputs": outputs,
    }

    return out


class BizyAirNodeIO:
    user_id_counter = 50 # user_ids
    def __init__(self, node_id: int = "0", nodes: Dict[str, Dict[str, any]] = {}):
        self.node_id = node_id
        self.nodes = nodes

    def copy(self, node_id=None):
        if node_id is None:
            new_node_id = self.new_node_id()
        else:
            new_node_id = node_id
        return BizyAirNodeIO(nodes=copy.deepcopy(self.nodes), node_id=new_node_id)

    @staticmethod
    def new_node_id():
        BizyAirNodeIO.user_id_counter +=1
        return str(BizyAirNodeIO.user_id_counter)


def convert_image_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def encode_image_to_base64(
    image: Image.Image, format: str = "png", quality: int = 100
) -> str:
    image = convert_image_to_rgb(image)
    with io.BytesIO() as output:
        image.save(output, format=format, quality=quality)
        output.seek(0)
        img_bytes = output.getvalue()
        if BIZYAIR_DEBUG:
            print(f"encode_image_to_base64: {format_bytes(len(img_bytes))}")
    return base64.b64encode(img_bytes).decode("utf-8")


def decode_base64_to_np(img_data: str, format: str = "png") -> np.ndarray:
    img_bytes = base64.b64decode(img_data)
    if BIZYAIR_DEBUG:
        print(f"decode_base64_to_np: {format_bytes(len(img_bytes))}")
    with io.BytesIO(img_bytes) as input_buffer:
        img = Image.open(input_buffer)
        img = img.convert("RGBA")
        return np.array(img)


def decode_base64_to_image(img_data: str) -> Image.Image:
    img_bytes = base64.b64decode(img_data)
    with io.BytesIO(img_bytes) as input_buffer:
        img = Image.open(input_buffer)
        if BIZYAIR_DEBUG:
            format_info = img.format.upper() if img.format else "Unknown"
            print(f"decode image format: {format_info}")
        return img


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


def tensor_to_base64(tensor: torch.Tensor) -> str:
    tensor_np = tensor.cpu().detach().numpy()

    tensor_bytes = pickle.dumps(tensor_np)

    tensor_bytes = zlib.compress(tensor_bytes)

    tensor_b64 = base64.b64encode(tensor_bytes).decode("utf-8")
    return tensor_b64


def base64_to_tensor(tensor_b64: str) -> torch.Tensor:
    tensor_bytes = base64.b64decode(tensor_b64)

    tensor_bytes = zlib.decompress(tensor_bytes)

    tensor_np = pickle.loads(tensor_bytes)

    tensor = torch.from_numpy(tensor_np)
    return tensor


@singledispatch
def decode_data(input):
    raise NotImplementedError(f"Unsupported type: {type(input)}")


@decode_data.register(int)
@decode_data.register(float)
@decode_data.register(bool)
@decode_data.register(type(None))
def _(input):
    return input


@decode_data.register(dict)
def _(input):
    return {k: decode_data(v) for k, v in input.items()}


@decode_data.register(list)
def _(input):
    return [decode_data(x) for x in input]


@decode_data.register(str)
def _(input):
    if input.startswith(TENSOR_MARKER):
        tensor_b64 = input[len(TENSOR_MARKER) :]
        return base64_to_tensor(tensor_b64)
    return input


@singledispatch
def encode_data(output):
    raise NotImplementedError(f"Unsupported type: {type(output)}")


@encode_data.register(dict)
def _(output):
    return {k: encode_data(v) for k, v in output.items()}


@encode_data.register(list)
def _(output):
    return [encode_data(x) for x in output]


@encode_data.register(torch.Tensor)
def _(output):
    return TENSOR_MARKER + tensor_to_base64(output)


@encode_data.register(BizyAirNodeIO)
def _(output: BizyAirNodeIO):
    origin_id = output.node_id
    origin_slot = output.nodes[origin_id]["outputs"]["slot_index"]
    return [origin_id, origin_slot]


@encode_data.register(int)
@encode_data.register(float)
@encode_data.register(str)
@encode_data.register(bool)
@encode_data.register(type(None))
def _(output):
    return output
