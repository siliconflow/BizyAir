# tests/test_examples.py

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMFY_HOST = os.getenv("COMFY_HOST", "127.0.0.1")
COMFY_PORT = os.getenv("COMFY_PORT", "8188")
BIZYAIR_KEY = os.getenv("BIZYAIR_KEY", "")

base_path = os.path.dirname(os.path.abspath(__file__))
print(f"Test base path: {base_path}")
from comfy.model_management import get_torch_device


def _get_torch_device():
    return "cpu"


get_torch_device = _get_torch_device


def test_comfyui():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"http://{COMFY_HOST}:{COMFY_PORT}")

    # Wait for the page to load
    time.sleep(5)

    # Add a cookie
    driver.add_cookie({"name": "api_key", "value": BIZYAIR_KEY, "path": "/"})

    driver.quit()
