# tests/test_examples.py

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def wait_for_comfy_ready(host="127.0.0.1", port=8188, wait_time_secs=120):
    url = f"http://{host}:{port}/system_stats"
    wait_secs = wait_time_secs

    while wait_secs > 0:
        print(f"Waiting for ComfyUI server ready at {url}, {wait_secs}s left ...")
        time.sleep(1)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass

        wait_secs -= 1

    print(f"Timeout {wait_time_secs} secs. ComfyUI Server not ready.")
    exit(1)


if __name__ == "__main__":

    COMFY_HOST = os.getenv("COMFY_HOST", "127.0.0.1")
    COMFY_PORT = os.getenv("COMFY_PORT", "8188")
    BIZYAIR_KEY = os.getenv("BIZYAIR_KEY", "")

    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Test base path: {base_path}")

    wait_for_comfy_ready(host=COMFY_HOST, port=COMFY_PORT, wait_time_secs=120)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"http://{COMFY_HOST}:{COMFY_PORT}")

    # Add a cookie
    driver.add_cookie({"name": "api_key", "value": BIZYAIR_KEY, "path": "/"})

    driver.quit()
