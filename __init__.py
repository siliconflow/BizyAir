from . import supernode

NODE_CLASS_MAPPINGS = {
    **supernode.NODE_CLASS_MAPPINGS,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    **supernode.NODE_DISPLAY_NAME_MAPPINGS,
}


from . import nodes_controlnet_aux
NODE_CLASS_MAPPINGS.update(
    **nodes_controlnet_aux.NODE_CLASS_MAPPINGS
)
NODE_DISPLAY_NAME_MAPPINGS.update(
    **nodes_controlnet_aux.NODE_DISPLAY_NAME_MAPPINGS
)
