# https://docs.comfy.org/essentials/custom_node_datatypes#model-datatypes
from functools import singledispatch
from typing import Any, Dict, List, Tuple, Union
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


@singledispatch
def convert_to_custom_type(data: Any) -> Any:
    return data

@convert_to_custom_type.register(str)
def _(data: str) -> Union[str, Any]:
    return BIZYAIR_TYPE_MAP.get(data, data)


@convert_to_custom_type.register(dict)
def _(data: Dict) -> Dict:
    return {k: convert_to_custom_type(v) for k, v in data.items()}

@convert_to_custom_type.register(list)
@convert_to_custom_type.register(tuple)
def _(data: Union[List, Tuple]) -> Union[List, Tuple]:
 return type(data)(convert_to_custom_type(item) for item in data)