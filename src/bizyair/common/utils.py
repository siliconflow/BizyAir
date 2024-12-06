import copy
import json
import os
from typing import Any, List

import torch
import yaml


def truncate_long_strings(obj, max_length=50):
    if isinstance(obj, str):
        return obj if len(obj) <= max_length else obj[:max_length] + "..."
    elif isinstance(obj, dict):
        return {k: truncate_long_strings(v, max_length) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [truncate_long_strings(v, max_length) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(truncate_long_strings(v, max_length) for v in obj)
    elif isinstance(obj, torch.Tensor):
        return obj.shape, obj.dtype, obj.device
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


def recursive_extract_models(data: Any, prefix_path: str = "") -> List[str]:
    def merge_paths(base_path: str, new_path: Any) -> str:
        if not isinstance(new_path, str):
            return base_path
        return f"{base_path}/{new_path}" if base_path else new_path

    results: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = merge_paths(prefix_path, key)
            results.extend(recursive_extract_models(value, new_prefix))
    elif isinstance(data, list):
        for item in data:
            new_prefix = merge_paths(prefix_path, item)
            results.extend(recursive_extract_models(item, new_prefix))
    elif isinstance(data, str) and prefix_path.endswith(data):
        return [prefix_path]

    return results


def _load_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def _load_json_config(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def load_config_file(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    if file_path.endswith(".json"):
        return _load_json_config(file_path)
    elif file_path.endswith(".yaml"):
        return _load_yaml_config(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_path}")
