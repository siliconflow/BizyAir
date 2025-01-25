import hashlib
import json
import pprint
from collections import deque
from typing import Any, Dict, List

from bizyair.common import client, get_api_key
from bizyair.common.caching import BizyAirTaskCache, CacheConfig
from bizyair.common.env_var import (
    BIZYAIR_DEBUG,
    BIZYAIR_DEV_REQUEST_URL,
    BIZYAIR_SERVER_ADDRESS,
)
from bizyair.common.task_base import DynamicLazyTaskExecutor, is_bizyair_async_response
from bizyair.common.utils import truncate_long_strings
from bizyair.configs.conf import ModelRule, config_manager
from bizyair.data_types import is_send_request_datatype
from bizyair.path_utils import guess_url_from_node

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


class SearchServiceRouter(Processor):
    def process(self, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str], **kwargs):
        if BIZYAIR_DEV_REQUEST_URL:
            return BIZYAIR_DEV_REQUEST_URL

        # TODO Improve distribution logic
        queue = deque(last_node_ids)
        visited = {key: True for key in last_node_ids}
        results: List[ModelRule] = []
        class_type_table = {
            node_data["class_type"]: True for node_data in prompt.values()
        }

        while queue:
            vertex = queue.popleft()
            if BIZYAIR_DEBUG:
                print(vertex, end="->")

            rules = guess_url_from_node(prompt[vertex], class_type_table)
            if rules:
                results.extend(rules)
            for _, in_data in prompt[vertex].get("inputs", {}).items():
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
        self, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str] = [], **kwargs
    ):
        assert len(last_node_ids) == 1
        return True


class PromptProcessor(Processor):
    def _exec_info(self, prompt: Dict[str, Dict[str, Any]]):
        exec_info = {
            "model_version_ids": [],
            "api_key": get_api_key(),
        }

        model_version_id_prefix = config_manager.get_model_version_id_prefix()
        for node_id, node_data in prompt.items():
            for k, v in node_data.get("inputs", {}).items():
                if isinstance(v, str) and v.startswith(model_version_id_prefix):
                    model_version_id = int(v[len(model_version_id_prefix) :])
                    exec_info["model_version_ids"].append(model_version_id)
        return exec_info

    def process(
        self, url: str, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str], **kwargs
    ):
        # import requests
        
        # out = requests.request(method='POST', url = url, json={
        #             "prompt": prompt,
        #             "exec_info": self._exec_info(prompt),
        #         }, headers=client._headers())
        
        # out =  requests.request(method='POST', url = url, json={'prompt':prompt, 'exec_info': self._exec_info(prompt)}, headers=client._headers())
        # # out =  requests.request(method='POST', url = 'https://bizyair-api.siliconflow.cn/x/v1/bizy_task/dev-flux-lora-train', json={'prompt':prompt, 'exec_info': self._exec_info(prompt)}, headers=client._headers())
        # # out =  requests.request(method='POST', url = 'https://bizyair-api.siliconflow.cn/x/v1/bizy_task/dev-flux-lora-train', json={'prompt':{'1': 'in'}, 'exec_info': self._exec_info(prompt)}, headers=client._headers())

        # import ipdb; ipdb.set_trace()
        return client.send_request(
            url=url,
            data=json.dumps(
                {
                    "prompt": prompt,
                    # "last_node_id": last_node_ids[0],
                    "exec_info": self._exec_info(prompt),
                }
            ).encode("utf-8"),
        )

    def validate_input(
        self, url: str, prompt: Dict[str, Dict[str, Any]], last_node_ids: List[str]
    ):
        return True


class PromptPreRunProcessor(Processor):
    def process(
        self,
        pre_prompt: Dict[str, Dict[str, Any]],
        hidden: Dict[str, Dict[str, Any]] = {},
        **kwargs,
    ):
        unique_id = hidden["unique_id"]
        extra_pnginfo = hidden["extra_pnginfo"]
        workflow = extra_pnginfo["workflow"]
        links = workflow["links"]

        queue = deque([int(unique_id)])
        visited = set()
        last_node_id = int(unique_id)
        
        while queue:
            node_id = queue.popleft()
            if str(node_id) not in pre_prompt and str(node_id) in hidden["prompt"]:
                pre_prompt[str(node_id)] = hidden["prompt"][str(node_id)]
            if BIZYAIR_DEBUG:
                print(f"{node_id} -> ", end="")

            if node_id in visited:
                continue

            visited.add(node_id)
            # https://docs.comfy.org/essentials/javascript_objects_and_hijacking#workflow
            for link in links:
                # (link_id, upstream_node_id, upstream_node_output_slot, downstream_node_id, downstream_node_input_slot, data type)
                upstream_node_id, downstream_node_id, data_type = (
                    link[1],
                    link[3],
                    link[5],
                )
                if is_send_request_datatype(data_type):
                    # if downstream_node_id == node_id: 
                    #  TODO refine
                    continue
                elif data_type == '*':
                    import nodes
                    class_type = hidden["prompt"][str(upstream_node_id)]['class_type']
                    class_def = nodes.NODE_CLASS_MAPPINGS[class_type]
                    data_type = class_def.RETURN_TYPES[link[2]]
                    if data_type == 'KOHYA_ARGS': # TODO fix
                        continue
                    if is_send_request_datatype(data_type):
                        continue
                
                if upstream_node_id == node_id and downstream_node_id not in visited:
                    print(f'add {downstream_node_id=}')
                    queue.append(downstream_node_id)

                elif downstream_node_id == node_id and upstream_node_id not in visited:
                    print(f'add {upstream_node_id=}')
                    queue.append(upstream_node_id)

        if BIZYAIR_DEBUG:
            pprint.pprint(
                {
                    "pre_prompt": truncate_long_strings({k: v['class_type'] for k,v in pre_prompt.items()}),
                    "last_node_id": last_node_id,
                }
            )
            # dict_keys(['139', '141', '142', '138', '143', '150'])

        # TODO remove hidden keys
        return pre_prompt

    def validate_input(
        self, pre_prompt: Dict[str, Dict[str, Any]], hidden: Dict[str, Dict[str, Any]], **kwargs
    ):
        assert all(key in hidden for key in ["unique_id", "prompt", "extra_pnginfo"])
        assert "workflow" in hidden["extra_pnginfo"]
        return True


from bizyair.common.caching import bizyair_task_cache
class PromptAsyncProcessor(PromptProcessor):
    def process(
        self, url: str, prompt: Dict[str, Dict[str, Any]], **kwargs
    ) -> DynamicLazyTaskExecutor:
        cache_key = hashlib.sha256(
            json.dumps({"url": url, "prompt": prompt}).encode("utf-8")
        ).hexdigest()
        cached_output = bizyair_task_cache.get(cache_key)
        if cached_output:
            print(f'find cached_output {cache_key=}')
            result = cached_output
        else:
            result = super().process(url, prompt, **kwargs)
            bizyair_task_cache.set(cache_key, result, overwrite=True)

        if is_bizyair_async_response(result):
            worker = DynamicLazyTaskExecutor.from_data(inputs=result, prompt=prompt)
            worker.execute_in_thread()
            return worker
        raise ValueError("Invalid response, not a bizyair async response")

    def validate_input(self, url: str, prompt: Dict[str, Dict[str, Any]], **kwargs):
        return True
