from bizyair import BizyAirBaseNode

class BizyAir_mochi(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"default": "Close-up of a chameleon's eye, with its scaly skin changing color. Ultra high resolution 4k."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 50}),
                "width": ("INT", {"default": 848, "min": 64, "max": 1536, "step": 8}),
                "height": ("INT", {"default": 480, "min": 64, "max": 1536, "step": 8}),
                "frames": ("INT", {"default": 96, "min": 1, "max": 4096}),
                "fps": ("INT", {"default": 22, "min": 8, "max": 64}),
                "filename": ("STRING", {"default": "mochi"}),                    
            }
        }

    RETURN_TYPES = ("STRING",)
    # RETURN_NAMES = ("path",)
    CATEGORY = "☁️BizyAir/mochi"
    NODE_DISPLAY_NAME = "☁️BizyAir mochi"
    OUTPUT_NODE = True