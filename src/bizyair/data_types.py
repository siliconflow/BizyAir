# https://docs.comfy.org/essentials/custom_node_datatypes#model-datatypes
# Model datatypes
MODEL = "BIZYAIR_MODEL"
CLIP = "BIZYAIR_CLIP"
VAE = "BIZYAIR_VAE"
CONDITIONING = "BIZYAIR_CONDITIONING"
CONTROL_NET = "BIZYAIR_CONTROL_NET"
UPSCALE_MODEL = "BIZYAIR_UPSCALE_MODEL"


def is_model_datatype(datatype):
    return datatype in [MODEL, CLIP, VAE, CONDITIONING, CONTROL_NET]
