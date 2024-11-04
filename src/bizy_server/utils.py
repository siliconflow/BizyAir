import os
from pathlib import Path

from .errno import INVALID_TYPE
from .resp import ErrResponse

TYPE_OPTIONS = {
    "lora": "bizyair/lora",
    # "other": "other",
}
ALLOW_TYPES = list(TYPE_OPTIONS.values())

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
        return ErrResponse(INVALID_TYPE)
    if not is_string_valid(json_data["type"]) or json_data["type"] not in ALLOW_TYPES:
        return ErrResponse(INVALID_TYPE)
    return None


def list_types():
    types = []
    for k, v in TYPE_OPTIONS.items():
        types.append({"label": k, "value": v})
    return types
