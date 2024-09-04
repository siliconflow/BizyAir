import json
from collections import deque
from typing import Any, Dict, List

from bizyair.common import client
from bizyair.common.env_var import BIZYAIR_DEBUG, BIZYAIR_DEV_REQUEST_URL
from bizyair.path_utils import (
    convert_prompt_label_path_to_real_path,
    guess_url_from_node,
)

from ..base import Processor  # type: ignore


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


@dataclass
class NodeUsageState:
    loras = []


class SearchServiceRouter(Processor):
    def process(self, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str]):
        if BIZYAIR_DEV_REQUEST_URL:
            return BIZYAIR_DEV_REQUEST_URL

        # TODO Improve distribution logic
        queue = deque(last_node_ids)
        visited = {key: True for key in last_node_ids}
        results = []
        node_usage_state = NodeUsageState()
        while queue:
            vertex = queue.popleft()
            if BIZYAIR_DEBUG:
                print(vertex, end="->")
            class_type = prompt[vertex]["class_type"]

            if class_type == "LoraLoader":
                node_usage_state.loras.append(prompt[vertex])

            url = guess_url_from_node(prompt[vertex], node_usage_state)
            if url:
                results.append(url)
            for _, in_data in prompt[vertex].get("inputs", {}).items():
                if is_link(in_data):
                    neighbor = in_data[0]
                    if neighbor not in visited:
                        visited[neighbor] = True
                        queue.append(neighbor)
        return results[-1]

    def validate_input(
        self, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str]
    ):
        assert len(last_node_ids) == 1
        return True


class PromptProcessor(Processor):
    def process(
        self, url: str, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str]
    ):
        prompt = convert_prompt_label_path_to_real_path(prompt)
        return client.send_request(
            url=url,
            data=json.dumps(
                {"prompt": prompt, "last_node_id": last_node_ids[0]}
            ).encode("utf-8"),
        )

    def validate_input(
        self, url: str, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str]
    ):
        return True
