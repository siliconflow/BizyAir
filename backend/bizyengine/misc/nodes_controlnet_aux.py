import json
import os

import numpy as np
import torch
from bizyengine.core import BizyAirMiscBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS

from .utils import decode_and_deserialize, serialize_and_encode

# Sync with theoritical limit from Comfy base
# https://github.com/comfyanonymous/ComfyUI/blob/eecd69b53a896343775bcb02a4f8349e7442ffd1/nodes.py#L45
MAX_RESOLUTION = 1024


class BasePreprocessor(BizyAirMiscBaseNode):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "model_name"):
            raise TypeError("Subclass must define 'model_name'")
        cls.API_URL = f"{BIZYAIR_SERVER_ADDRESS}{cls.model_name}"
        cls.CATEGORY = f"☁️BizyAir/{cls.CATEGORY}"

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    def execute(self, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])

        compress = True
        image: torch.Tensor = kwargs.pop("image")
        device = image.device
        kwargs["image"] = serialize_and_encode(image, compress)[0]
        kwargs["is_compress"] = compress
        if "prompt_id" in extra_data:
            kwargs["prompt_id"] = extra_data["prompt_id"]
        data = json.dumps(kwargs).encode("utf-8")

        image_np = client.send_request(
            url=self.API_URL,
            data=data,
            headers=headers,
            callback=None,
            response_handler=decode_and_deserialize,
        )
        image_torch = torch.from_numpy(image_np).to(device)
        return (image_torch,)


def create_node_input_types(**extra_kwargs):
    return {
        "required": {"image": ("IMAGE",)},
        "optional": {
            **extra_kwargs,
            "resolution": (
                "INT",
                {
                    "default": 512,
                    "min": 64,
                    "max": MAX_RESOLUTION,
                    "step": 64,
                    "display": "number",
                },
            ),  # Cosmetic only: display as "number" or "slider"})
        },
    }


class PiDiNetPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxpidinetpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class ColorPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxcolorpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/T2IAdapter-only"


class CannyEdgePreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxcannyedgepreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            low_threshold=("INT", {"default": 100, "min": 0, "max": 255, "step": 1}),
            high_threshold=("INT", {"default": 200, "min": 0, "max": 255, "step": 1}),
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class SAMPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxsampreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"


class BinaryPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxbinarypreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            bin_threshold=("INT", {"default": 100, "min": 0, "max": 255, "step": 1})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class ScribblePreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxscribblepreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class M_LSDPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxm-lsdpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            score_threshold=(
                "FLOAT",
                {"default": 0.1, "min": 0.01, "max": 2.0, "step": 0.01},
            ),
            dist_threshold=(
                "FLOAT",
                {"default": 0.1, "min": 0.01, "max": 20.0, "step": 0.01},
            ),
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class UniFormer_SemSegPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxuniformer-semsegpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"


class Zoe_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxzoe-depthmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class MiDaS_NormalMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxmidas-normalmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            a=(
                "FLOAT",
                {"default": np.pi * 2.0, "min": 0.0, "max": np.pi * 5.0, "step": 0.05},
            ),
            bg_threshold=("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.05}),
        )

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class MiDaS_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxmidas-depthmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            a=(
                "FLOAT",
                {"default": np.pi * 2.0, "min": 0.0, "max": np.pi * 5.0, "step": 0.05},
            ),
            bg_threshold=("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.05}),
        )

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class OpenposePreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxopenposepreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            detect_hand=(["enable", "disable"], {"default": "enable"}),
            detect_body=(["enable", "disable"], {"default": "enable"}),
            detect_face=(["enable", "disable"], {"default": "enable"}),
        )

    RETURN_TYPES = ("IMAGE", "POSE_KEYPOINT")
    CATEGORY = "ControlNet Preprocessors/Faces and Poses Estimators"


class LineArtPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxlineartpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            coarse=(["disable", "enable"], {"default": "disable"})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class LeReS_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxleres-depthmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            rm_nearest=("FLOAT", {"default": 0.0, "min": 0.0, "max": 100, "step": 0.1}),
            rm_background=(
                "FLOAT",
                {"default": 0.0, "min": 0.0, "max": 100, "step": 0.1},
            ),
            boost=(["enable", "disable"], {"default": "disable"}),
        )

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class BAE_NormalMapPreprocessor(BasePreprocessor):

    model_name = "/supernode/controlnetauxbae-normalmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class OneFormer_COCO_SemSegPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxoneformer-coco-semsegpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    RETURN_TYPES = ("IMAGE",)

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"


class OneFormer_ADE20K_SemSegPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxoneformer-ade20k-semsegpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types()

    CATEGORY = "ControlNet Preprocessors/Semantic Segmentation"


class HEDPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxhedpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class FakeScribblePreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxfakescribblepreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            safe=(["enable", "disable"], {"default": "enable"})
        )

    CATEGORY = "ControlNet Preprocessors/Line Extractors"


class TilePreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxtilepreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            pyrUp_iters=("INT", {"default": 3, "min": 1, "max": 10, "step": 1})
        )

    CATEGORY = "ControlNet Preprocessors/tile"


class DepthAnythingV2Preprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxdepthanythingv2preprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            ckpt_name=(
                [
                    "depth_anything_v2_vitg.pth",
                    "depth_anything_v2_vitl.pth",
                    "depth_anything_v2_vitb.pth",
                    "depth_anything_v2_vits.pth",
                ],
                {"default": "depth_anything_v2_vitl.pth"},
            )
        )

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class Metric3D_DepthMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxmetric3d-depthmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            backbone=(
                ["vit-small", "vit-large", "vit-giant2"],
                {"default": "vit-small"},
            ),
            fx=("INT", {"default": 1000, "min": 1, "max": MAX_RESOLUTION}),
            fy=("INT", {"default": 1000, "min": 1, "max": MAX_RESOLUTION}),
        )

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class Metric3D_NormalMapPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxmetric3d-normalmappreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        return create_node_input_types(
            backbone=(
                ["vit-small", "vit-large", "vit-giant2"],
                {"default": "vit-small"},
            ),
            fx=("INT", {"default": 1000, "min": 1, "max": MAX_RESOLUTION}),
            fy=("INT", {"default": 1000, "min": 1, "max": MAX_RESOLUTION}),
        )

    CATEGORY = "ControlNet Preprocessors/Normal and Depth Estimators"


class DWPreprocessor(BasePreprocessor):
    model_name = "/supernode/controlnetauxdwpreprocessor"

    @classmethod
    def INPUT_TYPES(s):
        input_types = create_node_input_types(
            detect_hand=(["enable", "disable"], {"default": "enable"}),
            detect_body=(["enable", "disable"], {"default": "enable"}),
            detect_face=(["enable", "disable"], {"default": "enable"}),
        )
        input_types["optional"] = {
            **input_types["optional"],
            "bbox_detector": (
                [
                    "yolox_l.torchscript.pt",
                    "yolox_l.onnx",
                    "yolo_nas_l_fp16.onnx",
                    "yolo_nas_m_fp16.onnx",
                    "yolo_nas_s_fp16.onnx",
                ],
                {"default": "yolox_l.onnx"},
            ),
            "pose_estimator": (
                [
                    "dw-ll_ucoco_384_bs5.torchscript.pt",
                    "dw-ll_ucoco_384.onnx",
                    "dw-ll_ucoco.onnx",
                ],
                {"default": "dw-ll_ucoco_384_bs5.torchscript.pt"},
            ),
        }
        return input_types

    CATEGORY = "ControlNet Preprocessors/Faces and Poses Estimators"


NODE_CLASS_MAPPINGS = {
    "BizyAirPiDiNetPreprocessor": PiDiNetPreprocessor,
    "BizyAirColorPreprocessor": ColorPreprocessor,
    "BizyAirCannyEdgePreprocessor": CannyEdgePreprocessor,
    "BizyAirSAMPreprocessor": SAMPreprocessor,
    "BizyAirBinaryPreprocessor": BinaryPreprocessor,
    "BizyAirScribblePreprocessor": ScribblePreprocessor,
    "BizyAirM_LSDPreprocessor": M_LSDPreprocessor,
    "BizyAirUniFormer_SemSegPreprocessor": UniFormer_SemSegPreprocessor,
    "BizyAirZoe_DepthMapPreprocessor": Zoe_DepthMapPreprocessor,
    "BizyAirMiDaS_NormalMapPreprocessor": MiDaS_NormalMapPreprocessor,
    "BizyAirMiDaS_DepthMapPreprocessor": MiDaS_DepthMapPreprocessor,
    "BizyAirOpenposePreprocessor": OpenposePreprocessor,
    "BizyAirLineArtPreprocessor": LineArtPreprocessor,
    "BizyAirLeReS_DepthMapPreprocessor": LeReS_DepthMapPreprocessor,
    "BizyAirBAE_NormalMapPreprocessor": BAE_NormalMapPreprocessor,
    "BizyAirOneFormer_COCO_SemSegPreprocessor": OneFormer_COCO_SemSegPreprocessor,
    "BizyAirOneFormer_ADE20K_SemSegPreprocessor": OneFormer_ADE20K_SemSegPreprocessor,
    "BizyAirHEDPreprocessor": HEDPreprocessor,
    "BizyAirFakeScribblePreprocessor": FakeScribblePreprocessor,
    "BizyAirTilePreprocessor": TilePreprocessor,
    "BizyAirDepthAnythingV2Preprocessor": DepthAnythingV2Preprocessor,
    "BizyAirMetric3D_DepthMapPreprocessor": Metric3D_DepthMapPreprocessor,
    "BizyAirMetric3D_NormalMapPreprocessor": Metric3D_NormalMapPreprocessor,
    "BizyAirDWPreprocessor": DWPreprocessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirPiDiNetPreprocessor": "☁️BizyAir PiDiNet Soft-Edge Lines",
    "BizyAirColorPreprocessor": "☁️BizyAir Color Pallete",
    "BizyAirCannyEdgePreprocessor": "☁️BizyAir Canny Edge",
    "BizyAirSAMPreprocessor": "☁️BizyAir SAM Segmentor",
    "BizyAirBinaryPreprocessor": "☁️BizyAir Binary Lines",
    "BizyAirScribblePreprocessor": "☁️BizyAir Scribble Lines",
    "BizyAirM_LSDPreprocessor": "☁️BizyAir M-LSD Lines",
    "BizyAirUniFormer_SemSegPreprocessor": "☁️BizyAir UniFormer Segmentor",
    "BizyAirZoe_DepthMapPreprocessor": "☁️BizyAir Zoe Depth Map",
    "BizyAirMiDaS_NormalMapPreprocessor": "☁️BizyAir MiDaS Normal Map",
    "BizyAirMiDaS_DepthMapPreprocessor": "☁️BizyAir MiDaS Depth Map",
    "BizyAirOpenposePreprocessor": "☁️BizyAir OpenPose Pose",
    "BizyAirLineArtPreprocessor": "☁️BizyAir Realistic Lineart",
    "BizyAirLeReS_DepthMapPreprocessor": "☁️BizyAir LeReS Depth Map (enable boost for leres++)",
    "BizyAirBAE_NormalMapPreprocessor": "☁️BizyAir BAE Normal Map",
    "BizyAirOneFormer_COCO_SemSegPreprocessor": "☁️BizyAir OneFormer COCO Segmentor",
    "BizyAirOneFormer_ADE20K_SemSegPreprocessor": "☁️BizyAir OneFormer ADE20K Segmentor",
    "BizyAirHEDPreprocessor": "☁️BizyAir HED Soft-Edge Lines",
    "BizyAirFakeScribblePreprocessor": "☁️BizyAir Fake Scribble Lines (aka scribble_hed)",
    "BizyAirTilePreprocessor": "☁️BizyAir Tile",
    "BizyAirDepthAnythingV2Preprocessor": "☁️BizyAir Depth Anything V2 - Relative",
    "BizyAirMetric3D_DepthMapPreprocessor": "☁️BizyAir Metric3D Depth Map",
    "BizyAirMetric3D_NormalMapPreprocessor": "☁️BizyAir Metric3D Normal Map",
    "BizyAirDWPreprocessor": "☁️BizyAir DWPose Estimator",
}
