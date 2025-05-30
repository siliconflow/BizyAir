import os
from collections.abc import Collection
from typing import Dict, Optional, Union

import yaml
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS
from bizyengine.core.configs.conf import config_manager


def compose_model_name(
    model_version_id: str = "", fallback_name: Optional[str] = None
) -> str:
    """Generate standardized model name from version ID.

    Args:
        model_version_id: Model version identifier (empty string or None treated as missing)
        fallback_name: Default name to use when version ID is missing

    Returns:
        Formatted model name (either prefixed ID or default)

    Raises:
        ValueError: If both model_version_id and default are missing
        RuntimeError: If configuration manager fails to provide prefix
    """
    # Handle missing version ID case
    if not model_version_id:  # Covers None, empty string, etc.
        if fallback_name is None:
            raise ValueError("Missing model_version_id with no default provided")
        return fallback_name

    # Validate ID format (adjust regex pattern as needed)
    if not isinstance(model_version_id, str):
        raise TypeError(
            f"model_version_id must be string, got {type(model_version_id)}"
        )

    # Safely retrieve configuration prefix
    try:
        prefix = config_manager.get_model_version_id_prefix()
    except AttributeError as e:
        raise RuntimeError("Configuration manager missing required method") from e
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve model prefix: {str(e)}") from e

    # Construct final model name
    return f"{prefix}{model_version_id}"


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
    if {"route"}.issubset(service_config):
        return str(
            service_config.get("service_address", BIZYAIR_SERVER_ADDRESS)
        ) + service_config.get("route")
    return None
