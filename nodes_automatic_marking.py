import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
import os

from PIL import Image, ImageOps

import folder_paths

# from .llm import BizyAirJoyCaption2
from .nodes_automatic_marking_utils import joycaption2

class BizyAirMultiJoyCaption2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "do_sample": ([True, False],),
                "temperature": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.01,
                        "round": 0.001,
                        "display": "number",
                    },
                ),
                "max_tokens": (
                    "INT",
                    {
                        "default": 256,
                        "min": 16,
                        "max": 512,
                        "step": 16,
                        "display": "number",
                    },
                ),
                "caption_type": (
                    [
                        "Descriptive",
                        "Descriptive (Informal)",
                        "Training Prompt",
                        "MidJourney",
                        "Booru tag list",
                        "Booru-like tag list",
                        "Art Critic",
                        "Product Listing",
                        "Social Media Post",
                    ],
                ),
                "caption_length": (
                    ["any", "very short", "short", "medium-length", "long", "very long"]
                    + [str(i) for i in range(20, 261, 10)],
                ),
                "extra_options": (
                    "STRING",
                    {
                        "default": "If there is a person/character in the image you must refer to them as {name}.",
                        "tooltip": "Extra options for the model",
                        "multiline": True,
                    },
                ),
                "name_input": (
                    "STRING",
                    {
                        "default": "Jack",
                        "tooltip": "Name input is only used if an Extra Option is selected that requires it.",
                    },
                ),
                "custom_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "multi_joycaption"
    NODE_DISPLAY_NAME = "☁️BizyAir Multi Joy Caption"

    def multi_joycaption(self, image, **kwargs):
        captions = []
        input_images = [img for img in image]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda img: joycaption2(image=img.unsqueeze(0), **kwargs), input_images))

        for i, result in enumerate(results):
            captions.append(result[0])
            # pbar.update_absolute(i + 1)
        combined_caption = " | ".join(captions)
        
        return {"ui": {"text": (combined_caption,)}, "result": (combined_caption,)}


class SaveCaptionsAndImages:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "captions": ("STRING", {"multiline": True}),
                "images": ("IMAGE",),
                "directory_prefix": (
                    "STRING",
                    {"default": "lora_dataset", "multiline": False},
                ),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "apply"

    def apply(self, captions, images, directory_prefix):

        # Split the captions string into a list using " | " as the delimiter
        caption_list = captions.split(" | ")
        full_output_folder = folder_paths.get_output_directory()
        # Find the next available directory number
        i = 0
        while True:
            dir_path = os.path.join(full_output_folder, f"{directory_prefix}_{i:03d}")
            if not os.path.exists(dir_path):
                break
            i += 1
        # Validate input
        if len(caption_list) != len(images):
            raise ValueError(
                "The number of captions does not match the number of images."
            )

        for batch_number, (image, caption) in enumerate(zip(images, caption_list)):
            # Generate a unique filename for each image
            filename = f"image_{batch_number:04d}"

            # Generate file paths
            image_filepath = os.path.join(dir_path, f"{filename}.png")
            caption_filepath = os.path.join(dir_path, f"{filename}.txt")

            # Ensure directory exists
            os.makedirs(dir_path, exist_ok=True)

            # Save the image
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img.save(image_filepath)

            # Write caption to file
            with open(caption_filepath, "w", encoding="utf-8") as caption_file:
                caption_file.write(caption)

            print(f"Image saved to: {image_filepath}")
            print(f"Caption saved to: {caption_filepath}")

        return {}

class BizyAirLoadImagesFromFolder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 1024, "min": 64, "step": 1}),
                "height": ("INT", {"default": 1024, "min": 64, "step": 1}),
                "keep_aspect_ratio": (["crop", "pad", "stretch",],), 
            },
            "optional": {
                "image_load_cap": ("INT", {"default": 0, "min": 0, "step": 1}),
                "start_index": ("INT", {"default": 0, "min": 0, "step": 1}),
                "include_subfolders": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "STRING",)
    RETURN_NAMES = ("image", "mask", "count", "image_path",)
    FUNCTION = "load_images"
    CATEGORY = "☁️BizyAir/marking"
    DESCRIPTION = """Loads images from a folder into a batch, images are resized and loaded into a batch."""

    def load_images(self, folder, width, height, image_load_cap, start_index, keep_aspect_ratio, include_subfolders=False):
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Folder '{folder} cannot be found.'")
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_paths = []
        if include_subfolders:
            for root, _, files in os.walk(folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in valid_extensions):
                        image_paths.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder):
                if any(file.lower().endswith(ext) for ext in valid_extensions):
                    image_paths.append(os.path.join(folder, file))

        dir_files = sorted(image_paths)

        if len(dir_files) == 0:
            raise FileNotFoundError(f"No files in directory '{folder}'.")

        # start at start_index
        dir_files = dir_files[start_index:]

        images = []
        masks = []
        image_path_list = []

        limit_images = False
        if image_load_cap > 0:
            limit_images = True
        image_count = 0

        for image_path in dir_files:
            if os.path.isdir(image_path):
                continue
            if limit_images and image_count >= image_load_cap:
                break
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            
            # Resize image to maximum dimensions
            if i.size != (width, height):
                i = self.resize_with_aspect_ratio(i, width, height, keep_aspect_ratio)
            
            
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
                if mask.shape != (height, width):
                    mask = torch.nn.functional.interpolate(mask.unsqueeze(0).unsqueeze(0), 
                                                         size=(height, width), 
                                                         mode='bilinear', 
                                                         align_corners=False).squeeze()
            else:
                mask = torch.zeros((height, width), dtype=torch.float32, device="cpu")
            
            images.append(image)
            masks.append(mask)
            image_path_list.append(image_path)
            image_count += 1

        if len(images) == 1:
            return (images[0], masks[0], 1, image_path_list)
        
        elif len(images) > 1:
            image1 = images[0]
            mask1 = masks[0].unsqueeze(0)

            for image2 in images[1:]:
                image1 = torch.cat((image1, image2), dim=0)

            for mask2 in masks[1:]:
                mask1 = torch.cat((mask1, mask2.unsqueeze(0)), dim=0)

            return (image1, mask1, len(images), image_path_list)
    def resize_with_aspect_ratio(self, img, width, height, mode):
        if mode == "stretch":
            return img.resize((width, height), Image.Resampling.LANCZOS)
        
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        target_ratio = width / height

        if mode == "crop":
            # Calculate dimensions for center crop
            if aspect_ratio > target_ratio:
                # Image is wider - crop width
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.Resampling.LANCZOS)
                left = (new_width - width) // 2
                return img.crop((left, 0, left + width, height))
            else:
                # Image is taller - crop height
                new_height = int(width / aspect_ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
                top = (new_height - height) // 2
                return img.crop((0, top, width, top + height))

        elif mode == "pad":
            pad_color = self.get_edge_color(img)
            # Calculate dimensions for padding
            if aspect_ratio > target_ratio:
                # Image is wider - pad height
                new_height = int(width / aspect_ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
                padding = (height - new_height) // 2
                padded = Image.new('RGBA', (width, height), pad_color)
                padded.paste(img, (0, padding))
                return padded
            else:
                # Image is taller - pad width
                new_width = int(height * aspect_ratio)
                img = img.resize((new_width, height), Image.Resampling.LANCZOS)
                padding = (width - new_width) // 2
                padded = Image.new('RGBA', (width, height), pad_color)
                padded.paste(img, (padding, 0))
                return padded
    def get_edge_color(self, img):
        from PIL import ImageStat
        """Sample edges and return dominant color"""
        width, height = img.size
        img = img.convert('RGBA')
        
        # Create 1-pixel high/wide images from edges
        top = img.crop((0, 0, width, 1))
        bottom = img.crop((0, height-1, width, height))
        left = img.crop((0, 0, 1, height))
        right = img.crop((width-1, 0, width, height))
        
        # Combine edges into single image
        edges = Image.new('RGBA', (width*2 + height*2, 1))
        edges.paste(top, (0, 0))
        edges.paste(bottom, (width, 0))
        edges.paste(left.resize((height, 1)), (width*2, 0))
        edges.paste(right.resize((height, 1)), (width*2 + height, 0))
        
        # Get median color
        stat = ImageStat.Stat(edges)
        median = tuple(map(int, stat.median))
        return median


NODE_CLASS_MAPPINGS = {
    "BizyAirLoadImagesFromFolder": BizyAirLoadImagesFromFolder,
    "BizyAirMultiJoyCaption2": BizyAirMultiJoyCaption2,
    "SaveCaptionsAndImages": SaveCaptionsAndImages,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "BizyAirLoadImagesFromFolder": "☁️BizyAir LoadImagesFromFolder",
    "BizyAirMultiJoyCaption2": "☁️BizyAir Multi Joy Caption2",
    "SaveCaptionsAndImages": "☁️BizyAir Save Captions And Images",
}
