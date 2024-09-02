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

# bizy_server
bizyair_adv_is_not_installed = False
try:
    import crcmod
    import oss2
except ImportError:
    bizyair_adv_is_not_installed = True
    print("\n\n\033[91m[WARN]\033[0m BizyAir: Please run"
          " 'pip install -r requirements_adv.txt' to install depencies for modelhost feature.\n\n")

if not bizyair_adv_is_not_installed:
    import bizy_server
