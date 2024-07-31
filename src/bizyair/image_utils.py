import base64
from enum import Enum
import io
import json
import os
import pickle
from functools import singledispatch
from typing import Any, List, Union
import zlib
import numpy as np
import torch
from PIL import Image
import yaml
from .client import BizyAirStreamClient, BizyAirRequestClient

# Marker to identify base64-encoded tensors
TENSOR_MARKER = "TENSOR:"
BIZYAIR_DEBUG = os.getenv("BIZYAIR_DEBUG", False)
from typing import Dict


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


def set_api_key(API_KEY="YOUR_API_KEY"):
    BizyAirNodeIO.API_KEY = API_KEY


class BizyAirNodeIO:
    API_KEY = os.getenv("BIZYAIR_API_KEY", "YOUR_API_KEY")

    def __init__(
        self,
        node_id: int = "0",
        nodes: Dict[str, Dict[str, any]] = {},
        config_file=None,
        configs: dict = None,
        debug: bool = os.getenv("BIZYAIR_DEBUG", False),
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
        # TODO (refine)
        return {"prompt": self.nodes, "last_node_id": self.node_id}

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

        return {"prompt": workflow, "last_node_id": node_id_mapping[self.node_id]}

    def add_node_data(
        self, class_type: str, inputs: Dict[str, Any], outputs: Dict[str, Any]
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
                f"API key is not set. Please provide a valid API key, {self.API_KEY=}"
            )

        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.API_KEY}",
        }

    def service_route(self):
        service_config = self.configs["service_config"]
        real_service_route = service_config["service_address"] + service_config["route"]
        return real_service_route

    def send_request(
        self, url=None, headers=None, *, progress_callback=None, stream=False
    ) -> any:
        # self._short_repr(self.nodes, max_length=100)
        # self._short_repr(self.workflow_api['prompt'], max_length=100)
        api_url = self.service_route()
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
            client = BizyAirRequestClient(
                api_url, self.workflow_api, BizyAirNodeIO.API_KEY
            )
            response_data = client.send_request()
            result = json.loads(response_data)

        if result is None:
            raise RuntimeError("result is None")

        if "result" in result:  # cloud
            msg = json.loads(result["result"])
            try:
                out = msg["data"]["payload"]
            except Exception as e:
                raise RuntimeError(
                    f'Unexpected error accessing result["data"]["payload"]. Result: {msg}'
                ) from e

        else:  # local
            try:
                out = result["data"]["payload"]
            except Exception as e:
                raise RuntimeError(
                    f'Unexpected error accessing result["data"]["payload"]. Result: {result}'
                ) from e

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
    output = torch.from_numpy(out)[None,]
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
