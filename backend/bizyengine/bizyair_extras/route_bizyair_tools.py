import json
import pprint

import bizyengine.core as bizyair
from aiohttp import web
from bizyengine.core.data_types import BIZYAIR_TYPE_MAP
from server import PromptServer


def get_bizyair_display_name(class_type: str) -> str:
    bizyair_cls_prefix = bizyair.nodes_base.PREFIX
    bizyair_logo = bizyair.nodes_base.LOGO
    return f"{bizyair_logo}{bizyair_cls_prefix} {bizyair.NODE_DISPLAY_NAME_MAPPINGS.get(class_type, class_type)}"


def workflow_convert(inputs: dict):
    nodes = inputs["nodes"]
    for node in nodes:
        class_type = node["type"]
        node_inputs = node.get("inputs")
        node_outputs = node.get("outputs")
        bizyair_cls_type = f"{bizyair.nodes_base.PREFIX}_{class_type}"
        is_converted = False
        if bizyair_cls_type in bizyair.NODE_CLASS_MAPPINGS:
            node["type"] = bizyair_cls_type
            display_name = get_bizyair_display_name(class_type)
            node["properties"]["Node name for S&R"] = display_name
            if node_inputs:
                for input_node in node_inputs:
                    input_type = input_node["type"]
                    input_node["type"] = BIZYAIR_TYPE_MAP.get(input_type, input_type)
            if node_outputs:
                for output_node in node_outputs:
                    output_type = output_node["type"]
                    output_node["type"] = BIZYAIR_TYPE_MAP.get(output_type, output_type)
            is_converted = True
        pprint.pprint(
            {
                "original_class_type": class_type,
                "bizyair_cls_type": bizyair_cls_type,
                "is_converted": is_converted,
            }
        )
    return inputs


@PromptServer.instance.routes.post("/bizyair/node_converter")
async def convert(request):
    try:
        data = await request.json()
        ret = workflow_convert(data)
        return web.Response(
            text=json.dumps(ret),
            content_type="application/json",
        )
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=400)
