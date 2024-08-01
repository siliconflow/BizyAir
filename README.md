# BizyAir

- [2024/07/31] 🌩️ The super-resolution node has been released, capable of enlarging images four times their original size. [BizyAir Photorealistic Image Super Resolution](https://siliconflow.github.io/BizyAir/others/index.html#bizyair-photorealistic-image-super-resolution)
- [2024/07/25] 🌩️ Users can load BizyAir workflow examples directly by clicking the "☁️BizyAir Workflow Examples" button. [Example GIF](./docs/docs/getting-started/imgs/run-bizyair-examples.gif)
- [2024/07/23] 🌩️ [BizyAir ChatGLM3 Text Encode](./examples/bizyair_showcase_run_with_local_nodes.json) node is released.
- [2024/07/16] 🌩️ [BizyAir Controlnet Union SDXL 1.0](https://siliconflow.github.io/BizyAir/controlnet-union/introduce.html) node is released.
- [2024/07/14] 🌩️ We release Image Caption nodes and add a tutorial for utilizing the LLM node. [AI Assistant](https://siliconflow.github.io/BizyAir/ai-assistants/introduce.html)
- [2024/07/11] 🌩️ We release new nodes that can perform ControlNet preprocessing. [BizyAir Controlnet Auxiliary Preprocessors](https://siliconflow.github.io/BizyAir/controlnet-preprocessor/introduce.html)
- [2024/07/11] 🌩️ We release new nodes, featuring removing image background, photo-quality image generation, and animation super-resolution capabilities.
- [2024/07/10] 🌩️ We release nodes that support Kolors and LLM(large language models). [Kolors](https://siliconflow.github.io/BizyAir/kolors/introduce.html)

BizyAir is a collection of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) nodes that help you overcome environmental and hardware limitations, allowing you to more easily generate high-quality content with ComfyUI.

![](./docs/docs/getting-started/imgs/run-bizyair-examples.gif)

BizyAir nodes are capable of operating in conjunction with local nodes. For example, the workflow below shows the use of BizyAir for ChatGLM3 text encoding and VAE decoding, while employing a local KSampler.

 ![](./docs/docs/getting-started/imgs/run-with-local-nodes.gif)

## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Installation](#installation)
- [Examples](#examples)


## Features

Run ComfyUI anywhere, anytime, without worrying about the environment or hardware requirements.

## Usage

Please see the [Quick Start](https://siliconflow.github.io/BizyAir/getting-started/quick-start.html) page to set up BizyAir.

Make sure to **set your API KEY** for the **first time** use!

![](./docs/docs/getting-started/imgs/how-to-set-key.gif)

## Installation

You can install BizyAir through several methods: using the ComfyUI Manager, the Comfy CLI, downloading the standalone package for Windows, or by cloning the BizyAir repository into the custom_nodes subdirectory of ComfyUI. 

### Method 1: Install via ComfyUI Manager

Assuming your ComfyUI already has the [ComfyUI Manager installed](https://github.com/ltdrdata/ComfyUI-Manager?tab=readme-ov-file#installation), search for BizyAir as shown in the image below. Click "Install" to complete the installation.
![ComfyUI_Manager_BizyAir_Search_Screenshot](./docs/docs/getting-started/imgs/ComfyUI_Manager_BizyAir_Search_Screenshot.png)


### Method 2: Install via git clone

You can install BizyAir by downloading the BizyAir repository to the custom_nodes subdirectory of ComfyUI by using git clone.

```bash
cd /path/to/ComfyUI/custom_nodes && \
git clone https://github.com/siliconflow/BizyAir.git
```

Then, restart ComfyUI.

### Method 3: Install via Comfy CLI

- Prerequisites
    - Ensure `pip install comfy-cli` is installed.
    - Installing ComfyUI `comfy install`
  
To install the `BizyAir`, use the following command:

```shell
comfy node install bizyair
```


### Method 4: Download windows portable ComfyUI

For NA/EU users:

https://github.com/siliconflow/ComfyUI/releases/tag/latest

For CN users:

https://bizy-air.oss-cn-beijing.aliyuncs.com/new_ComfyUI_windows_portable_nvidia_none_or_cpu.7z


## Examples

There are some workflow examples in the [examples](./examples) directory.
