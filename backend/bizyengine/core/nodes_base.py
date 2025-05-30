import importlib
import logging
import warnings
from functools import wraps
from typing import List

from bizyengine.core.common.env_var import BIZYAIR_DEBUG, BIZYAIR_SERVER_MODE
from bizyengine.core.configs.conf import config_manager
from server import PromptServer

from .common.client import get_api_key
from .data_types import is_send_request_datatype
from .nodes_io import BizyAirNodeIO, create_node_data

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

BIZYAIR_PROMPT_KEY = "bizyair_prompt"
BIZYAIR_PARAM_MAGIC_NODE_ID = "bizyair_magic_node"


def pop_api_key_and_prompt_id(kwargs):
    extra_data = {}
    prompt = None
    if BIZYAIR_PROMPT_KEY in kwargs:
        prompt = kwargs.pop(BIZYAIR_PROMPT_KEY)
    if BIZYAIR_SERVER_MODE:
        if BIZYAIR_PARAM_MAGIC_NODE_ID in prompt:
            extra_data["api_key"] = prompt[BIZYAIR_PARAM_MAGIC_NODE_ID]["_meta"][
                "api_key"
            ]
            extra_data["prompt_id"] = prompt[BIZYAIR_PARAM_MAGIC_NODE_ID]["_meta"][
                "prompt_id"
            ]
            logging.debug(
                "Using server mode passed in prompt_id: " + extra_data["prompt_id"]
            )
    else:
        extra_data["api_key"] = get_api_key()
        if (
            PromptServer.instance is not None
            and PromptServer.instance.last_prompt_id is not None
        ):
            extra_data["prompt_id"] = PromptServer.instance.last_prompt_id
            print("Processing prompt with ID: " + PromptServer.instance.last_prompt_id)

    return extra_data


def process_kwargs(kwargs):
    possibleWidgetNames = [
        "model_name",
        "instantid_file",
        "pulid_file",
        "style_model_name",
    ]

    model_version_id = kwargs.get("model_version_id", "")
    if model_version_id:
        name = f"{config_manager.get_model_version_id_prefix()}{model_version_id}"
        for key in possibleWidgetNames:
            if key in kwargs:
                kwargs[key] = name
    return kwargs


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


def ensure_unique_id(org_func, original_has_unique_id=False):
    @wraps(org_func)
    def new_func(self, **kwargs):
        if original_has_unique_id:
            self._assigned_id = kwargs.get("unique_id", "UNIQUE_ID")
        elif "unique_id" in kwargs:
            self._assigned_id = kwargs.pop("unique_id")
        return org_func(self, **kwargs)

    return new_func


def ensure_hidden_unique_id_and_prompt(org_input_types_func):
    original_has_unique_id = False

    @wraps(org_input_types_func)
    def new_input_types_func():
        nonlocal original_has_unique_id

        result = org_input_types_func()
        if "hidden" not in result:
            result["hidden"] = {"unique_id": "UNIQUE_ID"}
        elif "unique_id" not in result["hidden"]:
            result["hidden"]["unique_id"] = "UNIQUE_ID"
        else:
            original_has_unique_id = True
        # Also set prompt, but to avoid naming conflict prefix with 'bizyair'
        if BIZYAIR_PROMPT_KEY not in result["hidden"]:
            result["hidden"][BIZYAIR_PROMPT_KEY] = "PROMPT"
        return result

    # Ensure original_has_unique_id is correctly set before returning
    new_input_types_func()
    return new_input_types_func, original_has_unique_id


class BizyAirBaseNode:
    FUNCTION = "default_function"

    def __init_subclass__(cls, **kwargs):
        if not cls.CATEGORY.startswith(f"{LOGO}{PREFIX}"):
            cls.CATEGORY = f"{LOGO}{PREFIX}/{cls.CATEGORY}"
        register_node(cls, PREFIX)
        cls.setup_input_types()

        # TODO refine 验证FUNCTION接受**kwargs
        if BIZYAIR_DEBUG:
            import inspect

            sig = inspect.signature(getattr(cls, cls.FUNCTION))
            params = sig.parameters.values()
            assert any([True for p in params if p.kind == p.VAR_KEYWORD])

    @classmethod
    def setup_input_types(cls):
        # https://docs.comfy.org/custom-nodes/backend/more_on_inputs#hidden-and-flexible-inputs
        new_input_types_func, original_has_unique_id = (
            ensure_hidden_unique_id_and_prompt(cls.INPUT_TYPES)
        )
        cls.INPUT_TYPES = new_input_types_func
        setattr(
            cls,
            cls.FUNCTION,
            ensure_unique_id(getattr(cls, cls.FUNCTION), original_has_unique_id),
        )

    @property
    def assigned_id(self):
        assert self._assigned_id is not None and isinstance(self._assigned_id, str)
        return str(self._assigned_id)

    def default_function(self, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        class_type = self._determine_class_type()
        kwargs = process_kwargs(kwargs)
        node_ios = self._process_non_send_request_types(class_type, kwargs)
        # TODO: add processing for send_request_types
        send_request_datatype_list = self._get_send_request_datatypes()
        if len(send_request_datatype_list) == len(self.RETURN_TYPES):
            return self._process_all_send_request_types(node_ios, **extra_data)
        return node_ios

    def _get_send_request_datatypes(self):
        return [
            return_type
            for return_type in self.RETURN_TYPES
            if is_send_request_datatype(return_type)
        ]

    def _determine_class_type(self):
        class_type = getattr(self, "CLASS_TYPE_NAME", type(self).__name__)
        if class_type.startswith(f"{PREFIX}_"):
            class_type = class_type[len(PREFIX) + 1 :]
        return class_type

    def _process_non_send_request_types(self, class_type, kwargs):
        outs = []
        for slot_index, _ in enumerate(self.RETURN_TYPES):
            node = BizyAirNodeIO(node_id=self.assigned_id, nodes={})
            node.add_node_data(
                class_type=class_type, inputs=kwargs, outputs={"slot_index": slot_index}
            )
            outs.append(node)
        return tuple(outs)

    def _process_all_send_request_types(self, node_ios: List[BizyAirNodeIO], **kwargs):
        out = node_ios[0].send_request(**kwargs)
        assert len(out) == len(self.RETURN_TYPES)
        return out


class BizyAirMiscBaseNode:
    # 作为Misc节点基类来保证hidden prompt, unique id存在
    def __init_subclass__(cls, **kwargs):
        if hasattr(cls, "CATEGORY"):
            if not cls.CATEGORY.startswith(f"{LOGO}{PREFIX}"):
                cls.CATEGORY = f"{LOGO}{PREFIX}/{cls.CATEGORY}"
        cls.setup_input_types()

        # 验证FUNCTION接受**kwargs
        if BIZYAIR_DEBUG:
            import inspect

            sig = inspect.signature(getattr(cls, cls.FUNCTION))
            params = sig.parameters.values()
            assert any([True for p in params if p.kind == p.VAR_KEYWORD])

    @classmethod
    def setup_input_types(cls):
        if not hasattr(cls, "INPUT_TYPES"):
            cls.INPUT_TYPES = lambda: {}
        # https://docs.comfy.org/custom-nodes/backend/more_on_inputs#hidden-and-flexible-inputs
        new_input_types_func, original_has_unique_id = (
            ensure_hidden_unique_id_and_prompt(cls.INPUT_TYPES)
        )
        cls.INPUT_TYPES = new_input_types_func
        setattr(
            cls,
            cls.FUNCTION,
            ensure_unique_id(getattr(cls, cls.FUNCTION), original_has_unique_id),
        )
