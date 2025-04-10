import copy
import json
import os
import pprint
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Collection, Dict, List, Union

from bizyengine.core.common import client, fetch_models_by_type
from bizyengine.core.common.env_var import BIZYAIR_DEBUG, BIZYAIR_SERVER_ADDRESS
from bizyengine.core.configs.conf import ModelRule, config_manager
from bizyengine.core.path_utils.utils import (
    filter_files_extensions,
    get_service_route,
    load_yaml_config,
)

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
folder_names_and_paths: dict[str, ScanPathType] = defaultdict(list)
filename_path_mapping: dict[str, dict[str, str]] = {}


@dataclass
class RefreshSettings:
    loras: bool = True
    controlnet: bool = True

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


def detect_model(model_version_id, detection_type, **kwargs):
    return "SDXL"
    # TODO support detect_model_type
    # json_data = {
    #     "prompt": {
    #         "model_version_id": model_version_id,
    #         "detection_type": detection_type,
    #     },
    #     "exec_info": {"api_key": client.get_api_key()},
    # }
    # detect_model_type: dict = models_config["model_version_config"]["detect_model_type"]
    # resq = client.send_request(
    #     url=detect_model_type["url"], data=json.dumps(json_data).encode("utf-8")
    # )
    # if resq["type"] != "success":
    #     raise RuntimeError(
    #         f"Request failed: {resq.get('type', 'unknown error')} - {resq.get('message', 'No details available')}"
    #     )

    # payload = resq["data"]["payload"]

    # model_type = payload.get("model_type")
    # return model_type


def action_call(action: str, *args, **kwargs) -> any:
    if action == "detect_model":
        return detect_model(*args, **kwargs)


def guess_url_from_node(
    node: Dict[str, Dict[str, Any]], class_type_table: Dict[str, bool]
) -> Union[List[ModelRule], None]:
    rules: List[ModelRule] = config_manager.get_rules(node["class_type"])
    out = []
    model_version_id_prefix = models_config["model_version_config"][
        "model_version_id_prefix"
    ]
    model_type = None
    for rule in rules:
        if len(rule.inputs) == 0:
            out.append(rule)

        skip = False
        for key, patterns in rule.inputs.items():
            if skip:
                break
            for pattern in patterns:
                value = node["inputs"][key]
                if isinstance(pattern, str) and re.search(pattern, value) is not None:
                    out.append(rule)
                    skip = True
                    break
                elif isinstance(pattern, dict) and value.startswith(
                    model_version_id_prefix
                ):
                    action = pattern["action"]
                    detection_type = pattern["detection_type"]
                    model_type = action_call(
                        action=action,
                        model_version_id=value[len(model_version_id_prefix) :],
                        detection_type=detection_type,
                    )
        if model_type and model_type == rule.base_model:
            out.append(rule)

    return out


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

        for key, folder_name in [
            ("lora_name", "loras"),
            ("control_net_name", "controlnet"),
        ]:
            if key in inputs:
                value = inputs[key]
                new_value = filename_path_mapping.get(folder_name, {}).get(value, None)
                if new_value:
                    inputs[key] = new_value
                else:
                    file_list = get_filename_list(folder_name)
                    if value not in file_list:
                        raise ValueError(
                            f"{key} '{value}' not found in file list. Available {key} names: {', '.join(file_list)}"
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
    results = folder_names_and_paths.get(folder_name, [])
    # 社区node上线后移除
    # if folder_name in models_config["model_types"]:
    #     refresh = refresh_settings.get(folder_name, True)
    #     results.extend(
    #         cached_filename_list(folder_name, verbose=verbose, refresh=refresh)
    #     )
    # if folder_name in folder_names_and_paths:
    #     results.extend(folder_names_and_paths[folder_name])
    # if BIZYAIR_DEBUG:
    #     try:
    #         import folder_paths
    #
    #         results.extend(folder_paths.get_filename_list(folder_name))
    #     except:
    #         pass
    return results


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
        return filter_files_extensions([prefix_path], supported_pt_extensions)

    return results


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def init_config():
    global folder_names_and_paths
    for k, filenames in config_manager.model_path_manager.model_paths.items():
        folder_names_and_paths[k].extend(filenames)
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
