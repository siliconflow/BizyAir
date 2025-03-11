import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple

from bizyengine.core.common.utils import load_config_file, recursive_extract_models


@dataclass
class ModelRule:
    mode_type: str
    base_model: str
    describe: str
    score: int
    route: str
    class_type: str
    inputs: dict


@dataclass
class TaskApi:
    task_result_endpoint: str


class ModelRuleManager:
    def __init__(self, model_rules: list[dict]):
        self.model_rules = model_rules
        self.validate()
        self.gen_model_rule_index_mapping()

    def gen_model_rule_index_mapping(self):
        self.model_rule_index_mapping = defaultdict(list)

        for idx_1, rule in enumerate(self.model_rules):
            for idx_2, node in enumerate(rule["nodes"]):
                self.model_rule_index_mapping[node["class_type"]].append((idx_1, idx_2))

    def validate(self):
        for rule in self.model_rules:
            self._validate_rule(rule)

    def _validate_rule(self, rule: dict):
        if "mode_type" not in rule:
            raise ValueError("mode_type is required")
        if "base_model" not in rule:
            raise ValueError("base_model is required")
        if "route" not in rule:
            raise ValueError("route is required")
        if "nodes" not in rule:
            raise ValueError("nodes is required")

    def find_rule_indexes(self, class_type: str) -> List[Tuple[int, int]]:
        return self.model_rule_index_mapping[class_type]

    def find_rules(self, class_type: str) -> List[ModelRule]:
        rule_indexes = self.find_rule_indexes(class_type)
        return [
            ModelRule(
                mode_type=self.model_rules[idx_1]["mode_type"],
                base_model=self.model_rules[idx_1]["base_model"],
                describe=self.model_rules[idx_1]["describe"],
                score=self.model_rules[idx_1]["score"],
                route=self.model_rules[idx_1]["route"],
                class_type=class_type,
                inputs=self.model_rules[idx_1]["nodes"][idx_2].get("inputs", {}),
            )
            for idx_1, idx_2 in rule_indexes
        ]


class ModelPathManager:
    def __init__(self, config_path: str):
        model_paths = {}
        for folder_name, v in load_config_file(config_path).items():
            model_paths[folder_name] = recursive_extract_models(v)
        self.model_paths = model_paths

    def get_filenames(self, folder_name: str) -> List[str]:
        return self.model_paths.get(folder_name, [])


class ConfigManager:
    def __init__(self, model_path_config: str, model_rule_config: str):
        self.model_path_manager = ModelPathManager(config_path=model_path_config)
        self.model_rule_config = load_config_file(model_rule_config)
        self.model_rules = ModelRuleManager(
            model_rules=self.model_rule_config["model_rules"]
        )

    def get_filenames(self, folder_name: str) -> List[str]:
        return self.model_path_manager.get_filenames(folder_name)

    def get_rules(self, class_type: str) -> List[ModelRule]:
        if class_type.startswith("BizyAir_"):
            class_type = class_type[8:]
        return self.model_rules.find_rules(class_type)

    def get_model_version_id_prefix(self):
        return self.model_rule_config["model_version_config"]["model_version_id_prefix"]

    def get_cache_config(self):
        return self.model_rule_config.get("cache_config", {})

    def get_task_api(self):
        return TaskApi(**self.model_rule_config["task_api"])


model_path_config = os.path.join(os.path.dirname(__file__), "models.json")
model_rule_config = os.path.join(os.path.dirname(__file__), "models.yaml")
config_manager = ConfigManager(
    model_path_config=model_path_config, model_rule_config=model_rule_config
)
