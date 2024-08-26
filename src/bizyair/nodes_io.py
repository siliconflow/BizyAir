import warnings
from typing import Any, Dict

from bizyair.commands import invoker

from .image_utils import encode_data


def create_node_data(class_type: str, inputs: dict, outputs: dict):
    assert (
        outputs.get("slot_index", None) is not None
    ), "outputs must contain 'slot_index'"
    assert isinstance(outputs["slot_index"], int), "'slot_index' must be an integer"
    assert isinstance(class_type, str)

    out = {
        "class_type": class_type,
        "inputs": inputs,
        "outputs": outputs,
    }

    return out


class BizyAirNodeIO:
    def __init__(
        self,
        node_id: int = "0",  # Unique identifier for the current node
        nodes: Dict[str, Dict[str, any]] = {},
        *args,
        **kwargs,
    ):
        self._validate_node_id(node_id=node_id)
        self.node_id = node_id
        self.nodes = nodes

    def _validate_node_id(self, node_id) -> bool:
        if node_id is None:
            raise ValueError("Node ID cannot be None.")
        if not isinstance(node_id, str):
            raise ValueError("Node ID must be a string.")
        if not node_id.isdigit():
            raise ValueError(
                "Node ID must be a string that can be converted to an integer."
            )
        return True

    def copy(self, new_node_id: str = None):
        self._validate_node_id(new_node_id)
        if new_node_id in self.nodes:
            raise ValueError(f"Node ID '{new_node_id}' already exists.")

        return BizyAirNodeIO(
            nodes=self.nodes.copy(),
            node_id=new_node_id,
        )

    # @property
    # def workflow_api(self):
    #     # class_configs = self.configs.get("class_types", {})
    #     # class_usage_count = {}
    #     # for _, instance_info in self.nodes.items():
    #     #     class_type = instance_info["class_type"]
    #     #     if class_type not in class_configs:
    #     #         continue
    #     #     if class_type not in class_usage_count:
    #     #         class_usage_count[class_type] = 0
    #     #     class_usage_count[class_type] += 1

    #     #     max_instances = class_configs[class_type]["max_instances"]
    #     #     # Check if the maximum instances limit has been exceeded
    #     #     if max_instances < class_usage_count[class_type]:
    #     #         raise RuntimeError(
    #     #             False,
    #     #             f"{class_type} max_instances is too large, allowed: {max_instances}",
    #     #         )
    #     # prompt = convert_prompt_label_path_to_real_path(self.nodes)
    #     return {"prompt": self.nodes, "last_node_id": self.node_id}

    def add_node_data(
        self,
        class_type: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any] = {"slot_index": 0},
    ):
        node_data = create_node_data(
            class_type=class_type,
            inputs=inputs,
            outputs=outputs,
        )

        self.update_nodes_from_others(*inputs.values())

        if self.node_id in self.nodes:
            warnings.warn(
                f"Node ID {self.node_id} already exists. Data will be overwritten.",
                RuntimeWarning,
            )

        self.nodes[self.node_id] = node_data

    def update_nodes_from_others(self, *others):
        for other in others:
            if isinstance(other, BizyAirNodeIO):
                self.nodes.update(other.nodes)

    def send_request(
        self, url=None, headers=None, *, progress_callback=None, stream=False
    ) -> any:
        out = invoker.prompt_server.execute(
            prompt=self.nodes, last_node_ids=[self.node_id]
        )
        return out
        # from .commands.invoker import Invoker
        # # Search service routing
        # ssr = SearchServiceRouter()
        # Invoker(PromptServer(ssr)).action()

        # # 处理请求
        # prompt_processer = PromptProcessor()
        # Invoker(PromptServer(prompt_processer)).action()
        # pass
        # api_url = self.service_route()
        # if self.debug:
        #     prompt = self._short_repr(self.workflow_api["prompt"], max_length=100)
        #     print(f"Debug: {prompt=}")
        # if stream:
        #     result = None
        #     pass  # TODO(fix)
        # def process_events(api_url, workflow_api, api_key):
        #     total_steps = None
        #     with BizyAirStreamClient(api_url, workflow_api, api_key) as stream_client:
        #         for event_data in stream_client.events():
        #             try:
        #                 event_data = json.loads(event_data)["data"]
        #             except json.JSONDecodeError as e:
        #                 print(f"rror decoding JSON: {e}")
        #                 print(f"Received data: {event_data}")
        #                 raise e

        #             # if self.debug:
        #             print(f"Debug Event Data: {self._short_repr(event_data, 100)}")

        #             status = event_data["status"]
        #             data = event_data["data"]
        #             pending_count = event_data.get("pending_tasks_count", None)
        #             if status == TaskStatus.PENDING.value:
        #                 print(
        #                     f"Task is pending, current pending tasks count: {pending_count}"
        #                 )
        #             elif status == TaskStatus.PROCESSING.value:
        #                 if "progress" in data and isinstance(data["progress"], dict):
        #                     step, total_steps = (
        #                         data["progress"]["value"],
        #                         data["progress"]["total"],
        #                     )
        #                     progress_callback(step, total_steps, preview=None)

        #             elif status == TaskStatus.COMPLETED.value:
        #                 if total_steps:
        #                     progress_callback(total_steps, total_steps, preview=None)
        #                 return event_data

        # result = process_events(api_url, self.workflow_api, self.API_KEY)
        # else:
        #     result = client.send_request(
        #         url=api_url, data=json.dumps(self.workflow_api).encode("utf-8")
        #     )

        # if result is None:
        #     raise RuntimeError("result is None")

        # try:
        #     out = result["data"]["payload"]
        # except Exception as e:
        #     raise RuntimeError(
        #         f'Unexpected error accessing result["data"]["payload"]. Result: {result}'
        #     ) from e
        # try:
        #     real_out = decode_data(out)
        #     return real_out[0]
        # except Exception as e:
        #     raise RuntimeError(
        #         f"Exception: {e=} {self._short_repr(out, max_length=100)}"
        #     ) from e


@encode_data.register(BizyAirNodeIO)
def _(output: BizyAirNodeIO, **kwargs):
    origin_id = output.node_id
    origin_slot = output.nodes[origin_id]["outputs"]["slot_index"]
    return [origin_id, origin_slot]
