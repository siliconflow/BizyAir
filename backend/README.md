## Server Mode

```bash
export BIZYAIR_API_KEY="your api key"
export BIZYAIR_SERVER_MODE=1
```

```python
import json
import os
from urllib import request

BIZYAIR_API_KEY=os.getenv("BIZYAIR_API_KEY", "")

prompt_text = """
{
  "36": {
    "inputs": {
      "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
      "clip_name2": "clip_l.safetensors",
      "type": "flux"
    },
    "class_type": "BizyAir_DualCLIPLoader",
    "_meta": {
      "title": "☁️BizyAir DualCLIPLoader"
    }
  },
  "37": {
    "inputs": {
      "text": "a very cute cat.",
      "clip": [
        "65",
        1
      ]
    },
    "class_type": "BizyAir_CLIPTextEncode",
    "_meta": {
      "title": "☁️BizyAir CLIP Text Encode (Prompt)"
    }
  },
  "47": {
    "inputs": {
      "model": [
        "65",
        0
      ],
      "conditioning": [
        "67",
        0
      ]
    },
    "class_type": "BizyAir_BasicGuider",
    "_meta": {
      "title": "☁️BizyAir BasicGuider"
    }
  },
  "48": {
    "inputs": {
      "unet_name": "flux/flux1-dev.sft",
      "weight_dtype": "fp8_e4m3fn"
    },
    "class_type": "BizyAir_UNETLoader",
    "_meta": {
      "title": "☁️BizyAir Load Diffusion Model"
    }
  },
  "50": {
    "inputs": {
      "noise": [
        "59",
        0
      ],
      "guider": [
        "47",
        0
      ],
      "sampler": [
        "60",
        0
      ],
      "sigmas": [
        "58",
        0
      ],
      "latent_image": [
        "51",
        0
      ]
    },
    "class_type": "BizyAir_SamplerCustomAdvanced",
    "_meta": {
      "title": "☁️BizyAir SamplerCustomAdvanced"
    }
  },
  "51": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "空Latent图像"
    }
  },
  "54": {
    "inputs": {
      "samples": [
        "50",
        0
      ],
      "vae": [
        "55",
        0
      ]
    },
    "class_type": "BizyAir_VAEDecode",
    "_meta": {
      "title": "☁️BizyAir VAE Decode"
    }
  },
  "55": {
    "inputs": {
      "vae_name": "flux/ae.sft"
    },
    "class_type": "BizyAir_VAELoader",
    "_meta": {
      "title": "☁️BizyAir Load VAE"
    }
  },
  "58": {
    "inputs": {
      "scheduler": "normal",
      "steps": 20,
      "denoise": 1,
      "model": [
        "65",
        0
      ]
    },
    "class_type": "BizyAir_BasicScheduler",
    "_meta": {
      "title": "☁️BizyAir BasicScheduler"
    }
  },
  "59": {
    "inputs": {
      "noise_seed": 9999921
    },
    "class_type": "BizyAir_RandomNoise",
    "_meta": {
      "title": "☁️BizyAir RandomNoise"
    }
  },
  "60": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "BizyAir_KSamplerSelect",
    "_meta": {
      "title": "☁️BizyAir KSamplerSelect"
    }
  },
  "65": {
    "inputs": {
      "lora_name": "墨幽-F.1-Lora-3D卡通_v1",
      "strength_model": 1,
      "strength_clip": 1,
      "model_version_id": 213,
      "model": [
        "48",
        0
      ],
      "clip": [
        "36",
        0
      ]
    },
    "class_type": "BizyAir_LoraLoader",
    "_meta": {
      "title": "☁️BizyAir Load LoRA"
    }
  },
  "67": {
    "inputs": {
      "guidance": 3.5,
      "conditioning": [
        "37",
        0
      ]
    },
    "class_type": "BizyAir_FluxGuidance",
    "_meta": {
      "title": "☁️BizyAir FluxGuidance"
    }
  },
  "70": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "54",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "保存图像"
    }
  },
    "bizyair_magic_node": {
        "inputs": {},
        "class_type": "BizyAir_PassParameter",
        "_meta": {
        "title": "☁️BizyAir PassParameter",
        "api_key": "",
        "prompt_id": "a-unique-prompt-id"
        }
    }
}
"""

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://127.0.0.1:9111/prompt", data=data)
    request.urlopen(req)


prompt = json.loads(prompt_text)
prompt["bizyair_magic_node"]["_meta"]["api_key"]=BIZYAIR_API_KEY

queue_prompt(prompt)
```
