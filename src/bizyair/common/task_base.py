import json
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import comfy
import requests

from bizyair.configs.conf import config_manager

from .client import send_request
from .env_var import (
    BIZYAIR_DEBUG,
    BIZYAIR_DEV_GET_TASK_RESULT_SERVER,
    BIZYAIR_SERVER_ADDRESS,
)


def is_bizyair_async_response(result: Dict[str, Any]) -> bool:
    """Determine if the result indicates an asynchronous task."""
    return (
        result.get("code") == 20000
        and result.get("status", False)
        and "task_id" in result.get("data", {})
    )


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
    new_events = []
    for event in events:
        if (
            "data" in event
            and isinstance(event["data"], str)
            and event["data"].startswith("https://")
        ):
            event["data"] = send_request(method="GET", url=event["data"])
        new_events.append(event)
    out["data"]["events"] = new_events
    return out


@dataclass
class BizyAirTask:
    TASK_DATA_STATUS = ["PENDING", "PROCESSING", "COMPLETED"]
    task_id: str
    data_pool: list[dict] = field(default_factory=list)
    data_status: str = None
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    @staticmethod
    def check_inputs(inputs: dict) -> bool:
        return (
            inputs.get("code") == 20000
            and inputs.get("status", False)
            and "task_id" in inputs.get("data", {})
        )

    @classmethod
    def from_data(cls, inputs: dict, check_inputs: bool = True) -> "BizyAirTask":
        if check_inputs and not cls.check_inputs(inputs):
            raise ValueError(f"Invalid inputs: {inputs}")
        data = inputs.get("data", {})
        task_id = data.get("task_id", "")
        return cls(task_id=task_id, data_pool=[], data_status="started")

    def is_finished(self) -> bool:
        with self._lock:
            if not self.data_pool:
                return False
            if self.data_pool[-1].get("data_status") == self.TASK_DATA_STATUS[-1]:
                return True
        return False

    def send_request(self, offset: int = 0) -> dict:
        with self._lock:
            if offset >= len(self.data_pool):
                return get_bizyair_task_result(self.task_id, offset)
            else:
                return self.data_pool[offset]

    def get_data(self, offset: int = 0) -> dict:
        with self._lock:
            if offset >= len(self.data_pool):
                return {}
            return self.data_pool[offset]

    @staticmethod
    def _fetch_remote_data(url: str) -> dict:
        return requests.get(url).json()

    def get_last_data(self) -> dict:
        with self._lock:
            if not self.data_pool:
                return {}
            return self.data_pool[-1]

    def do_task_until_completed(
        self, *, timeout: int = 600, poll_interval: float = 1
    ) -> None:
        offset = 0
        start_time = time.time()
        pbar = None
        while not self.is_finished():
            try:
                data = self.send_request(offset)
                data_lst = self._extract_data_list(data)
                with self._lock:
                    self.data_pool.extend(data_lst)
                    offset += len(data_lst)
                for data in data_lst:
                    message = data.get("data", {}).get("message", {})
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
    def __init__(
        self, task_id: str, data_pool: list[dict] = [], data_status: str = "started"
    ):
        super().__init__(task_id, data_pool, data_status)
        self._data_offset = 0  # current data cursor
        self.executor = ThreadPoolExecutor(max_workers=1)

    def get_current_result(self) -> dict:
        with self._lock:
            if self._data_offset >= len(self.data_pool):
                return {}
            else:
                return self.data_pool[self._data_offset]

    def _process_result(self, node_id: str, result: dict) -> dict:
        try:
            if (
                "message" in result
                and isinstance(result["message"], dict)
                and result["message"]["event"] == "result"
            ):
                event_node_id = result["message"]["data"]["node"]
                if event_node_id == node_id:
                    return result["data"]["payload"]
                else:
                    self.tmp_result[event_node_id] = result["data"]["payload"]
        except Exception as e:
            print(f"Error processing message for {self.name}: {e}")
            return None

    def get_result(self, node_id):
        while not self.is_finished() or self._data_offset < len(self.data_pool):
            ret = self.get_current_result()
            if ret:
                with self._lock:
                    self._data_offset += 1
                return self._process_result(node_id, ret)
            time.sleep(1)  # TODO: avoid busy waiting
        return {}

    def reset(self) -> None:
        with self._lock:
            self._data_offset = 0

    def execute_in_thread(self, timeout: int = 600, poll_interval: float = 1) -> None:
        self.executor.submit(
            self.do_task_until_completed, timeout=timeout, poll_interval=poll_interval
        )
