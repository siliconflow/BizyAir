import pytest
from bizyengine.core.path_utils import guess_config

test_data = {
    "ckpt_name": [
        ("sdxl/counterfeitxl_v25.safetensors", "sdxl_config.yaml"),
        ("sdxl/dreamshaperXL_lightningDPMSDE.safetensors", "sdxl_config.yaml"),
        ("sdxl/dreamshaperXL_v21TurboDPMSDE.safetensors", "sdxl_config.yaml"),
        ("sdxl/HelloWorldXL_v70.safetensors", "sdxl_config.yaml"),
        ("sdxl/juggernautXL_v9Rdphoto2Lightning.safetensors", "sdxl_config.yaml"),
        ("sdxl/Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors", "sdxl_config.yaml"),
        ("sdxl/Juggernaut_X_RunDiffusion_Hyper.safetensors", "sdxl_config.yaml"),
        ("sdxl/mannEDreams_v004.safetensors", "sdxl_config.yaml"),
        ("sdxl/realisticStockPhoto_v20.safetensors", "sdxl_config.yaml"),
        ("sdxl/samaritan3dCartoon_v40SDXL.safetensors", "sdxl_config.yaml"),
    ],
    "unet_name": [
        ("kolors/Kolors-Inpainting.safetensors", "kolors_config.yaml"),
        ("kolors/Kolors.safetensors", "kolors_config.yaml"),
        ("flux/flux1-schnell.sft", "flux_config.yaml"),
        ("flux/flux1-dev.sft", "flux_dev_config.yaml"),
    ],
    "vae_name": [
        ("sdxl/sdxl_vae.safetensors", "sdxl_config.yaml"),
        ("flux/ae.sft", "flux_config.yaml"),
    ],
    # 'clip_name': [
    #     ('clip_l.safetensors', "clip_config.yaml"),
    #     ('t5xxl_fp16.safetensors', "t5_config.yaml"),
    #     ('t5xxl_fp8_e4m3fn.safetensors', "t5_config.yaml")
    # ]
}


@pytest.mark.path_utils
@pytest.mark.parametrize("input_type, input_values_with_expected", test_data.items())
def test_guess_config(input_type, input_values_with_expected):
    for input_value, expected_result in input_values_with_expected:
        result: str = guess_config(**{input_type: input_value})
        assert result.endswith(
            expected_result
        ), f"Test failed for {input_type=} and {input_value=}. Expected {expected_result}, but got {result}."
