import os
from collections.abc import Collection
from typing import Dict, Union

import yaml


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


def get_service_route(service_config: Dict[str, str]) -> Union[str, None]:
    if {"route", "service_address"}.issubset(service_config):
        return f"{service_config['service_address']}{service_config['route']}"
    return None
