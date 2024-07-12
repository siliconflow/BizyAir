from . import auth


NODE_CLASS_MAPPINGS = {
    **auth.NODE_CLASS_MAPPINGS,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    **auth.NODE_DISPLAY_NAME_MAPPINGS,
}

WEB_DIRECTORY = "./js"

# from . import supernode

# NODE_CLASS_MAPPINGS.update(**supernode.NODE_CLASS_MAPPINGS)
# NODE_DISPLAY_NAME_MAPPINGS.update(**supernode.NODE_DISPLAY_NAME_MAPPINGS)

from . import llm

NODE_CLASS_MAPPINGS.update(**llm.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**llm.NODE_DISPLAY_NAME_MAPPINGS)

# from . import nodes_controlnet_aux

# NODE_CLASS_MAPPINGS.update(**nodes_controlnet_aux.NODE_CLASS_MAPPINGS)
# NODE_DISPLAY_NAME_MAPPINGS.update(**nodes_controlnet_aux.NODE_DISPLAY_NAME_MAPPINGS)

from . import kolors

NODE_CLASS_MAPPINGS.update(**kolors.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(**kolors.NODE_DISPLAY_NAME_MAPPINGS)


from . import nodes_controlnet_union_sdxl

NODE_CLASS_MAPPINGS.update(**nodes_controlnet_union_sdxl.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(
    **nodes_controlnet_union_sdxl.NODE_DISPLAY_NAME_MAPPINGS
)
