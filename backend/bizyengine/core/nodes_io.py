import warnings
from typing import Any, Dict

from .commands import invoker
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
        self, url=None, headers=None, *, progress_callback=None, stream=False, **kwargs
    ) -> any:
        out = invoker.prompt_server.execute(
            prompt=self.nodes, last_node_ids=[self.node_id], **kwargs
        )
        return out


@encode_data.register(BizyAirNodeIO)
def _(output: BizyAirNodeIO, **kwargs):
    origin_id = output.node_id
    origin_slot = output.nodes[origin_id]["outputs"]["slot_index"]
    return [origin_id, origin_slot]
