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
      "clip_name1": "t5xxl_fp16.safetensors",
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
      "text": "close up photo of a rabbit, forest in spring, haze, halation, bloom, dramatic atmosphere, centred, rule of thirds, 200mm 1.4f macro shot",
      "clip": [
        "36",
        0
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
        "48",
        0
      ],
      "conditioning": [
        "37",
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
      "unet_name": "flux/pixelwave-flux1-dev.safetensors",
      "weight_dtype": "default"
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
        "66",
        0
      ]
    },
    "class_type": "BizyAir_SamplerCustomAdvanced",
    "_meta": {
      "title": "☁️BizyAir SamplerCustomAdvanced"
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
  "56": {
    "inputs": {
      "images": [
        "54",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "预览图像"
    }
  },
  "58": {
    "inputs": {
      "scheduler": "simple",
      "steps": 20,
      "denoise": 1,
      "model": [
        "48",
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
      "noise_seed": 0
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
  "66": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptySD3LatentImage",
    "_meta": {
      "title": "空Latent图像（SD3）"
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
param_node =  {
        "inputs": {},
        "class_type": "BizyAir_PassParameter",
        "_meta": {
        "title": "☁️BizyAir PassParameter",
        "api_key": BIZYAIR_API_KEY,
        "prompt_id": "a-unique-prompt-id"
        }
    }
prompt["bizyair_magic_node"]=param_node
queue_prompt(prompt)
```
