# https://docs.comfy.org/essentials/custom_node_datatypes#model-datatypes
# Model datatypes
MODEL = "BIZYAIR_MODEL"
CLIP = "BIZYAIR_CLIP"
VAE = "BIZYAIR_VAE"
CONDITIONING = "BIZYAIR_CONDITIONING"
CONTROL_NET = "BIZYAIR_CONTROL_NET"
UPSCALE_MODEL = "BIZYAIR_UPSCALE_MODEL"
INSTANTID = "BIZYAIR_INSTANTID"
FACEANALYSIS = "BIZYAIR_FACEANALYSIS"


def is_model_datatype(datatype: str) -> bool:
    return datatype in [MODEL, CLIP, VAE, CONDITIONING, CONTROL_NET]


# https://docs.comfy.org/essentials/custom_node_images_and_masks
def is_send_request_datatype(datatype: str) -> bool:
    return datatype in {"IMAGE", "LATENT", "MASK"}
