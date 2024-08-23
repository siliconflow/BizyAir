import importlib
import logging
import os
import threading
import warnings

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


class IDAllocator:
    # TODO Change to using Comfyui system ID
    _id_counter = 0
    _lock = threading.Lock()

    def __init__(self):
        with IDAllocator._lock:
            self._assigned_id = IDAllocator._id_counter
            IDAllocator._id_counter += 1

    @property
    def assigned_id(self):
        return str(self._assigned_id)


class BizyAirBaseNode(IDAllocator):
    def __init_subclass__(cls, **kwargs):
        if not cls.CATEGORY.startswith(f"{LOGO}{PREFIX}"):
            cls.CATEGORY = f"{LOGO}{PREFIX}/{cls.CATEGORY}"
        register_node(cls, PREFIX)
