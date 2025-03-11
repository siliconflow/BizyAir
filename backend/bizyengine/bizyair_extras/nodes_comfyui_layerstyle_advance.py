from bizyengine.core import BizyAirBaseNode

# layerstyle advance
NODE_NAME = "SegmentAnythingUltra V2"
sam_model_dir_name = "sams"
sam_model_list = {
    "sam_vit_h (2.56GB)": {
        "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    },
    # "sam_vit_l (1.25GB)": {
    #     "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    # },
    # "sam_vit_b (375MB)": {
    #     "model_url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    # },
    # "sam_hq_vit_h (2.57GB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth"
    # },
    # "sam_hq_vit_l (1.25GB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_l.pth"
    # },
    # "sam_hq_vit_b (379MB)": {
    #     "model_url": "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_b.pth"
    # },
    # "mobile_sam(39MB)": {
    #     "model_url": "https://github.com/ChaoningZhang/MobileSAM/blob/master/weights/mobile_sam.pt"
    # }
}

groundingdino_model_dir_name = "grounding-dino"
groundingdino_model_list = {
    "GroundingDINO_SwinT_OGC (694MB)": {
        "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinT_OGC.cfg.py",
        "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth",
    },
    # "GroundingDINO_SwinB (938MB)": {
    #     "config_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/GroundingDINO_SwinB.cfg.py",
    #     "model_url": "https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swinb_cogcoor.pth"
    # },
}


def list_sam_model():
    return list(sam_model_list.keys())


def list_groundingdino_model():
    return list(groundingdino_model_list.keys())


class SegmentAnythingUltraV2(BizyAirBaseNode):

    CLASS_TYPE_NAME = "LayerMask: SegmentAnythingUltra V2"
    NODE_DISPLAY_NAME = "LayerMask: SegmentAnythingUltra V2(Advance)"

    def __init__(self):
        self.SAM_MODEL = None
        self.DINO_MODEL = None
        self.previous_sam_model = ""
        self.previous_dino_model = ""
        pass

    @classmethod
    def INPUT_TYPES(cls):

        method_list = [
            "VITMatte",
            "VITMatte(local)",
            "PyMatting",
            "GuidedFilter",
        ]
        device_list = ["cuda"]
        return {
            "required": {
                "image": ("IMAGE",),
                "sam_model": (list_sam_model(),),
                "grounding_dino_model": (list_groundingdino_model(),),
                "threshold": (
                    "FLOAT",
                    {"default": 0.3, "min": 0, "max": 1.0, "step": 0.01},
                ),
                "detail_method": (method_list,),
                "detail_erode": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "detail_dilate": (
                    "INT",
                    {"default": 6, "min": 1, "max": 255, "step": 1},
                ),
                "black_point": (
                    "FLOAT",
                    {
                        "default": 0.15,
                        "min": 0.01,
                        "max": 0.98,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "white_point": (
                    "FLOAT",
                    {
                        "default": 0.99,
                        "min": 0.02,
                        "max": 0.99,
                        "step": 0.01,
                        "display": "slider",
                    },
                ),
                "process_detail": ("BOOLEAN", {"default": True}),
                "prompt": ("STRING", {"default": "subject"}),
                "device": (device_list,),
                "max_megapixels": (
                    "FLOAT",
                    {"default": 2.0, "min": 1, "max": 999, "step": 0.1},
                ),
                "cache_model": ("BOOLEAN", {"default": True}),
            },
            "optional": {},
        }

    RETURN_TYPES = (
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "image",
        "mask",
    )
    # FUNCTION = "segment_anything_ultra_v2"
    CATEGORY = "😺dzNodes/LayerMask"


NODE_CLASS_MAPPINGS = {
    "LayerMask: SegmentAnythingUltra V2": SegmentAnythingUltraV2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LayerMask: SegmentAnythingUltra V2": "LayerMask: SegmentAnythingUltra V2(Advance)",
}
