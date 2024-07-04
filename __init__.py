from . import supernode
from . import llm

NODE_CLASS_MAPPINGS = {
    **supernode.NODE_CLASS_MAPPINGS,
    **llm.NODE_CLASS_MAPPINGS,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    **supernode.NODE_DISPLAY_NAME_MAPPINGS,
    **llm.NODE_DISPLAY_NAME_MAPPINGS,
}

WEB_DIRECTORY = "./js"
