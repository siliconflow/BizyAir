# tests/test_examples.py
import json
import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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


def modify_steps_decorator(func):
    def wrapper(*args, **kwargs):
        json_content = func(*args, **kwargs)

        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content: {e}")

        for node in data["nodes"]:
            if node["type"] == "BizyAir_BasicScheduler":
                if len(node["widgets_values"]) == 3:
                    node["widgets_values"][1] = 1
                else:
                    raise ValueError("BizyAir_BasicScheduler widget_values is wrong")
            if node["type"] == "BizyAir_KSampler":
                if len(node["widgets_values"]) == 7:
                    node["widgets_values"][2] = 1
                else:
                    raise ValueError("BizyAir_KSampler widget_values is wrong")

        modified_json_content = json.dumps(data, indent=2)
        return modified_json_content

    return wrapper


@modify_steps_decorator
def read_workflow_json(filename) -> str:
    _, extension = os.path.splitext(filename)
    if extension.endswith("json"):
        with open(filename, "r", encoding="utf-8") as f:
            c = f.read()
            return c
    else:
        raise NotImplementedError("Only json or png workflow file supported yet")


def load_workflow_graph(driver, workflow: str):
    driver.execute_script(f"window.app.loadGraphData({workflow})")


def click_queue_prompt_button(driver):
    try:
        driver.execute_script(f"window.app.queuePrompt()")
    except Exception as e:
        print(str(e))
        raise Exception("Error: app.queuePrompt() failed.")


def clear_curernt_workflow(driver):
    try:
        driver.execute_script("window.app.graph.clear()")
    except Exception as e:
        print(str(e))
        raise Exception("Error: clear graph failed.")


def wait_until_queue_finished(driver, timeout=100):
    time.sleep(0.3)
    try:
        wait = WebDriverWait(driver, timeout)

        def queue_size_is_zero(driver):
            return driver.execute_script(
                "return window.app.ui.queueSize.textContent === 'Queue size: 0';"
            )

        wait.until(queue_size_is_zero)
    except TimeoutException:
        print("Timeout: Queue prompt not finished.")
        raise
    except Exception as e:
        print(e)
        raise Exception("Error: wait queue finished failed.")


def wait_until_app_ready(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "bizyair-logo"))
    )


def launch_and_wait(driver, *, timeout=100):
    click_queue_prompt_button(driver)
    wait_until_queue_finished(driver, timeout)


def check_graph_node_types(driver):
    try:
        driver.execute_script("window.graph.checkNodeTypes()")
    except Exception as e:
        raise Exception(
            f"Error: Workflow nodes checking failed, likely missing nodes {e=}"
        )


def check_error_occurs(driver):
    elements = driver.find_elements(By.CLASS_NAME, "p-card-content")

    for element in elements:
        if element.text:
            raise Exception(f"Element text: {element.text}")
        else:
            print("Element has no text content")


app_ready = None


def launch_prompt(driver, comfy_host, comfy_port, workflow, timeout):
    BIZYAIR_KEY = os.getenv("BIZYAIR_KEY", "")
    try:
        time.sleep(0.2)
        start_time = time.time()
        global app_ready
        if app_ready is None:
            wait_until_app_ready(driver)
            app_ready = True

        print(" clear the workflow...")
        clear_curernt_workflow(driver)
        print(" workflow cleard")

        print(" load the target workflow...")
        load_workflow_graph(driver, read_workflow_json(workflow))

        print(" check the nodes type of workflow...")
        check_graph_node_types(driver)
        print(f" workflow checked")

        print(f" launch the queue prompt (timeout: {timeout}s)...")
        launch_and_wait(driver, timeout=timeout)

        duration = time.time() - start_time
        print(f" workflow has finished, time elapsed: {duration:.1f}")

        if duration < 1:
            print(
                f" Warning: Execution duration is too short ({duration:.1f}), be careful with your workflow execution"
            )

        print(f" check if error occurs...")
        check_error_occurs(driver)
        print(f" no error occurs when executing workflow")
    except TimeoutException:
        print("Time out")
        driver.quit()
        driver = init_driver()
        driver.get(f"http://{comfy_host}:{comfy_port}")
        driver.add_cookie({"name": "api_key", "value": BIZYAIR_KEY, "path": "/"})
    except Exception as e:
        print(type(e))
        print(e)
        print(" exit with error: 1")
        driver.quit()
        exit(1)


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def flatten_dict(data):
    file_whitelist = {}
    for key, value in data.items():
        if isinstance(value, dict):
            file_whitelist.update(flatten_dict(value))
        else:
            file_whitelist[key] = value
    return file_whitelist


def get_all_examples_json(base_path):
    with open(
        os.path.join(base_path, "..", "bizyair_example_menu.json"),
        "r",
        encoding="utf-8",
    ) as file:
        show_cases_example = json.load(file)
    all_examples = flatten_dict(show_cases_example)
    return all_examples


def filter_examples_json(all_examples_json: dict, bypass_titles: list):
    return {k: v for k, v in all_examples_json.items() if k not in bypass_titles}


if __name__ == "__main__":

    COMFY_HOST = os.getenv("COMFY_HOST", "127.0.0.1")
    COMFY_PORT = os.getenv("COMFY_PORT", "8188")
    BIZYAIR_KEY = os.getenv("BIZYAIR_KEY", "")

    wait_for_comfy_ready(host=COMFY_HOST, port=COMFY_PORT, wait_time_secs=120)

    driver = init_driver()
    driver.get(f"http://{COMFY_HOST}:{COMFY_PORT}")

    # Set BizyAir API Key
    driver.add_cookie({"name": "api_key", "value": BIZYAIR_KEY, "path": "/"})

    base_path = os.path.dirname(os.path.abspath(__file__))
    all_examples_json = get_all_examples_json(base_path)
    all_examples_json = filter_examples_json(
        all_examples_json,
        [
            "All types of ControlNet preprocessors",
            "FLUX-dev Simple Lora",
            "Super Resolution",
        ],
    )
    print("========Running all examples========")
    print("\n".join(f"{key} -- {value}" for key, value in all_examples_json.items()))
    print("====================================")
    for title, file in all_examples_json.items():
        print(f"Running example: {title} - {file}")
        launch_prompt(
            driver,
            COMFY_HOST,
            COMFY_PORT,
            os.path.join(base_path, "..", "examples", file),
            timeout=100,
        )

    driver.quit()
