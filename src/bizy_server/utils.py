import os
from pathlib import Path

from .errno import errnos
from .resp import ErrResponse

TYPE_OPTIONS = {
    "LoRA": "LoRA",
    "Controlnet": "Controlnet",
}

BASE_MODEL_TYPE_OPTIONS = {
    "Flux.1 D": "Flux.1 D",
    "SDXL": "SDXL",
    "SD 1.5": "SD 1.5",
    "SD 3.5": "SD 3.5",
    "Pony": "Pony",
    "Kolors": "Kolors",
    "Hunyuan 1": "Hunyuan 1",
    "Other": "Other",
}

ALLOW_TYPES = list(TYPE_OPTIONS.values())
ALLOW_BASE_MODEL_TYPES = list(BASE_MODEL_TYPE_OPTIONS.values())
ALLOW_UPLOADABLE_EXT_NAMES = [
    ".safetensors",
    ".pth",
    ".bin",
    ".pt",
    ".ckpt",
    ".gguf",
    ".sft",
]

current_path = os.path.abspath(os.path.dirname(__file__))


def get_html_content(filename: str):
    html_file_path = Path(current_path) / filename
    with open(html_file_path, "r", encoding="utf-8") as htmlfile:
        html_content = htmlfile.read()
    return html_content


def is_string_valid(s):
    # 检查s是否已经被定义（即不是None）且不是空字符串
    if s is not None and s != "":
        return True
    else:
        return False


def to_slash(path):
    return path.replace("\\", "/")


def check_str_param(json_data, param_name: str, err):
    if param_name not in json_data:
        return ErrResponse(err)
    if not is_string_valid(json_data[param_name]):
        return ErrResponse(err)
    return None


def check_type(json_data):
    if "type" not in json_data:
        return ErrResponse(errnos.INVALID_TYPE)
    if not is_string_valid(json_data["type"]) or (
        json_data["type"] not in ALLOW_TYPES and json_data["type"] != "Workflow"
    ):
        return ErrResponse(errnos.INVALID_TYPE)
    return None


def types():
    types = []
    for k, v in TYPE_OPTIONS.items():
        types.append({"label": k, "value": v})
    return types


def base_model_types():
    base_model_types = []
    for k, v in BASE_MODEL_TYPE_OPTIONS.items():
        base_model_types.append({"label": k, "value": v})
    return base_model_types


def is_allow_ext_name(local_file_name):
    if not os.path.isfile(local_file_name):
        return False
    _, ext = os.path.splitext(local_file_name)
    return ext.lower() in ALLOW_UPLOADABLE_EXT_NAMES
