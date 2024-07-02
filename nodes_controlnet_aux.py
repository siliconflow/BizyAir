import numpy as np
import os

from .utils import decode_and_deserialize, send_post_request, serialize_and_encode

COMFY_AIR_SERVER_ADDRESS = os.getenv(
    "COMFY_AIR_SERVER_ADDRESS", "http://127.0.0.1:8000"
)
# auth = f"Bearer {API_KEY}"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    # "authorization": auth,
}

class BasePreprocessor:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'model_name'):
            raise TypeError("Subclass must define 'model_name'")
        cls.API_URL = f"{COMFY_AIR_SERVER_ADDRESS}{cls.model_name}"
        cls.CATEGORY = f"ComfyAir/{cls.CATEGORY}"
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    def execute(self, **kwargs):
        compress = True
        image = kwargs.pop("image")
        kwargs['image'] = serialize_and_encode(image, compress)[0]
        kwargs["is_compress"] = compress
        response = send_post_request(self.API_URL, payload=kwargs, headers=HEADERS)
        image = decode_and_deserialize(response.text)
        return (image,)

def create_node_input_types(**extra_kwargs):
    # Sync with theoritical limit from Comfy base
    # https://github.com/comfyanonymous/ComfyUI/blob/eecd69b53a896343775bcb02a4f8349e7442ffd1/nodes.py#L45
    MAX_RESOLUTION=16384
    return {
        "required": {
            "image": ("IMAGE",)
        },
        "optional": {
            **extra_kwargs,
            "resolution": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64, "display": "number",}),  # Cosmetic only: display as "number" or "slider"})
        }
    }


class PiDiNetPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/pidinetpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    
    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class ColorPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/colorpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/T2IAdapter-only"

class CannyEdgePreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/cannyedgepreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            low_threshold=("INT", {"default": 100, "min": 0, "max": 255, "step": 1}),
            high_threshold=("INT", {"default": 200, "min": 0, "max": 255, "step": 1})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class SAMPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/sampreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/others"

class BinaryPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/binarypreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            bin_threshold=("INT", {"default": 100, "min": 0, "max": 255, "step": 1})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class ScribblePreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/scribblepreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class M_LSDPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/m-lsdpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            score_threshold = ("FLOAT", {"default": 0.1, "min": 0.01, "max": 2.0, "step": 0.01}),
            dist_threshold = ("FLOAT", {"default": 0.1, "min": 0.01, "max": 20.0, "step": 0.01})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class UniFormer_SemSegPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/uniformer-semsegpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"


class Zoe_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/zoe-depthmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class MiDaS_NormalMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/midas-normalmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            a =  ("FLOAT", {"default": np.pi * 2.0, "min": 0.0, "max": np.pi * 5.0, "step": 0.05}),
            bg_threshold = ("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.05})
        )

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class MiDaS_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/midas-depthmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            a =  ("FLOAT", {"default": np.pi * 2.0, "min": 0.0, "max": np.pi * 5.0, "step": 0.05}),
            bg_threshold = ("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.05})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class OpenposePreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/openposepreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            detect_hand = (["enable", "disable"], {"default": "enable"}),
            detect_body = (["enable", "disable"], {"default": "enable"}),
            detect_face = (["enable", "disable"], {"default": "enable"})
        )
        
    RETURN_TYPES = ("IMAGE", "POSE_KEYPOINT")
    CATEGORY = "ControlNet Preprocessors/Faces and Poses Estimators"

class LineArtPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/lineartpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            coarse=(["disable", "enable"], {"default": "disable"})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class LeReS_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/leres-depthmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            rm_nearest=("FLOAT", {"default": 0.0, "min": 0.0, "max": 100, "step": 0.1}),
            rm_background=("FLOAT", {"default": 0.0, "min": 0.0, "max": 100, "step": 0.1}),
            boost=(["enable", "disable"], {"default": "disable"})
        )

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class BAE_NormalMapPreprocessor(BasePreprocessor):
    
    model_name = "/controlnet_aux/bae-normalmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class OneFormer_COCO_SemSegPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/oneformer-coco-semsegpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"

class OneFormer_ADE20K_SemSegPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/oneformer-ade20k-semsegpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"

class HEDPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/hedpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class FakeScribblePreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/fakescribblepreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )
    CATEGORY = "ControlNet Preprocessors/Line Extractors"

class TilePreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/tilepreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            pyrUp_iters = ("INT", {"default": 3, "min": 1, "max": 10, "step": 1})
        )

    CATEGORY = "ControlNet Preprocessors/tile"

class DepthAnythingV2Preprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/depthanythingv2preprocessor"
    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            ckpt_name=(["depth_anything_v2_vitg.pth", "depth_anything_v2_vitl.pth", "depth_anything_v2_vitb.pth", "depth_anything_v2_vits.pth"], {"default": "depth_anything_v2_vitl.pth"})
        )
    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class Metric3D_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/metric3d-depthmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        MAX_RESOLUTION=16384
        return create_node_input_types(
            backbone=(["vit-small", "vit-large", "vit-giant2"], {"default": "vit-small"}),
            fx=("INT", {"default": 1000, 'min': 1, 'max': MAX_RESOLUTION}),
            fy=("INT", {"default": 1000, 'min': 1, 'max': MAX_RESOLUTION})
        )


    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class Metric3D_NormalMapPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/metric3d-normalmappreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        MAX_RESOLUTION  = 16384
        return create_node_input_types(
            backbone=(["vit-small", "vit-large", "vit-giant2"], {"default": "vit-small"}),
            fx=("INT", {"default": 1000, 'min': 1, 'max': MAX_RESOLUTION}),
            fy=("INT", {"default": 1000, 'min': 1, 'max': MAX_RESOLUTION})
        )


    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"

class DWPreprocessor(BasePreprocessor):
    model_name = "/controlnet_aux/dwpreprocessor"
    @classmethod
    def INPUT_TYPES(s):
        input_types = create_node_input_types(
            detect_hand=(["enable", "disable"], {"default": "enable"}),
            detect_body=(["enable", "disable"], {"default": "enable"}),
            detect_face=(["enable", "disable"], {"default": "enable"})
        )
        input_types["optional"] = {
            **input_types["optional"],
            "bbox_detector": (
                ["yolox_l.torchscript.pt", "yolox_l.onnx", "yolo_nas_l_fp16.onnx", "yolo_nas_m_fp16.onnx", "yolo_nas_s_fp16.onnx"],
                {"default": "yolox_l.onnx"}
            ),
            "pose_estimator": (["dw-ll_ucoco_384_bs5.torchscript.pt", "dw-ll_ucoco_384.onnx", "dw-ll_ucoco.onnx"], {"default": "dw-ll_ucoco_384_bs5.torchscript.pt"})
        }
        return input_types
    
    RETURN_TYPES = ("IMAGE", "POSE_KEYPOINT")
    FUNCTION = "estimate_pose"

    CATEGORY = "ControlNet Preprocessors/Faces and Poses Estimators"

    def estimate_pose(self, *args):
        raise RuntimeError()

    
NODE_CLASS_MAPPINGS = {
    "ComfyAirPiDiNetPreprocessor": PiDiNetPreprocessor,
    "ComfyAirColorPreprocessor": ColorPreprocessor,
    "ComfyAirCannyEdgePreprocessor": CannyEdgePreprocessor,
    "ComfyAirSAMPreprocessor": SAMPreprocessor,
    "ComfyAirBinaryPreprocessor": BinaryPreprocessor,
    "ComfyAirScribblePreprocessor": ScribblePreprocessor,
    "ComfyAirM_LSDPreprocessor": M_LSDPreprocessor,
    "ComfyAirUniFormer_SemSegPreprocessor": UniFormer_SemSegPreprocessor,
    "ComfyAirZoe_DepthMapPreprocessor": Zoe_DepthMapPreprocessor,
    "ComfyAirMiDaS_NormalMapPreprocessor": MiDaS_NormalMapPreprocessor,
    "ComfyAirMiDaS_DepthMapPreprocessor": MiDaS_DepthMapPreprocessor,
    "ComfyAirOpenposePreprocessor": OpenposePreprocessor,
    "ComfyAirLineArtPreprocessor": LineArtPreprocessor,
    "ComfyAirLeReS_DepthMapPreprocessor": LeReS_DepthMapPreprocessor,
    "ComfyAirBAE_NormalMapPreprocessor": BAE_NormalMapPreprocessor,
    "ComfyAirOneFormer_COCO_SemSegPreprocessor": OneFormer_COCO_SemSegPreprocessor,
    "ComfyAirOneFormer_ADE20K_SemSegPreprocessor": OneFormer_ADE20K_SemSegPreprocessor,
    "ComfyAirHEDPreprocessor": HEDPreprocessor,
    "ComfyAirFakeScribblePreprocessor": FakeScribblePreprocessor,
    "ComfyAirTilePreprocessor": TilePreprocessor,
    "ComfyAirDepthAnythingV2Preprocessor": DepthAnythingV2Preprocessor,
    "ComfyAirMetric3D_DepthMapPreprocessor": Metric3D_DepthMapPreprocessor,
    "ComfyAirMetric3D_NormalMapPreprocessor": Metric3D_NormalMapPreprocessor,
    "ComfyAirDWPreprocessor": DWPreprocessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyAirPiDiNetPreprocessor": "ComfyAir PiDiNet Soft-Edge Lines",
    "ComfyAirColorPreprocessor": "ComfyAir Color Pallete",
    "ComfyAirCannyEdgePreprocessor": "ComfyAir Canny Edge",
    "ComfyAirSAMPreprocessor": "ComfyAir SAM Segmentor",
    "ComfyAirBinaryPreprocessor": "ComfyAir Binary Lines",
    "ComfyAirScribblePreprocessor": "ComfyAir Scribble Lines",
    "ComfyAirM_LSDPreprocessor": "ComfyAir M-LSD Lines",
    "ComfyAirUniFormer_SemSegPreprocessor": "ComfyAir UniFormer Segmentor",
    "ComfyAirZoe_DepthMapPreprocessor": "ComfyAir Zoe Depth Map",
    "ComfyAirMiDaS_NormalMapPreprocessor": "ComfyAir MiDaS Normal Map",
    "ComfyAirMiDaS_DepthMapPreprocessor": "ComfyAir MiDaS Depth Map",
    "ComfyAirOpenposePreprocessor": "ComfyAir OpenPose Pose",
    "ComfyAirLineArtPreprocessor": "ComfyAir Realistic Lineart",
    "ComfyAirLeReS_DepthMapPreprocessor": "ComfyAir LeReS Depth Map (enable boost for leres++)",
    "ComfyAirBAE_NormalMapPreprocessor": "ComfyAir BAE Normal Map",
    "ComfyAirOneFormer_COCO_SemSegPreprocessor": "ComfyAir OneFormer COCO Segmentor",
    "ComfyAirOneFormer_ADE20K_SemSegPreprocessor": "ComfyAir OneFormer ADE20K Segmentor",
    "ComfyAirHEDPreprocessor": "ComfyAir HED Soft-Edge Lines",
    "ComfyAirFakeScribblePreprocessor": "ComfyAir Fake Scribble Lines (aka scribble_hed)",
    "ComfyAirTilePreprocessor": "ComfyAir Tile",
    "ComfyAirDepthAnythingV2Preprocessor": "ComfyAir Depth Anything V2 - Relative",
    "ComfyAirMetric3D_DepthMapPreprocessor": "ComfyAir Metric3D Depth Map",
    "ComfyAirMetric3D_NormalMapPreprocessor": "ComfyAir Metric3D Normal Map",
    "ComfyAirDWPreprocessor": "ComfyAir DWPose Estimator",
}