import base64
from collections import deque
import io
import os
import pickle
from functools import singledispatch
from typing import Any, List, Union
import zlib
import numpy as np
import requests
import torch
from PIL import Image
import yaml

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
    user_id_counter = 1  # user_ids

    def __init__(
        self,
        node_id: int = "0",
        nodes: Dict[str, Dict[str, any]] = {},
        request_mode="batch",
        config_file=None,
        configs: dict = None,
    ):
        self.node_id = node_id
        self.nodes = nodes
        valid_modes = ["batch", "instant"]
        assert (
            request_mode in valid_modes
        ), f"Invalid request mode: {request_mode}. Must be one of {valid_modes}."
        self.request_mode = request_mode

        if config_file:
            if not os.path.exists(config_file):
                raise FileNotFoundError(
                    f"Configuration file '{config_file}' does not exist."
                )
            self.configs = self._load_config_file(config_file)
        else:
            self.configs = configs

    def _load_config_file(self, config_file) -> dict:
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            return config

    def copy(self, node_id=None):
        if node_id is None:
            BizyAirNodeIO.user_id_counter += 1
            new_node_id = str(BizyAirNodeIO.user_id_counter)
        else:
            try:
                if not isinstance(node_id, str):
                    raise ValueError("Node ID must be a string.")
                int(node_id)
            except ValueError:
                raise ValueError(
                    "Node ID must be a string that can be converted to an integer."
                )
            new_node_id = node_id

        return BizyAirNodeIO(
            nodes=self.nodes.copy(),
            node_id=new_node_id,
            request_mode=self.request_mode,
            configs=self.configs,
        )

    @property
    def workflow_api(self):
        class_configs = self.configs.get("class_types", {})
        class_usage_count = {}
        for _, instance_info in self.nodes.items():
            class_type = instance_info["class_type"]
            if class_type not in class_configs:
                raise NotImplementedError(f"NotImplementedError for {class_type}")
            if class_type not in class_usage_count:
                class_usage_count[class_type] = 0
            class_usage_count[class_type] += 1

            max_instances = class_configs[class_type]["max_instances"]
            # Check if the maximum instances limit has been exceeded
            if max_instances < class_usage_count[class_type]:
                raise RuntimeError(
                    False,
                    f"{class_type} max_instances is too large, allowed: {max_instances}",
                )

            wokflow_api = self.generate_workflow_with_allocated_ids()
            return wokflow_api

    def generate_workflow_with_allocated_ids(self):
        class_configs = self.configs.get("class_types", {})
        class_id_counter = {}
        node_id_mapping = {}

        for node_id, node_data in self.nodes.items():
            class_type = node_data["class_type"]
            class_node_ids = class_configs[class_type]["node_ids"]
            class_id_counter.setdefault(class_type, 0)
            allocated_id = class_node_ids[class_id_counter[class_type]]
            class_id_counter[class_type] += 1
            node_id_mapping[node_id] = str(allocated_id)

        workflow = {}
        for ins_id, ins_info in self.nodes.items():
            node_id = node_id_mapping[ins_id]
            workflow[node_id] = {
                "class_type": ins_info["class_type"],
                "outputs": ins_info["outputs"],
                "inputs": {},
            }

            for in_key, value in ins_info["inputs"].items():
                if isinstance(value, list) and len(value) == 2:
                    workflow[node_id]["inputs"][in_key] = [
                        node_id_mapping[value[0]],
                        value[1],
                    ]
                else:
                    workflow[node_id]["inputs"][in_key] = value
        return {"workflow": workflow, "last_link_id": node_id_mapping[self.node_id]}

    def add_node_data(
        self, class_type: str, inputs: Dict[str, Any], outputs: Dict[str, Any]
    ):
        node_data = create_node_data(
            class_type=class_type, inputs=inputs, outputs=outputs,
        )

        encoded_node_data = encode_data(node_data)

        self.update_nodes_from_others(*inputs.values())

        if self.node_id in self.nodes:
            print(
                f"Warning: Node ID {self.node_id} already exists. Data will be overwritten."
            )

        self.nodes[self.node_id] = encoded_node_data

    def update_nodes_from_others(self, *others):
        for other in others:
            if isinstance(other, BizyAirNodeIO):
                self.nodes.update(other.nodes)

    def send_request(self, url, headers) -> any:
        response = requests.post(url, headers=headers, json=self.workflow_api,)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")

        # local
        out = response.json()["data"]["payload"]
        real_out = decode_data(out)
        return real_out[0]


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
