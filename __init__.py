from . import register
from . import nodes
from . import bizyair_extras

WEB_DIRECTORY = "./js"
NODE_CLASS_MAPPINGS: dict = register.NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS: dict = register.NODE_DISPLAY_NAME_MAPPINGS


from . import auth

NODE_CLASS_MAPPINGS.update(
    {**auth.NODE_CLASS_MAPPINGS,}
)
NODE_DISPLAY_NAME_MAPPINGS.update(
    {**auth.NODE_DISPLAY_NAME_MAPPINGS,}
)


from . import supernode

NODE_CLASS_MAPPINGS.update(**supernode.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**supernode.NODE_DISPLAY_NAME_MAPPINGS)

from . import llm

NODE_CLASS_MAPPINGS.update(**llm.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**llm.NODE_DISPLAY_NAME_MAPPINGS)

from . import nodes_controlnet_aux

NODE_CLASS_MAPPINGS.update(**nodes_controlnet_aux.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**nodes_controlnet_aux.NODE_DISPLAY_NAME_MAPPINGS)

from . import kolors

NODE_CLASS_MAPPINGS.update(**kolors.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**kolors.NODE_DISPLAY_NAME_MAPPINGS)


from . import nodes_controlnet_union_sdxl

NODE_CLASS_MAPPINGS.update(**nodes_controlnet_union_sdxl.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(
    **nodes_controlnet_union_sdxl.NODE_DISPLAY_NAME_MAPPINGS
)

from . import mzkolors

NODE_CLASS_MAPPINGS.update(**mzkolors.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**mzkolors.NODE_DISPLAY_NAME_MAPPINGS)
