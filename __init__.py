import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(current_path, "src")
if os.path.isdir(src_path):
    sys.path.insert(0, src_path)

from bizyair import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./js"

from . import (
    auth,
    bizyair_extras,
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
    import bizy_server
except Exception as e:
    print("\n\n\033[91m[BizyAir]\033[0m Fail to import 'bizy_server':" f" {e}\n\n")
