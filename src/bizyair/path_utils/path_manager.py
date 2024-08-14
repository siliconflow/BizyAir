from collections.abc import Collection
import copy
import os
import yaml
import json
from typing import Any, Dict, List
from ..common import fetch_models_by_type

supported_pt_extensions: set[str] = {
    ".ckpt",
    ".pt",
    ".bin",
    ".pth",
    ".safetensors",
    ".pkl",
    ".sft",
}
ScanPathType = list[str]
folder_names_and_paths: dict[str, ScanPathType] = {}
filename_path_mapping: dict[str, dict[str, str]] = {}


def _get_config_path():
    src_bizyair_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    configs_path = os.path.join(src_bizyair_path, "configs")
    return configs_path


configs_path = _get_config_path()


def filter_files_extensions(
    files: Collection[str], extensions: Collection[str]
) -> list[str]:
    return sorted(
        list(
            filter(
                lambda a: os.path.splitext(a)[-1].lower() in extensions
                or len(extensions) == 0,
                files,
            )
        )
    )


def load_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def guess_config(
    *,
    ckpt_name: str = None,
    unet_name: str = None,
    vae_name: str = None,
    clip_name: str = None,
) -> str:
    # Debug
    return os.path.join(configs_path, "sdxl_config.yaml")

    if ckpt_name is not None and ckpt_name.lower().startswith("sdxl"):
        return os.path.join(configs_path, "sdxl_config.yaml")
    if unet_name is not None and unet_name.lower().startswith("kolors"):
        return os.path.join(configs_path, "kolors_config.yaml")
    if vae_name is not None and vae_name.lower().startswith(
        "sdxl/sdxl_vae.safetensors"
    ):
        return os.path.join(configs_path, "kolors_config.yaml")
    if unet_name is not None and unet_name.lower().startswith("flux/flux1-dev.sft"):
        return os.path.join(configs_path, "flux_dev_config.yaml")
    if unet_name is not None and unet_name.lower().startswith("flux/flux1-schnell.sft"):
        return os.path.join(configs_path, "flux_config.yaml")
    if vae_name is not None and vae_name.lower().startswith("flux/ae.sft"):
        return os.path.join(configs_path, "flux_config.yaml")


def get_config_file_list(base_path=None) -> list:
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(configs_path)
    extensions = ".yaml"
    config_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                config_files.append(file_path)
    return config_files


models_config: Dict[str, Dict[str, Any]] = load_yaml_config(
    os.path.join(configs_path, "models.yaml")
)


def cached_filename_list(
    folder_name: str, verbose=True
) -> tuple[list[str], dict[str, float], float] | None:
    global filename_path_mapping
    if folder_name not in filename_path_mapping:
        mod_service_config = models_config["service_config"]
        url = f"{mod_service_config['service_address']}{mod_service_config['route']}"
        model_types: Dict[str, str] = models_config["model_types"]
        msg = fetch_models_by_type(url=url, model_type=model_types[folder_name])
        if verbose:
            print(f"cached_filename_list {msg=}")

        filename_path_mapping[folder_name] = {
            x["label_path"]: x["real_path"] for x in msg["data"] if x["label_path"]
        }

    return list(
        filter_files_extensions(
            filename_path_mapping[folder_name].keys(),
            extensions=supported_pt_extensions,
        )
    )


def convert_prompt_label_path_to_real_path(
    prompt: dict[str, dict[str, any]], inplace: bool = True
) -> dict:
    # TODO fix Temporarily write dead
    if not inplace:
        prompt = copy.deepcopy(prompt)

    for unique_id in prompt:
        inputs = prompt[unique_id]["inputs"]
        if (
            "lora_name" in inputs
            and inputs["lora_name"] in filename_path_mapping["loras"]
        ):
            lora_name = inputs["lora_name"]
            inputs["lora_name"] = filename_path_mapping["loras"][lora_name]

    return prompt


def get_filename_list(folder_name, *, verbose=False):
    global folder_names_and_paths
    results = []
    if folder_name in models_config["model_types"]:
        results.extend(cached_filename_list(folder_name, verbose=verbose))
    results.extend(folder_names_and_paths[folder_name])
    return results


def recursive_extract_models(data: Any, prefix_path: str = "") -> List[str]:
    def merge_paths(base_path: str, new_path: str) -> str:
        if base_path == "":
            return new_path
        else:
            return f"{base_path}/{new_path}"

    results: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            results.extend(
                recursive_extract_models(value, merge_paths(prefix_path, key))
            )
    elif isinstance(data, list):
        for item in data:
            results.extend(
                recursive_extract_models(item, merge_paths(prefix_path, str(item)))
            )
    elif isinstance(data, str) and prefix_path.endswith(data):
        return filter_files_extensions([prefix_path], supported_pt_extensions)

    return results


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def init_config():
    global folder_names_and_paths
    models_file = os.path.join(configs_path, "models.json")
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
    # print(folder_names_and_paths)
    api_key = os.getenv("BIZYAIR_KEY", "")
    host_ckpts = get_filename_list("loras", verbose=True)
    print(host_ckpts)
