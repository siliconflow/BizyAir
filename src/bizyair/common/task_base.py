import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, Set

import comfy
import requests

from bizyair.configs.conf import config_manager
from bizyair.image_utils import decode_data

from .client import send_request
from .env_var import (
    BIZYAIR_DEBUG,
    BIZYAIR_DEV_GET_TASK_RESULT_SERVER,
    BIZYAIR_SERVER_ADDRESS,
)
from .utils import retry_on_failure


def is_bizyair_async_response(result: Dict[str, Any]) -> bool:
    """Determine if the result indicates an asynchronous task."""
    return (
        result.get("code") == 20000
        and result.get("status", False)
        and "task_id" in result.get("data", {})
    )


_TRAINING_SUBSCRIBER = None


def set_training_subscriber(subscriber=None):
    global _TRAINING_SUBSCRIBER
    _TRAINING_SUBSCRIBER = subscriber


def get_training_subscriber():
    global _TRAINING_SUBSCRIBER
    return _TRAINING_SUBSCRIBER


def is_training_mode() -> bool:
    return _TRAINING_SUBSCRIBER is not None


from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


@retry_on_failure(max_retries=2)
def _process_event(event):
    if (
        "data" in event
        and isinstance(event["data"], str)
        and event["data"]
        .strip('"')
        .startswith("https://")  # TODO fix need .strip('"') bug
    ):
        # event["data"] = send_request(method="GET", url=event["data"].strip('"'))
        event["data"] = requests.get(url=event["data"].strip('"')).json()
    return decode_data(event)


def process_events_with_threadpool(events):
    new_events = [None] * len(events)  # 预分配一个与 events 大小相同的列表
    with ThreadPoolExecutor() as executor:
        # 提交任务到线程池，并记录每个任务的索引
        future_to_index = {
            executor.submit(_process_event, event): idx
            for idx, event in enumerate(events)
        }

        # 使用 tqdm 显示进度
        for future in tqdm(
            as_completed(future_to_index),
            total=len(events),
            desc="Processing events",
            unit="it",
        ):
            idx = future_to_index[future]  # 获取当前任务对应的索引
            new_event = future.result()
            new_events[idx] = new_event  # 将结果放到正确的位置

    return new_events


def get_bizyair_task_result(task_id: str, offset: int = 0) -> dict:
    """
    Get the result of a task.
    """
    task_api = config_manager.get_task_api()
    if BIZYAIR_DEV_GET_TASK_RESULT_SERVER:
        url = f"{BIZYAIR_DEV_GET_TASK_RESULT_SERVER}{task_api.task_result_endpoint}/{task_id}"
    else:
        url = f"{BIZYAIR_SERVER_ADDRESS}{task_api.task_result_endpoint}/{task_id}"

    if BIZYAIR_DEBUG:
        print(f"Debug: get task result url: {url}")
    response_json = send_request(
        method="GET", url=url, data=json.dumps({"offset": offset}).encode("utf-8")
    )
    out = response_json
    events = out.get("data", {}).get("events", [])
    new_events = process_events_with_threadpool(events)
    out["data"]["events"] = new_events
    return out


@dataclass
class BizyAirTask:
    """
    Represents a task in the BizyAir system.

    Attributes:
        task_id (str): The unique identifier of the task.
        data_pool (List[Dict]): A list of data items associated with the task.
        node_output_cache (Dict[str, Dict]): A cache to store output results by node ID.
        data_status (TaskDataStatus): The current status of the task data.
    """

    TASK_DATA_STATUS = ["PENDING", "PROCESSING", "COMPLETED"]
    task_id: str
    prompt: Dict[str, Any] = field(default_factory=dict)
    data_pool: list[dict] = field(default_factory=list)
    node_output_cache: Dict[str, Dict] = field(default_factory=dict)
    data_status: str = None

    @staticmethod
    def check_inputs(inputs: dict) -> bool:
        return (
            inputs.get("code") == 20000
            and inputs.get("status", False)
            and "task_id" in inputs.get("data", {})
        )

    @classmethod
    def from_data(
        cls, inputs: dict, prompt: Dict[str, Any], check_inputs: bool = True
    ) -> "BizyAirTask":
        if check_inputs and not cls.check_inputs(inputs):
            raise ValueError(f"Invalid inputs: {inputs}")
        data = inputs.get("data", {})
        task_id = data.get("task_id", "")
        return cls(task_id=task_id, data_pool=[], data_status="started", prompt=prompt)

    def is_finished(self) -> bool:
        if not self.data_pool:
            return False
        if self.data_pool[-1].get("data_status") == self.TASK_DATA_STATUS[-1]:
            return True
        return False

    def send_request(self, offset: int = 0) -> dict:
        if offset >= len(self.data_pool):
            return get_bizyair_task_result(self.task_id, offset)
        else:
            return self.data_pool[offset]

    def get_data(self, offset: int = 0) -> dict:
        if offset >= len(self.data_pool):
            return {}
        return self.data_pool[offset]

    @staticmethod
    def _fetch_remote_data(url: str) -> dict:
        return requests.get(url).json()

    def get_last_data(self) -> dict:
        if not self.data_pool:
            return {}
        return self.data_pool[-1]

    def do_task_until_completed(
        self, *, timeout: int = 6000, poll_interval: float = 1
    ) -> None:
        offset = 0
        start_time = time.time()
        pbar = None
        while not self.is_finished():
            try:
                data = self.send_request(offset)
                data_lst = self._extract_data_list(data)
                self.data_pool.extend(data_lst)
                offset += len(data_lst)

                for data in data_lst:
                    message = data.get("data", {}).get("message", {})
                    print(f"{message=}")
                    if (
                        isinstance(message, dict)
                        and message.get("event", None) == "progress"
                    ):
                        value = message["data"]["value"]
                        total = message["data"]["max"]
                        if pbar is None:
                            pbar = comfy.utils.ProgressBar(total)
                        pbar.update_absolute(value + 1, total, None)
            except Exception as e:
                print(f"Exception: {e}")

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for task {self.task_id} to finish")

            time.sleep(poll_interval)

    def _extract_data_list(self, data):
        data_lst = data.get("data", {}).get("events", [])
        if not data_lst:
            raise ValueError(f"No data found in task {self.task_id}")
        return data_lst


class DynamicLazyTaskExecutor(BizyAirTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_offset = 0  # current data cursor
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.cache_result = {}
        self.queried_nodes: Set[str] = set()

    def get_current_result(self) -> dict:
        if self._data_offset >= len(self.data_pool):
            return {}
        else:
            return self.data_pool[self._data_offset]

    def _process_result(self, result: dict, **kwargs) -> dict:
        try:
            message = result.get("data", {}).get("message", {})
            if isinstance(message, dict) and message.get("event", None) == "result":
                event_node_id = message["data"]["node"]
                self.cache_result[event_node_id] = result["data"]["payload"]
        except Exception as e:
            print(f"Error processing message for : {e}")
            return None

    def get_result(self, node_id):
        print(f"in =" * 20, node_id, "-" * 10)
        if node_id not in self.prompt:
            print(f"Error {node_id} not in self.prompt")
            return None

        self.queried_nodes.add(node_id)

        def check():
            return not self.is_finished() or self._data_offset < len(self.data_pool)

        pbar = None
        while check():  # Poll for the result
            if node_id in self.cache_result:
                break
            print(f"{self.cache_result.keys()=}")
            data = self.send_request(self._data_offset)

            data_lst = self._extract_data_list(data)

            self.data_pool.extend(data_lst)
            self._data_offset += len(data_lst)

            for data in data_lst:
                if BIZYAIR_DEBUG:
                    print(f"\n{str(data)[:200]}")
                try:
                    message = data.get("data", {}).get("message", {})
                except Exception as e:
                    print(f"Warning get message failed {data=} {e=}")
                    continue
                if BIZYAIR_DEBUG:
                    print(f"{message=}")

                if (
                    isinstance(message, dict)
                    and message.get("event", None) == "progress"
                ):
                    value = message["data"]["value"]
                    total = message["data"]["max"]
                    if pbar is None:
                        pbar = comfy.utils.ProgressBar(total)
                    pbar.update_absolute(value + 1, total, None)

                self._process_result(data)
            time.sleep(0.5)  # TODO: avoid busy waiting

        return self.cache_result.get(node_id, None)

    def reset(self) -> None:
        self._data_offset = 0
