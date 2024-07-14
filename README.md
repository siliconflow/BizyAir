# BizyAir

- [2024/07/14] 🌩️ We release Image Caption nodes and add a tutorial for utilizing the LLM node. [AI Assistant](https://siliconflow.github.io/BizyAir/ai-assistants/introduce.html)
- [2024/07/11] 🌩️ We release new nodes that can perform ControlNet preprocessing. [BizyAir Controlnet Auxiliary Preprocessors](https://siliconflow.github.io/BizyAir/controlnet-preprocessor/introduce.html)
- [2024/07/11] 🌩️ We release new nodes, featuring removing image background, photo-quality image generation, and animation super-resolution capabilities.
- [2024/07/10] 🌩️ We release nodes that support Kolors and LLM(large language models). [Kolors](https://siliconflow.github.io/BizyAir/kolors/introduce.html)

BizyAir is a collection of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) nodes that help you overcome environmental and hardware limitations, allowing you to more easily generate high-quality content with ComfyUI.

![](./docs/docs/getting-started/imgs/text2img.gif)

![](./docs/docs/getting-started/imgs/llmnode.gif)

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

Assuming your ComfyUI already has the ComfyUI Manager installed, search for BizyAir as shown in the image below. Click "Install" to complete the installation.
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

https://bizy-air.oss-cn-beijing.aliyuncs.com/new_ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z


## Examples

There are some workflow examples in the [examples](./examples) directory.
