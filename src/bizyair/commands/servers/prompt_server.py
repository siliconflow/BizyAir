import json
import pprint
import traceback
from typing import Any, Dict, List

import requests

from bizyair.common import BizyAirTask
from bizyair.common.env_var import BIZYAIR_DEBUG
from bizyair.common.utils import truncate_long_strings
from bizyair.image_utils import decode_data, encode_data

from ..base import Command, Processor  # type: ignore


class PromptServer(Command):
    def __init__(self, router: Processor, processor: Processor):
        self.router = router
        self.processor = processor

    def get_task_id(self, result: Dict[str, Any]) -> str:
        return result.get("data", {}).get("task_id", "")

    def is_async_task(self, result: Dict[str, Any]) -> str:
        """Determine if the result indicates an asynchronous task."""
        return (
            result.get("code") == 20000
            and result.get("status", False)
            and "task_id" in result.get("data", {})
        )

    def _get_result(self, result: Dict[str, Any]):
        try:
            response_data = result["data"]
            if BizyAirTask.check_inputs(result):
                bz_task = BizyAirTask.from_data(result, check_inputs=False)

                i = 0
                while i < 1000:
                    import time

                    time.sleep(1)
                    try:
                        _ = bz_task.send_request(offset=i)
                        import ipdb

                        ipdb.set_trace()
                        i += 1
                    except Exception as e:
                        print(f"Exception: {e}")

            if "upload_to_s3" in result and result["upload_to_s3"]:
                upload_url = result["data"]
                response = requests.get(upload_url)
                assert response.status_code == 200
                response_data = response.json()
            out = response_data["payload"]
            return out
        except Exception as e:
            raise RuntimeError(
                f'Unexpected error accessing result["data"]["payload"]. Result: {result}'
            ) from e

    def execute(
        self,
        prompt: Dict[str, Dict[str, Any]],
        last_node_ids: List[str],
        *args,
        **kwargs,
    ):
        prompt = encode_data(prompt)
        if BIZYAIR_DEBUG:
            debug_info = {
                "prompt": truncate_long_strings(prompt, 50),
                "last_node_ids": last_node_ids,
            }
            pprint.pprint(debug_info, indent=4)
        url = self.router(prompt=prompt, last_node_ids=last_node_ids)
        if BIZYAIR_DEBUG:
            print(f"Generated URL: {url}")

        result = self.processor(url, prompt=prompt, last_node_ids=last_node_ids)
        if BIZYAIR_DEBUG:
            pprint.pprint({"result": truncate_long_strings(result, 50)}, indent=4)

        if result is None:
            raise RuntimeError("result is None")

        out = self._get_result(result)
        try:
            real_out = decode_data(out)
            return real_out[0]
        except Exception as e:
            print("Exception occurred while decoding data")
            traceback.print_exc()
            raise RuntimeError(f"Exception: {e=}") from e
