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
STYLE_MODEL = "BIZYAIR_STYLE_MODEL"


BIZYAIR_TYPE_MAP = {
    "MODEL": MODEL,
    "CLIP": CLIP,
    "VAE": VAE,
    "CONDITIONING": CONDITIONING,
    "CONTROL_NET": CONTROL_NET,
    "UPSCALE_MODEL": UPSCALE_MODEL,
    "INSTANTID": INSTANTID,
    "FACEANALYSIS": FACEANALYSIS,
    "STYLE_MODEL": STYLE_MODEL,
}


def is_model_datatype(datatype):
    return datatype in [MODEL, CLIP, VAE, CONDITIONING, CONTROL_NET, STYLE_MODEL]


# https://docs.comfy.org/essentials/custom_node_images_and_masks
def is_send_request_datatype(datatype: str) -> bool:
    return datatype in {"IMAGE", "LATENT", "MASK", "STRING", "FLOAT", "INT"}
