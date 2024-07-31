import os
import yaml

SupportedFileExtensionsType = set[str]
ScanPathType = list[str]
folder_names_and_paths: dict[str, tuple[ScanPathType, SupportedFileExtensionsType]] = {}


def load_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def guess_config(*, ckpt_name: str = None, vae_name: str = None) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    if ckpt_name is not None:
        if ckpt_name == "sdxl/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors":
            return os.path.join(base_path, "configs", "sdxl_config.yaml")
    if vae_name is not None:
        if vae_name == "sdxl/sdxl_vae.safetensors":
            return os.path.join(base_path, "configs", "kolors_config.yaml")


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


def init_config():
    class_type_key_mapping = {
        "CheckpointLoaderSimple": ["ckpt_name", "checkpoints"],
        "ControlNetLoader": ["control_net_name", "controlnet"],
        "LoraLoader": ["lora_name", "loras"],
        "CLIPVisionLoader": ["clip_name", "clip_vision"],
        "VAELoader": ["vae_name", "vae"],
    }
    for path in get_config_file_list():
        config = load_yaml_config(path)
        for class_type in config["class_types"]:
            inputs = config["class_types"][class_type].get("inputs", {})
            if class_type in class_type_key_mapping:
                key, folder_key = class_type_key_mapping[class_type]
                if key not in folder_names_and_paths:
                    folder_names_and_paths[folder_key] = []
                if key not in inputs:
                    print(f"Warning: no find limit for {class_type=} {key=}")
                else:
                    folder_names_and_paths[folder_key].extend(inputs[key])


init_config()

if __name__ == "__main__":
    print(f"Loaded config from {get_config_file_list()}")
    configs = [load_yaml_config(x) for x in get_config_file_list()]
    # print(f'{configs}')
    import pdb

    pdb.set_trace()
