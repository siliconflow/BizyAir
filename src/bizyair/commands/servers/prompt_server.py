import pprint
import traceback
from typing import Any, Dict, List

from bizyair.common.env_var import BIZYAIR_DEBUG
from bizyair.common.utils import truncate_long_strings
from bizyair.image_utils import decode_data, encode_data

from ..base import Command, Processor  # type: ignore


class PromptServer(Command):
    def __init__(self, router: Processor, processor: Processor):
        self.router = router
        self.processor = processor

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

        try:
            out = result["data"]["payload"]
        except Exception as e:
            raise RuntimeError(
                f'Unexpected error accessing result["data"]["payload"]. Result: {result}'
            ) from e
        try:
            real_out = decode_data(out)
            return real_out[0]
        except Exception as e:
            print("Exception occurred while decoding data")
            traceback.print_exc()
            raise RuntimeError(f"Exception: {e=}") from e
