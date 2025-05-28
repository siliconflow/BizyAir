import argparse
import json
import os
import uuid
import requests
import websocket

os.environ["BIZYAIR_SERVER_MODE"] = "True"
BIZYAIR_DOMAIN = os.getenv("BIZYAIR_DOMAIN", "https://api.bizyair.cn")
BIZYAIR_KEY = os.getenv("BIZYAIR_KEY", "")
COMFY_HOST = os.getenv("COMFY_HOST", "127.0.0.1")
COMFY_PORT = os.getenv("COMFY_PORT", "8188")
BIZYAIR_TEST_SKIP_WORKFLOW_IDS = str.split(
    os.getenv("BIZYAIR_TEST_SKIP_WORKFLOW_IDS", ""), ","
)
BIZYAIR_OFFICIAL_WORKFLOW_MAX_TOTAL = int(
    os.getenv("BIZYAIR_OFFICIAL_WORKFLOW_MAX_TOTAL", "100")
)
CLIENT_ID = str(uuid.uuid4())


def load_workflow_from_file(file_path):
    """从JSON文件加载工作流"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Workflow file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")


def queue_prompt(comfy_host, comfy_port, prompt, timeout):
    base_url = f"{comfy_host}:{comfy_port}"

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(base_url, CLIENT_ID))
    ws.settimeout(60 * 10)

    p = {"prompt": prompt, "client_id": CLIENT_ID}
    response = requests.post(f"http://{base_url}/prompt", json=p)
    prompt_id = response.json()["prompt_id"]
    while True:
        out = ws.recv()
        print(out)
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "execution_error":
                print(message["data"])
                raise Exception(f"Error from ComfyUI")
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None:
                    if data["prompt_id"] != prompt_id:
                        print(
                            f"Warning: unmatched prompt_id: {data['prompt_id']} vs {prompt_id}"
                        )
                    break  # Execution is done
        else:
            continue  # previews are binary data
    ws.close()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run ComfyUI workflow")
    parser.add_argument(
        "-w",
        "--workflow",
        type=str,
        required=True,
        help="Path to the workflow JSON file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    prompt = load_workflow_from_file(args.workflow)
    param_node = {
        "inputs": {},
        "class_type": "BizyAir_PassParameter",
        "_meta": {
            "title": "☁️BizyAir PassParameter",
            "api_key": BIZYAIR_KEY,
            "prompt_id": "a-unique-prompt-id",
        },
    }
    prompt["bizyair_magic_node"] = param_node
    queue_prompt(
        comfy_host=COMFY_HOST, comfy_port=COMFY_PORT, prompt=prompt, timeout=3600
    )
