import os
import yaml
import json
from pathlib import Path
from typing import Any, List

ScanPathType = list[str]
folder_names_and_paths: dict[str, ScanPathType] = {}
base_path = os.path.dirname(os.path.abspath(__file__))


def load_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def guess_config(
    *, ckpt_name: str = None, unet_name: str = None, vae_name: str = None
) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    if ckpt_name is not None and ckpt_name.lower().startswith("sdxl"):
        return os.path.join(base_path, "configs", "sdxl_config.yaml")
    if unet_name is not None and unet_name.lower().startswith("kolors"):
        return os.path.join(base_path, "configs", "kolors_config.yaml")
    if vae_name is not None and vae_name.lower().startswith(
        "sdxl/sdxl_vae.safetensors"
    ):
        return os.path.join(base_path, "configs", "kolors_config.yaml")
    raise RuntimeError()


def get_config_file_list(base_path=None) -> list:
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, "configs")
    extensions = ".yaml"
    config_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                config_files.append(file_path)
    return config_files


def get_filename_list(folder_name):
    global folder_names_and_paths
    return folder_names_and_paths[folder_name]


def recursive_extract_models(data: Any, prefix_path: Path = Path(".")) -> List[str]:
    def extract_from_dict(d: dict, path: Path) -> List[str]:
        results: List[str] = []
        for key, value in d.items():
            results.extend(recursive_extract_models(value, path / key))
        return results

    def extract_from_list(l: list, path: Path) -> List[str]:
        results: List[str] = []
        for item in l:
            results.extend(recursive_extract_models(item, path / str(item)))
        return results

    if isinstance(data, dict):
        return extract_from_dict(data, prefix_path)
    elif isinstance(data, list):
        return extract_from_list(data, prefix_path)

    if str(prefix_path) == ".":
        return []
    else:
        return [str(prefix_path)]


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def init_config():
    global folder_names_and_paths
    models_file = os.path.join(base_path, "configs", "models.json")
    models_data = load_json(models_file)
    for k, v in models_data.items():
        if k not in folder_names_and_paths:
            folder_names_and_paths[k] = []
        folder_names_and_paths[k].extend(recursive_extract_models(v))


init_config()

if __name__ == "__main__":
    # print(f"Loaded config from {get_config_file_list()}")
    # configs = [load_yaml_config(x) for x in get_config_file_list()]
    # print(get_filename_list("clip_vision"))
    print(folder_names_and_paths)
