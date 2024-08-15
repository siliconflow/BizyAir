import os
import sys
import warnings

current_path = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(current_path, "src")
if os.path.isdir(src_path):
    sys.path.insert(0, src_path)

from bizyair import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./js"

try:
    from . import nodes
    from . import bizyair_extras
    from . import showcase
    from . import auth
    from . import supernode
    from . import llm
    from . import nodes_controlnet_aux
    from . import nodes_controlnet_union_sdxl
    from . import mzkolors

    def update_mappings(module):
        NODE_CLASS_MAPPINGS.update(**module.NODE_CLASS_MAPPINGS)
        NODE_DISPLAY_NAME_MAPPINGS.update(**module.NODE_DISPLAY_NAME_MAPPINGS)

    update_mappings(auth)
    update_mappings(supernode)
    update_mappings(llm)
    update_mappings(nodes_controlnet_aux)
    update_mappings(nodes_controlnet_union_sdxl)
    update_mappings(mzkolors)

except ImportError as e:
    warnings.warn(f"Import error: {e}")
except Exception as e:
    warnings.warn(f"An error occurred: {e}")
