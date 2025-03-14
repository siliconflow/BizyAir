import base64
import io
import json
import os
import sys
from io import BytesIO

import imageio.v2 as imageio
import numpy as np
import requests
import torch
from PIL import Image

# current_dir = os.path.dirname(os.path.abspath(__file__))
# full_path = os.path.abspath(os.path.join(current_dir, "../../.."))
# sys.path.append(full_path)


def convert_image_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def encode_image_to_base64(
    image: Image.Image, format: str = "WEBP", quality: int = 100, **kwargs
) -> str:
    image = convert_image_to_rgb(image)
    with io.BytesIO() as output:
        imageio.imwrite(output, image, format=format, quality=quality)
        output.seek(0)
        img_bytes = output.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


def send_request(create_task_url, payload):
    with TaskClient(create_task_url) as client:
        response = client.pull(payload)

        if response is None:
            raise RuntimeError()
        ret = response.json()

        if "result" in ret:
            msg = json.loads(ret["result"])
        else:
            msg = ret
        # print("why msg: ", msg)
        msg = msg["data"]
        if msg["type"] not in (
            "comfyair",
            "bizyair",
        ):
            raise Exception(f"Unexpected response type: {msg}")

        if "error" in msg:
            raise Exception(f"Error happens: {msg}")

        # img = msg["image"]
        # mask_img = msg["mask_image"]

        # output_file1 = "sam_test.webp"
        # output_file2 = "sam_test_mask.webp"
        # decode_base64_to_image(img, "webp").save(output_file1)
        # decode_base64_to_image(mask_img, "webp").save(output_file2)


class TaskClient:
    def __init__(self, create_task_url):
        self.create_task_url = create_task_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def pull(self, payload):
        response = requests.post(
            self.create_task_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        return response


def test_task_creation_and_result_retrieval():
    create_task_url = "http://0.0.0.0:9899/supernode/sam"
    # create_task_url = "https://bizyair-api.siliconflow.cn/x/v1/supernode/sam"
    image_url = (
        "https://bizy-air.oss-cn-beijing.aliyuncs.com/examples_asset/sam-people.png"
    )

    # image_to_sam = "people.png"
    # img_pil = Image.open(image_to_sam)

    response = requests.get(image_url)
    if response.status_code == 200:
        img_pil = Image.open(BytesIO(response.content))
    else:
        raise Exception(
            f"Failed to retrieve the image, status code: {response.status_code}"
        )

    mode = 2  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes

    ######################使用Point作为Prompt##############################
    input_points = np.array([[500, 375]])
    input_points = json.dumps(input_points.tolist())
    input_label = np.array([1])
    input_label = json.dumps(input_label.tolist())
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
        "params": {
            "input_points": input_points,
            "input_label": input_label,
            "input_boxes": None,
        },
    }

    send_request(create_task_url, payload)

    # ###################使用Box作为Prompt##############################
    input_boxes = np.array([451.8652, 71.6301, 648.0280, 1022.0955])
    input_boxes = json.dumps(input_boxes.tolist())
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
        "params": {
            "input_points": None,
            "input_label": None,
            "input_boxes": input_boxes,
        },
    }

    send_request(create_task_url, payload)

    # ######################使用Points和Box作为Prompt##############################
    input_boxes = np.array([451.8652, 71.6301, 648.0280, 1022.0955])
    input_boxes = json.dumps(input_boxes.tolist())

    input_points = np.array([[575, 750]])
    input_points = json.dumps(input_points.tolist())
    input_label = np.array([0])
    input_label = json.dumps(input_label.tolist())
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
        "params": {
            "input_points": input_points,
            "input_label": input_label,
            "input_boxes": input_boxes,
        },
    }

    send_request(create_task_url, payload)

    # #####################使用Batched Box作为Prompt##############################
    input_boxes = torch.tensor(
        [
            [24.0652, 127.0906, 181.5945, 932.2192],
            [451.8652, 71.6301, 648.0280, 1022.0955],
            [731.7250, 201.1820, 956.5409, 1022.2478],
            [236.7201, 131.5688, 414.6645, 979.8284],
            [145.1680, 183.1925, 308.3481, 955.5884],
            [358.4024, 192.8287, 506.4283, 1011.5869],
            [588.2826, 152.5342, 798.1860, 1021.6285],
        ]
    )
    input_boxes = json.dumps(input_boxes.tolist())
    mode = 3
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
        "params": {
            "input_boxes": input_boxes,
        },
    }

    send_request(create_task_url, payload)

    # ####################使用自动模式作为Prompt##############################
    mode = 0
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
    }
    send_request(create_task_url, payload)

    ######################使用text模式作为Prompt##############################
    text = "human"
    box_threshold = 0.3
    text_threshold = 0.25
    mode = 1
    payload = {
        "image": encode_image_to_base64(img_pil),
        "mode": mode,  # 0: auto mode  1:text mode 2: points/boxes 3: batched boxes
        "params": {
            "prompt": text,
            "box_threshold": box_threshold,  # 检测框置信度
            "text_threshold": text_threshold,  # 文本置信度
        },
    }

    send_request(create_task_url, payload)


if __name__ == "__main__":
    test_task_creation_and_result_retrieval()
