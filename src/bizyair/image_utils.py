import base64
import io
import json
import os
import pickle
import zlib
from enum import Enum
from functools import singledispatch
from typing import Any, List, Union

import numpy as np
import torch
import yaml
from PIL import Image

# Marker to identify base64-encoded tensors
TENSOR_MARKER = "TENSOR:"
IMAGE_MARKER = "IMAGE:"

BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)

from typing import Dict

from .common import client
from .path_utils import convert_prompt_label_path_to_real_path


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


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
    def __init__(
        self,
        node_id: int = "0",
        nodes: Dict[str, Dict[str, any]] = {},
        config_file=None,
        configs: dict = {},
        debug: bool = BIZYAIR_DEBUG,
    ):
        self._validate_node_id(node_id=node_id)

        self.node_id = node_id
        self.nodes = nodes
        self.debug = debug

        if config_file:
            if not os.path.exists(config_file):
                raise FileNotFoundError(
                    f"Configuration file '{config_file}' does not exist."
                )
            self.configs = self._load_config_file(config_file)
        else:
            self.configs = configs

    def _short_repr(self, obj: Any, max_length: int = 50) -> str:
        if isinstance(obj, str):
            if len(obj) > max_length:
                return obj[:max_length] + "..."
            return obj
        elif isinstance(obj, torch.Tensor):
            return f"Tensor(shape={obj.shape}, dtype={obj.dtype})"
        elif isinstance(obj, dict):
            return {k: self._short_repr(v) for k, v in obj.items()}
        else:
            obj_str = repr(obj)
            if len(obj_str) > max_length:
                return obj_str[:max_length] + "..."
            return obj_str

    def _load_config_file(self, config_file) -> dict:
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            return config

    def _validate_node_id(self, node_id) -> bool:
        if node_id is None:
            raise ValueError("Node ID cannot be None.")
        if not isinstance(node_id, str):
            raise ValueError("Node ID must be a string.")
        if not node_id.isdigit():
            raise ValueError(
                "Node ID must be a string that can be converted to an integer."
            )
        return True

    def copy(self, new_node_id: str = None):
        self._validate_node_id(new_node_id)
        if new_node_id in self.nodes:
            raise ValueError(f"Node ID '{new_node_id}' already exists.")

        return BizyAirNodeIO(
            nodes=self.nodes.copy(),
            node_id=new_node_id,
            configs=self.configs,
        )

    @property
    def workflow_api(self):
        class_configs = self.configs.get("class_types", {})
        class_usage_count = {}
        for _, instance_info in self.nodes.items():
            class_type = instance_info["class_type"]
            if class_type not in class_configs:
                continue
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
        prompt = convert_prompt_label_path_to_real_path(self.nodes)
        return {"prompt": prompt, "last_node_id": self.node_id}

    def add_node_data(
        self,
        class_type: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any] = {"slot_index": 0},
    ):
        node_data = create_node_data(
            class_type=class_type,
            inputs=inputs,
            outputs=outputs,
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

    def get_headers(self):
        if self.API_KEY is None or not self.API_KEY.startswith("sk-"):
            raise ValueError(
                f"API key is not set. Please provide a valid API key(from cloud.siliconflow.cn), {self.API_KEY=}"
            )

        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.API_KEY}",
        }

    def service_route(self):
        if not self.configs:
            return None
        service_config = self.configs["service_config"]
        real_service_route = service_config["service_address"] + service_config["route"]
        return real_service_route

    def send_request(
        self, url=None, headers=None, *, progress_callback=None, stream=False
    ) -> any:
        # self._short_repr(self.nodes, max_length=100)
        # self._short_repr(self.workflow_api['prompt'], max_length=100)

        api_url = self.service_route()
        if self.debug:
            prompt = self._short_repr(self.workflow_api["prompt"], max_length=100)
            print(f"Debug: {prompt=}")
        if stream:
            result = None
            pass  # TODO(fix)
            # def process_events(api_url, workflow_api, api_key):
            #     total_steps = None
            #     with BizyAirStreamClient(api_url, workflow_api, api_key) as stream_client:
            #         for event_data in stream_client.events():
            #             try:
            #                 event_data = json.loads(event_data)["data"]
            #             except json.JSONDecodeError as e:
            #                 print(f"rror decoding JSON: {e}")
            #                 print(f"Received data: {event_data}")
            #                 raise e

            #             # if self.debug:
            #             print(f"Debug Event Data: {self._short_repr(event_data, 100)}")

            #             status = event_data["status"]
            #             data = event_data["data"]
            #             pending_count = event_data.get("pending_tasks_count", None)
            #             if status == TaskStatus.PENDING.value:
            #                 print(
            #                     f"Task is pending, current pending tasks count: {pending_count}"
            #                 )
            #             elif status == TaskStatus.PROCESSING.value:
            #                 if "progress" in data and isinstance(data["progress"], dict):
            #                     step, total_steps = (
            #                         data["progress"]["value"],
            #                         data["progress"]["total"],
            #                     )
            #                     progress_callback(step, total_steps, preview=None)

            #             elif status == TaskStatus.COMPLETED.value:
            #                 if total_steps:
            #                     progress_callback(total_steps, total_steps, preview=None)
            #                 return event_data

            # result = process_events(api_url, self.workflow_api, self.API_KEY)
        else:
            result = client.send_request(
                url=api_url, data=json.dumps(self.workflow_api).encode("utf-8")
            )

        if result is None:
            raise RuntimeError("result is None")

        try:
            out = result["data"]["payload"]
        except Exception as e:
            raise RuntimeError(
                f'Unexpected error accessing result["data"]["payload"]. Result: {result}'
            ) from e
        try:
            real_out = decode_data(out)
            return real_out[0]
        except Exception as e:
            raise RuntimeError(
                f"Exception: {e=} {self._short_repr(out, max_length=100)}"
            ) from e


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
        # https://github.com/comfyanonymous/ComfyUI/blob/a178e25912b01abf436eba1cfaab316ba02d272d/nodes.py#L1511
        img = img.convert("RGB")
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


def _legacy_encode_comfy_image(image: torch.Tensor, image_format="png") -> str:
    input_image = image.cpu().detach().numpy()
    i = 255.0 * input_image[0]
    input_image = np.clip(i, 0, 255).astype(np.uint8)
    base64ed_image = encode_image_to_base64(
        Image.fromarray(input_image), format=image_format
    )
    return base64ed_image


def _legacy_decode_comfy_image(
    img_data: Union[List, str], image_format="png"
) -> torch.tensor:
    if isinstance(img_data, List):
        decoded_imgs = [decode_comfy_image(x, old_version=True) for x in img_data]

        combined_imgs = torch.cat(decoded_imgs, dim=0)
        return combined_imgs

    out = decode_base64_to_np(img_data, format=image_format)
    out = np.array(out).astype(np.float32) / 255.0
    output = torch.from_numpy(out)[None,]
    return output


def _new_encode_comfy_image(images: torch.Tensor, image_format="WEBP") -> str:
    """https://docs.comfy.org/essentials/custom_node_snippets#save-an-image-batch
    Encode a batch of images to base64 strings.

    Args:
        images (torch.Tensor): A batch of images.
        image_format (str, optional): The format of the images. Defaults to "WEBP".

    Returns:
        str: A JSON string containing the base64-encoded images.
    """
    results = {}
    for batch_number, image in enumerate(images):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        base64ed_image = encode_image_to_base64(img, format=image_format)
        results[batch_number] = base64ed_image

    return json.dumps(results)


def _new_decode_comfy_image(img_datas: str, image_format="WEBP") -> torch.tensor:
    """
    Decode a batch of base64-encoded images.

    Args:
        img_datas (str): A JSON string containing the base64-encoded images.
        image_format (str, optional): The format of the images. Defaults to "WEBP".

    Returns:
        torch.Tensor: A tensor containing the decoded images.
    """
    img_datas = json.loads(img_datas)

    decoded_imgs = []
    for img_data in img_datas.values():
        decoded_image = decode_base64_to_np(img_data, format=image_format)
        decoded_image = np.array(decoded_image).astype(np.float32) / 255.0
        decoded_imgs.append(torch.from_numpy(decoded_image)[None,])

    return torch.cat(decoded_imgs, dim=0)


def encode_comfy_image(
    image: torch.Tensor, image_format="WEBP", old_version=False
) -> str:
    if old_version:
        return _legacy_encode_comfy_image(image, image_format)
    return _new_encode_comfy_image(image, image_format)


def decode_comfy_image(
    img_data: Union[List, str], image_format="WEBP", old_version=False
) -> torch.tensor:
    if old_version:
        return _legacy_decode_comfy_image(img_data, image_format)
    return _new_decode_comfy_image(img_data, image_format)


def tensor_to_base64(tensor: torch.Tensor, compress=True) -> str:
    tensor_np = tensor.cpu().detach().numpy()

    tensor_bytes = pickle.dumps(tensor_np)
    if compress:
        tensor_bytes = zlib.compress(tensor_bytes)

    tensor_b64 = base64.b64encode(tensor_bytes).decode("utf-8")
    return tensor_b64


def base64_to_tensor(tensor_b64: str, compress=True) -> torch.Tensor:
    tensor_bytes = base64.b64decode(tensor_b64)

    if compress:
        tensor_bytes = zlib.decompress(tensor_bytes)

    tensor_np = pickle.loads(tensor_bytes)

    tensor = torch.from_numpy(tensor_np)
    return tensor


@singledispatch
def decode_data(input, old_version=False):
    raise NotImplementedError(f"Unsupported type: {type(input)}")


@decode_data.register(int)
@decode_data.register(float)
@decode_data.register(bool)
@decode_data.register(type(None))
def _(input, **kwargs):
    return input


@decode_data.register(dict)
def _(input, **kwargs):
    return {k: decode_data(v, **kwargs) for k, v in input.items()}


@decode_data.register(list)
def _(input, **kwargs):
    return [decode_data(x, **kwargs) for x in input]


@decode_data.register(str)
def _(input: str, **kwargs):
    if input.startswith(TENSOR_MARKER):
        tensor_b64 = input[len(TENSOR_MARKER) :]
        return base64_to_tensor(tensor_b64)
    elif input.startswith(IMAGE_MARKER):
        tensor_b64 = input[len(IMAGE_MARKER) :]
        old_version = kwargs.get("old_version", False)
        return decode_comfy_image(tensor_b64, old_version=old_version)
    return input


@singledispatch
def encode_data(output, disable_image_marker=False, old_version=False):
    raise NotImplementedError(f"Unsupported type: {type(output)}")


@encode_data.register(dict)
def _(output, **kwargs):
    return {k: encode_data(v, **kwargs) for k, v in output.items()}


@encode_data.register(list)
def _(output, **kwargs):
    return [encode_data(x, **kwargs) for x in output]


def is_image_tensor(tensor) -> bool:
    """https://docs.comfy.org/essentials/custom_node_datatypes#image

    Check if the given tensor is in the format of an IMAGE (shape [B, H, W, C] where C=3).

    `Args`:
        tensor (torch.Tensor): The tensor to check.

    `Returns`:
        bool: True if the tensor is in the IMAGE format, False otherwise.
    """
    try:
        if not isinstance(tensor, torch.Tensor):
            return False

        if len(tensor.shape) != 4:
            return False

        B, H, W, C = tensor.shape
        if C != 3:
            return False

        return True
    except Exception as e:
        return False


@encode_data.register(torch.Tensor)
def _(output, **kwargs):
    if is_image_tensor(output) and not kwargs.get("disable_image_marker", False):
        old_version = kwargs.get("old_version", False)
        return IMAGE_MARKER + encode_comfy_image(
            output, image_format="WEBP", old_version=old_version
        )
    return TENSOR_MARKER + tensor_to_base64(output)


@encode_data.register(BizyAirNodeIO)
def _(output: BizyAirNodeIO, **kwargs):
    origin_id = output.node_id
    origin_slot = output.nodes[origin_id]["outputs"]["slot_index"]
    return [origin_id, origin_slot]


@encode_data.register(int)
@encode_data.register(float)
@encode_data.register(bool)
@encode_data.register(type(None))
def _(output, **kwargs):
    return output


@encode_data.register(str)
def _(output, **kwargs):
    return output
