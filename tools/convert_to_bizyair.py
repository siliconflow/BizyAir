"""
python tools/convert_to_bizyair.py \
    -i <input_file>
"""

import argparse
import json
import os
import pprint
import sys
from pathlib import Path
from typing import List

from loguru import logger


def setup_comfyui_env():
    comfyui_dir = Path(__file__).parents[3]
    sys.path.append(str(comfyui_dir))


def initialize_comfyui(cli_args: List = []):
    logger.info(f"Initializing ComfyUI with cli_args: {cli_args}")
    assert cli_args is not None and isinstance(
        cli_args, list
    ), f"cli_args must be a list, but got {cli_args}"

    orig_argv = sys.argv[1:]
    # Enable argument parsing and set temporary arguments
    import comfy.options

    comfy.options.enable_args_parsing()
    sys.argv[1:] = cli_args
    # Import ComfyUI modules
    import main

    if hasattr(main, "execute_prestartup_script"):
        main.execute_prestartup_script()
    else:
        logger.warning(
            "The 'main' object does not have an 'execute_prestartup_script' method."
        )

    import comfy
    import execution
    import nodes
    import server
    from comfy.cli_args import args

    if args.cuda_device is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.cuda_device)
        logger.info("Set cuda device to: {}".format(args.cuda_device))

    # This server is not used by real mode, but some nodes require it to load
    main.server = server.PromptServer(None)
    main.server.add_routes()

    nodes.init_extra_nodes(init_custom_nodes=not args.disable_all_custom_nodes)

    if hasattr(main, "cuda_malloc_warning"):
        main.cuda_malloc_warning()
    else:
        logger.warning(
            "The 'main' object does not have a 'cuda_malloc_warning' method."
        )
    sys.argv[1:] = orig_argv


def validate_input_file(func):
    def wrapper(file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        workflow = func(file_path)
        if not isinstance(workflow, dict):
            raise ValueError(f"Invalid input file: {file_path}")
        # TODO: check if the workflow format is correct [workflow_api, workflow]
        return workflow

    return wrapper


@validate_input_file
def load_input_file(file_path: str):
    if file_path.endswith(".json"):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


setup_comfyui_env()
initialize_comfyui()
import bizyengine.core


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, required=False, default=None)
    return parser.parse_args()


def main():
    args = get_args()
    out = convert_to_bizyair(load_input_file(args.input))
    if args.output is None:
        args.output = args.input.replace(".json", ".bizyair.json")
    with open(args.output, "w") as f:
        json.dump(out, f)
    pprint.pprint({"status": "success"})


def get_bizyair_display_name(class_type: str) -> str:
    bizyair_cls_prefix = bizyengine.core.nodes_base.PREFIX
    bizyair_logo = bizyengine.core.nodes_base.LOGO
    return f"{bizyair_logo}{bizyair_cls_prefix} {bizyengine.core.NODE_DISPLAY_NAME_MAPPINGS.get(class_type, class_type)}"


def convert_to_bizyair(inputs: dict):
    bizyengine.core.NODE_CLASS_MAPPINGS

    for x in inputs.copy():
        class_type = inputs[x]["class_type"]
        bizyair_cls_type = f"{bizyengine.core.nodes_base.PREFIX}_{class_type}"
        is_converted = False
        if bizyair_cls_type in bizyengine.core.NODE_CLASS_MAPPINGS:
            inputs[x]["class_type"] = bizyair_cls_type
            display_name = get_bizyair_display_name(class_type)
            inputs[x]["_meta"]["title"] = display_name
            is_converted = True

        pprint.pprint(
            {
                "original_class_type": class_type,
                "bizyair_cls_type": bizyair_cls_type,
                "is_converted": is_converted,
            }
        )
    return inputs


if __name__ == "__main__":
    main()
