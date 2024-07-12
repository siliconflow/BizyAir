# Kolors

Kolors is a large-scale text-to-image generation model based on latent diffusion, developed by the Kuaishou Kolors team.

You can find more about Kolors at [Kwai-Kolors/Kolors](https://huggingface.co/Kwai-Kolors/Kolors).

BizyAir offers 5 nodes related to Kolors, each serving for:

- Kolors Sampler
- Text encoding
- VAE decoding
- VAE encoding

Here is an example of a text-to-image workflow using Kolors:

![](./imgs/bizyair_kolors_txt2img.png)

Here is an example of a image-to-image workflow using Kolors:

![](./imgs/bizyair_kolors_img2img.png)


 The nodes provided by BizyAir are compatible with the nodes provided by [ComfyUI-KwaiKolorsWrapper](https://github.com/kijai/ComfyUI-KwaiKolorsWrapper) , allowing you to freely combine them.
 
 Enjoy.
