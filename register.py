import threading
import nodes as comfy_nodes

LOGO = "☁️"
PREFIX = f"BizyAir"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def to_camel_case(s):
    return "".join(word.capitalize() for word in s.split("_"))


def validate_category(cls, prefix):
    assert cls.CATEGORY.startswith(f"☁️{prefix}")


def register_node(cls, prefix):
    class_name = cls.__name__
    assert class_name.startswith(
        f"{prefix}_"
    ), f"Class name '{class_name}' must start with prefix '{prefix}_'"

    if hasattr(cls, "NODE_DISPLAY_NAME"):
        display_name = cls.NODE_DISPLAY_NAME
        assert display_name.startswith(
            f"{LOGO}{prefix}"
        ), f"Display name '{display_name}' must start with '{LOGO}{prefix}'"
    else:
        base_name = class_name[len(prefix) + 1 :]
        if base_name in comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS:
            display_name = (
                f"{LOGO}{prefix} {comfy_nodes.NODE_DISPLAY_NAME_MAPPINGS[base_name]}"
            )
        else:
            display_name = f"{LOGO}{prefix} {base_name}"
            print(
                f"Warning: Display name '{display_name}' might differ from the native display name."
            )

    NODE_CLASS_MAPPINGS[class_name] = cls
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name




class IDAllocator:
    _id_counter = 0
    _lock = threading.Lock()

    def __init__(self):
        with IDAllocator._lock:
            self._assigned_id = IDAllocator._id_counter
            IDAllocator._id_counter += 1

    @property
    def assigned_id(self):
        print(f"{self._assigned_id=}")
        return str(self._assigned_id)


class BizyAirBaseNode(IDAllocator):
    def __init_subclass__(cls, **kwargs):
        validate_category(cls, PREFIX)
        register_node(cls, PREFIX)
