import copy
from typing import Any

import torch


def truncate_long_strings(obj, max_length=50):
    if isinstance(obj, str):
        return obj if len(obj) <= max_length else obj[:max_length] + "..."
    elif isinstance(obj, dict):
        return {k: truncate_long_strings(v, max_length) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [truncate_long_strings(v, max_length) for v in obj]
    else:
        return obj


def deepcopy_except_tensor(obj, exclude_types=[torch.Tensor]):
    return deepcopy_except_types(obj=obj, exclude_types=exclude_types)


def deepcopy_except_types(obj, exclude_types):
    """
    Recursively copy an object, excluding specified data types.

    :param obj: The object to be copied
    :param exclude_types: A list of data types to be excluded from deep copying
    :return: The copied object
    """
    if any(isinstance(obj, t) for t in exclude_types):
        return obj  # Return the object directly without deep copying
    elif isinstance(obj, (list, tuple)):
        return type(obj)(deepcopy_except_types(item, exclude_types) for item in obj)
    elif isinstance(obj, dict):
        return {
            deepcopy_except_types(key, exclude_types): deepcopy_except_types(
                value, exclude_types
            )
            for key, value in obj.items()
        }
    else:
        return copy.deepcopy(obj)

def is_comfy_transferrable(obj: Any) -> bool:
    """
    Check if the object is a transferrable type.
    """   
    if isinstance(obj, (torch.Tensor, str, int, float, bool)):
        return True
    elif isinstance(obj, tuple):
        return all(is_comfy_transferrable(item) for item in obj)
    elif isinstance(obj, list):
        return all(is_comfy_transferrable(item) for item in obj)
    elif isinstance(obj, dict):
        return all(is_comfy_transferrable(item) for item in obj.values())
    else:
        return False