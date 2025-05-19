import json
from collections import deque
from typing import Any, Dict, List

from bizyengine.core.commands.base import Processor  # type: ignore
from bizyengine.core.common import client, get_api_key
from bizyengine.core.common.caching import BizyAirTaskCache, CacheConfig
from bizyengine.core.common.env_var import (
    BIZYAIR_DEBUG,
    BIZYAIR_DEV_REQUEST_URL,
    BIZYAIR_SERVER_ADDRESS,
)
from bizyengine.core.configs.conf import ModelRule, config_manager
from bizyengine.core.path_utils import (
    convert_prompt_label_path_to_real_path,
    guess_url_from_node,
)
from bizyengine.misc.utils import get_api_key_and_prompt_id


def is_link(obj):
    if not isinstance(obj, list):
        return False
    if len(obj) != 2:
        return False
    if not isinstance(obj[0], str):
        return False
    if not isinstance(obj[1], int) and not isinstance(obj[1], float):
        return False
    return True


from dataclasses import dataclass


class SearchServiceRouter(Processor):
    def process(
        self, nodes: Dict[str, Dict[str, Any]], last_node_ids: List[str], **kwargs
    ):
        if BIZYAIR_DEV_REQUEST_URL:
            return BIZYAIR_DEV_REQUEST_URL

        # TODO Improve distribution logic
        queue = deque(last_node_ids)
        visited = {key: True for key in last_node_ids}
        results: List[ModelRule] = []
        class_type_table = {
            node_data["class_type"]: True for node_data in nodes.values()
        }

        while queue:
            vertex = queue.popleft()
            if BIZYAIR_DEBUG:
                print(vertex, end="->")

            rules = guess_url_from_node(nodes[vertex], class_type_table)
            if rules:
                results.extend(rules)
            for _, in_data in nodes[vertex].get("inputs", {}).items():
                if is_link(in_data):
                    neighbor = in_data[0]
                    if neighbor not in visited:
                        visited[neighbor] = True
                        queue.append(neighbor)

        base_model, out_route, out_score = None, None, 0
        for rule in results[::-1]:
            # TODO add to config models.yaml
            if rule.mode_type in {"unet", "vae", "checkpoint", "upscale_models"}:
                base_model = rule.base_model
                out_route = rule.route
                out_score = rule.score
                break

        for rule in results:
            if base_model is None:
                if rule.score > out_score:
                    out_route, out_score = rule.route, rule.score
            if rule.base_model == base_model:
                if rule.score > out_score:
                    out_route, out_score = rule.route, rule.score
        assert (
            out_route is not None
        ), "Failed to find out_route, please check your prompt"
        return f"{BIZYAIR_SERVER_ADDRESS}{out_route}"

    def validate_input(
        self, nodes: Dict[str, Dict[str, Any]], last_node_ids: List[str], **kwargs
    ):
        assert len(last_node_ids) == 1
        return True


class PromptProcessor(Processor):
    def _exec_info(self, nodes: Dict[str, Dict[str, Any]], api_key: str):
        exec_info = {"model_version_ids": [], "api_key": api_key}

        model_version_id_prefix = config_manager.get_model_version_id_prefix()
        for node_id, node_data in nodes.items():
            for k, v in node_data.get("inputs", {}).items():
                if isinstance(v, str) and v.startswith(model_version_id_prefix):
                    model_version_id = int(v[len(model_version_id_prefix) :])
                    exec_info["model_version_ids"].append(model_version_id)
        return exec_info

    def process(
        self,
        url: str,
        nodes: Dict[str, Dict[str, Any]],
        last_node_ids: List[str],
        **kwargs,
    ):
        extra_data = get_api_key_and_prompt_id(prompt=kwargs["prompt"])
        # NOTE: nodes是bizyair中的节点数据，与comfybridge约定叫prompt，但是comfyui中的隐藏输入也叫prompt且是通过关键字传进来，所以把优先让给comfyui
        dict = {
            "prompt": nodes,
            "last_node_id": last_node_ids[0],
            "exec_info": self._exec_info(nodes, extra_data["api_key"]),
        }
        if "prompt_id" in extra_data:
            dict["prompt_id"] = extra_data["prompt_id"]

        return client.send_request(
            url=url,
            data=json.dumps(dict).encode("utf-8"),
            headers=client.headers(api_key=extra_data["api_key"]),
        )

    def validate_input(
        self,
        url: str,
        nodes: Dict[str, Dict[str, Any]],
        last_node_ids: List[str],
        **kwargs,
    ):
        return True
