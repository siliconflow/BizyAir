from bizyengine.core import BizyAirBaseNode


class CogView4_6B_Pipe(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(self):
        default_prompt = "A vibrant cherry red sports car sits proudly under the gleaming sun, its polished exterior smooth and flawless, casting a mirror-like reflection. The car features a low, aerodynamic body, angular headlights that gaze forward like predatory eyes, and a set of black, high-gloss racing rims that contrast starkly with the red. A subtle hint of chrome embellishes the grille and exhaust, while the tinted windows suggest a luxurious and private interior. The scene conveys a sense of speed and elegance, the car appearing as if it's about to burst into a sprint along a coastal road, with the ocean's azure waves crashing in the background.The license plate number of the car is 'CogView4'. The car sprinted along a coastal road, with the same sports car printed on the roadside billboard and large Chinese text '遥遥领先' written to it. The text was yellow, with thick strokes and heavy shadow lines."
        return {
            "required": {
                "prompt": ("STRING", {"default": default_prompt, "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 1e14}),
                "guidance_scale": (
                    "FLOAT",
                    {"default": 3.5, "min": 0.1, "max": 100, "step": 0.1},
                ),
                "num_images_per_prompt": (
                    "INT",
                    {"default": 1, "min": 1, "max": 4, "step": 1},
                ),
                "num_inference_steps": (
                    "INT",
                    {"default": 30, "min": 1, "max": 100, "step": 1},
                ),
                "width": ("INT", {"default": 1536, "min": 16, "max": 4096, "step": 16}),
                "height": ("INT", {"default": 832, "min": 16, "max": 4096, "step": 16}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    CATEGORY = "CogView4 Wrapper"
