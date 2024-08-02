# Install BizyAir

BizyAir is a set of ComfyUI nodes that allows you to skip the time-consuming process of downloading models and setting up requirements, enabling you to run ComfyUI workflows directly without being constrained by environmental limitations.

You can choose any of the following methods to install BizyAir

### Method 1: Install via ComfyUI Manager

Assuming your ComfyUI already has the ComfyUI Manager installed, search for BizyAir as shown in the image below. Click "Install" to complete the installation.
![ComfyUI_Manager_BizyAir_Search_Screenshot](./imgs/ComfyUI_Manager_BizyAir_Search_Screenshot.png)


### Method 2: Install via git clone

You can install BizyAir by downloading the BizyAir repository to the custom_nodes subdirectory of ComfyUI by using git clone.

```bash
cd /path/to/ComfyUI/custom_nodes && \
git clone https://github.com/siliconflow/BizyAir.git
```

Then, restart ComfyUI.

## Method 3: Install via Comfy CLI

- Prerequisites
    - Ensure `pip install comfy-cli` is installed.
    - Installing ComfyUI `comfy install`

To install the `BizyAir`, use the following command:

```shell
comfy node install bizyair
```


## Method 4: Download windows portable ComfyUI

For NA/EU users:

https://github.com/siliconflow/ComfyUI/releases/tag/latest

For CN users:

https://bizy-air.oss-cn-beijing.aliyuncs.com/new_ComfyUI_windows_portable_nvidia_none_or_cpu.7z
