import importlib
import logging
import warnings
from functools import wraps
from typing import Any, Dict, List

from .commands import invoker
from .common.utils import is_comfy_transferrable
from .data_types import is_send_request_datatype
from .image_utils import decode_data, encode_data
from .nodes_io import BizyAirNodeIO

try:
    comfy_nodes = importlib.import_module("nodes")
except ModuleNotFoundError:
    warnings.warn("Importing comfyui.nodes failed!")
    comfy_nodes = type("nodes", (object,), {"NODE_DISPLAY_NAME_MAPPINGS": {}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOGO = "☁️"
PREFIX = f"BizyAir"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def to_camel_case(s):
    return "".join(word.capitalize() for word in s.split("_"))


def validate_category(cls, prefix):
    assert cls.CATEGORY.startswith(f"☁️{prefix}")


def register_node(cls, prefix):
    class_name = (
        f"{prefix}_{cls.__name__}"
        if not cls.__name__.startswith(prefix)
        else cls.__name__
    )
    logger.debug(
        f"Class: {cls}, Name: {class_name}, Has DISPLAY_NAME: {hasattr(cls, 'NODE_DISPLAY_NAME')}"
    )

    if hasattr(cls, "NODE_DISPLAY_NAME"):
        display_name = cls.NODE_DISPLAY_NAME
        if not display_name.startswith(f"{LOGO}{prefix}"):
            display_name = f"{LOGO}{prefix} {display_name}"
    else:
        base_name = class_name[len(prefix) + 1 :]
        if base_name in comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS:
            display_name = (
                f"{LOGO}{prefix} {comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS[base_name]}"
            )
        else:
            display_name = f"{LOGO}{prefix} {base_name}"
            logger.warning(
                f"Display name '{display_name}' might differ from the native display name."
            )

    NODE_CLASS_MAPPINGS[class_name] = cls
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name


def ensure_unique_id(org_func: callable, original_hidden: Dict = {}):

    hidden_fields = {
        "unique_id": "UNIQUE_ID",
        "prompt": "PROMPT",
        "extra_pnginfo": "EXTRA_PNGINFO",
    }

    @wraps(org_func)
    def wrapped_func(self, **kwargs):
        # Ensure only new hidden fields are added, existing ones are not popped
        if not hasattr(self, "_hidden"):
            self._hidden = {}
        for key in hidden_fields:
            if key not in original_hidden:
                self._hidden[key] = kwargs.pop(key, None)
            else:
                self._hidden[key] = kwargs[key]
        return org_func(self, **kwargs)

    return wrapped_func


def ensure_hidden_unique_id(org_input_types_func: callable):
    hidden_fields = {
        "unique_id": "UNIQUE_ID",
        "prompt": "PROMPT",
        "extra_pnginfo": "EXTRA_PNGINFO",
    }

    @wraps(org_input_types_func)
    def wrapped_input_types_func():
        result = org_input_types_func()
        result.setdefault("hidden", {}).update(hidden_fields)
        return result

    return wrapped_input_types_func


class BizyAirBaseNode:
    FUNCTION = "default_function"
    subscriber = None

    def __init_subclass__(cls, **kwargs):
        if getattr(cls, "FUNCTION", None) is None:
            cls.FUNCTION = "default_function"

        if not cls.CATEGORY.startswith(f"{LOGO}{PREFIX}"):
            cls.CATEGORY = f"{LOGO}{PREFIX}/{cls.CATEGORY}"
        register_node(cls, PREFIX)
        cls.setup_input_types()
        # elif cls.FUNCTION != "default_function":
        #     original_function = getattr(cls, cls.FUNCTION)

        #     def run_function(self, **kwargs):
        #         return original_function(self, **kwargs)

        #     setattr(cls, cls.FUNCTION, run_function)

    @classmethod
    def setup_input_types(cls):
        # https://docs.comfy.org/essentials/custom_node_more_on_inputs#hidden-inputs
        original_hidden = cls.INPUT_TYPES().get("hidden", {})
        new_input_types_func = ensure_hidden_unique_id(cls.INPUT_TYPES)
        cls.INPUT_TYPES = new_input_types_func
        setattr(
            cls,
            cls.FUNCTION,
            ensure_unique_id(getattr(cls, cls.FUNCTION), original_hidden),
        )

    @property
    def assigned_id(self):
        assert self._hidden is not None
        return self._hidden["unique_id"]

    def _merge_results(self, result: List[List[Any]], node_ios: List[BizyAirNodeIO]):
        assert len(result) == len(node_ios)
        return [x[0] if x is not None else y for x, y in zip(result, node_ios)]

    def _should_pre_run(self):
        subscriber = BizyAirBaseNode.subscriber
        return subscriber is not None and self.assigned_id in subscriber.prompt

    def _pre_run(self, timeout=86400):
        subscriber = BizyAirBaseNode.subscriber
        result = subscriber.get_result(self.assigned_id, timeout=timeout)
        return decode_data(result)

    def default_function(self, **kwargs):
        class_type = self._determine_class_type()
        send_request_datatype_list = self._get_send_request_datatypes()
        node_ios: List[BizyAirNodeIO] = self._process_non_send_request_types(
            class_type, kwargs
        )
        if self._should_pre_run():
            result = self._pre_run()
            if result:
                return self._merge_results(result, node_ios)
            else:
                warnings.warn("Pre-run result is None")

        if len(send_request_datatype_list) == len(self.RETURN_TYPES):
            return self._process_all_send_request_types(node_ios)
        elif len(send_request_datatype_list) > 0:
            return self._process_partial_send_request_types(node_ios)
        else:
            return node_ios

    def _determine_class_type(self):
        class_type = type(self).__name__
        if class_type.startswith(f"{PREFIX}_"):
            class_type = class_type[len(PREFIX) + 1 :]
        return class_type

    def _get_send_request_datatypes(self):
        return [
            return_type
            for return_type in self.RETURN_TYPES
            if is_send_request_datatype(return_type)
        ]

    def _process_all_send_request_types(self, node_ios: List[BizyAirNodeIO]):
        return node_ios[0].send_request()

    def _process_partial_send_request_types(self, node_ios: List[BizyAirNodeIO]):
        # TODO: Implement handling for partial send request datatypes
        # https://docs.comfy.org/essentials/javascript_objects_and_hijacking#properties-2
        pre_prompt = node_ios[0].nodes
        pre_prompt = encode_data(pre_prompt)
        subscriber = invoker.prompt_sse_server.execute(
            pre_prompt=pre_prompt, hidden=self._hidden
        )
        result = subscriber.get_result(self.assigned_id, timeout=240 * 60)
        result = decode_data(result)
        BizyAirBaseNode.subscriber = subscriber
        return self._merge_results(result, node_ios)

    def _process_non_send_request_types(self, class_type, kwargs):
        outs = []
        for slot_index, _ in enumerate(self.RETURN_TYPES):
            node = BizyAirNodeIO(node_id=self.assigned_id, nodes={})
            node.add_node_data(
                class_type=class_type, inputs=kwargs, outputs={"slot_index": slot_index}
            )
            outs.append(node)
        return tuple(outs)
