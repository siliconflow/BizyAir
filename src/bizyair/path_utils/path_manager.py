import copy
import json
import os
import pprint
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from ..common import fetch_models_by_type
from ..common.env_var import BIZYAIR_DEBUG, BIZYAIR_SERVER_ADDRESS
from .utils import filter_files_extensions, get_service_route, load_yaml_config

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


@dataclass
class RefreshSettings:
    loras: bool = True

    def get(self, folder_name: str, default: bool = True):
        return getattr(self, folder_name, default)

    def set(self, folder_name: str, value: bool):
        setattr(self, folder_name, value)


refresh_settings = RefreshSettings()


def enable_refresh_options(folder_names: Union[str, list[str]]):
    if isinstance(folder_names, str):
        folder_names = [folder_names]
    for folder_name in folder_names:
        refresh_settings.set(folder_name, True)


def disable_refresh_options(folder_names: Union[str, list[str]]):
    if isinstance(folder_names, str):
        folder_names = [folder_names]
    for folder_name in folder_names:
        refresh_settings.set(folder_name, False)


def _get_config_path():
    src_bizyair_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    configs_path = os.path.join(src_bizyair_path, "configs")
    return configs_path


configs_path = _get_config_path()

models_config: Dict[str, Dict[str, Any]] = load_yaml_config(
    os.path.join(configs_path, "models.yaml")
)


def guess_url_from_node(
    node: Dict[str, Dict[str, Any]], node_usage_state
) -> Union[str, None]:
    if "loader" in node["class_type"].lower():
        for attr in ("ckpt_name", "unet_name", "vae_name"):
            if attr in node["inputs"]:
                input_name = node["inputs"][attr].lower()

                routing_rules = models_config["routing_rules"]
                routing_configs = models_config["routing_configs"]
                for rule in routing_rules:
                    if re.match(rule["pattern"], input_name):
                        config_key = rule["config"]
                        configs = routing_configs[config_key]
                        # TODO fix
                        if config_key == "flux-dev":
                            if (
                                node["inputs"]["weight_dtype"] == "fp8_e4m3fn"
                                or node_usage_state.loras
                            ):
                                node["inputs"][
                                    "weight_dtype"
                                ] = "fp8_e4m3fn"  # set to fp8_e4m3fn for lora
                                return (
                                    configs.get(
                                        "service_address", BIZYAIR_SERVER_ADDRESS
                                    )
                                    + "/supernode/flux-dev-bizyair-comfy-ksampler-fp8-v2"
                                )
                        return get_service_route(configs)


def guess_config(
    *,
    ckpt_name: str = None,
    unet_name: str = None,
    vae_name: str = None,
    clip_name: str = None,
) -> str:
    warnings.warn("The interface has changed, please do not use it", DeprecationWarning)


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


def cached_filename_list(
    folder_name: str, *, share_id: str = None, verbose=False, refresh=False
) -> list[str]:
    global filename_path_mapping
    if refresh or folder_name not in filename_path_mapping:
        model_types: Dict[str, str] = models_config["model_types"]
        if share_id:
            url = f"{BIZYAIR_SERVER_ADDRESS}/{share_id}/models/files"
        else:
            url = get_service_route(models_config["model_hub"]["find_model"])
        msg = fetch_models_by_type(
            url=url, method="GET", model_type=model_types[folder_name]
        )
        if verbose:
            pprint.pprint({"cached_filename_list": msg})

        try:
            if not msg or "data" not in msg or msg["data"] is None:
                return []

            filename_path_mapping[folder_name] = {
                x["label_path"]: x["real_path"]
                for x in msg["data"]["files"]
                if x["label_path"]
            }
        except Exception as e:
            warnings.warn(f"Failed to get filename list: {e}")
            return []
        finally:
            # TODO fix share_id vaild refresh settings
            if share_id is None:
                disable_refresh_options(folder_name)

    return list(
        filter_files_extensions(
            filename_path_mapping[folder_name].keys(),
            extensions=supported_pt_extensions,
        )
    )


def convert_prompt_label_path_to_real_path(prompt: dict[str, dict[str, any]]) -> dict:
    # TODO fix Temporarily write dead
    new_prompt = {}
    for unique_id in prompt:
        new_prompt[unique_id] = copy.copy(prompt[unique_id])
        inputs = copy.copy(prompt[unique_id]["inputs"])
        if "lora_name" in inputs:
            lora_name = inputs["lora_name"]
            new_lora_name = filename_path_mapping.get("loras", {}).get(lora_name, None)
            if new_lora_name:
                inputs["lora_name"] = new_lora_name
            else:
                file_list = get_filename_list("loras")
                if lora_name not in file_list:
                    raise ValueError(
                        f"Lora name '{lora_name}' not found in file list. Available lora names: {', '.join(file_list)}"
                    )

        new_prompt[unique_id]["inputs"] = inputs
    return new_prompt


def get_share_filename_list(folder_name, share_id, *, verbose=BIZYAIR_DEBUG):
    assert share_id is not None and isinstance(share_id, str)
    # TODO fix share_id vaild refresh settings
    return cached_filename_list(
        folder_name, share_id=share_id, verbose=verbose, refresh=True
    )


def get_filename_list(folder_name, *, verbose=BIZYAIR_DEBUG):

    global folder_names_and_paths
    results = []
    if folder_name in models_config["model_types"]:
        refresh = refresh_settings.get(folder_name, True)
        results.extend(
            cached_filename_list(folder_name, verbose=verbose, refresh=refresh)
        )
    if folder_name in folder_names_and_paths:
        results.extend(folder_names_and_paths[folder_name])
    if BIZYAIR_DEBUG:
        try:
            import folder_paths

            results.extend(folder_paths.get_filename_list(folder_name))
        except:
            pass
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
    if BIZYAIR_DEBUG:
        pprint.pprint("=" * 20 + "init_config: " + "=" * 20)
        pprint.pprint(folder_names_and_paths)


init_config()


if __name__ == "__main__":
    # print(f"Loaded config from {get_config_file_list()}")
    # configs = [load_yaml_config(x) for x in get_config_file_list()]
    # print(get_filename_list("clip_vision"))
    # print(folder_names_and_paths)

    api_key = os.getenv("BIZYAIR_API_KEY", "")
    host_ckpts = get_filename_list("loras", verbose=True)
    print(host_ckpts)
