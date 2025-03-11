from bizyengine.core import BizyAirBaseNode, data_types


class InstructPixToPixConditioning(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": (data_types.CONDITIONING,),
                "negative": (data_types.CONDITIONING,),
                "vae": (data_types.VAE,),
                "pixels": ("IMAGE",),
            }
        }

    RETURN_TYPES = (data_types.CONDITIONING, data_types.CONDITIONING, "LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    # FUNCTION = "encode"

    CATEGORY = "conditioning/instructpix2pix"
