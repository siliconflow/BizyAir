import os
import sys

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

from .bizyair import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./js"
import bizyair.bizyair_extras
from bizyair.misc import (
    auth,
    llm,
    mzkolors,
    nodes,
    nodes_controlnet_aux,
    nodes_controlnet_union_sdxl,
    segment_anything,
    showcase,
    supernode,
)


def update_mappings(module):
    NODE_CLASS_MAPPINGS.update(**module.NODE_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(**module.NODE_DISPLAY_NAME_MAPPINGS)


update_mappings(auth)
update_mappings(supernode)
update_mappings(llm)
update_mappings(nodes_controlnet_aux)
update_mappings(nodes_controlnet_union_sdxl)
update_mappings(mzkolors)
update_mappings(segment_anything)

try:
    import bizyair.bizy_server as bizy_server
except Exception as e:
    print("\n\n\033[91m[BizyAir]\033[0m Fail to import 'bizy_server':" f" {e}\n\n")
