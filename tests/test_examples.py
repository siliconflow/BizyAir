# tests/test_examples.py
import json
import os
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
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


def read_workflow_json(filename) -> str:
    _, extension = os.path.splitext(filename)
    if extension.endswith("json"):
        with open(filename, "r") as f:
            c = f.read()
            return c
    else:
        raise NotImplementedError("Only json or png workflow file supported yet")


def load_workflow_graph(driver, workflow: str):
    driver.execute_script(f"window.app.loadGraphData({workflow})")


def click_queue_prompt_button(driver):
    wait = WebDriverWait(driver, 1)
    queue_button = wait.until(EC.presence_of_element_located((By.ID, "queue-button")))
    queue_button.click()


def clear_curernt_workflow(driver):
    driver.execute_script("window.app.graph.clear()")


def wait_until_queue_finished(driver, timeout=100):
    time.sleep(0.3)
    wait = WebDriverWait(driver, timeout)
    element = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f'//*[contains(text(), "Queue size: 0")]')
        )
    )


def wait_until_app_ready(driver):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "comfy-clear-button"))
    )
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "graph-canvas"))
    )


def launch_and_wait(driver, *, timeout=100):
    click_queue_prompt_button(driver)
    wait_until_queue_finished(driver, timeout)


def check_graph_node_types(driver):
    try:
        driver.execute_script("window.graph.checkNodeTypes()")
    except Exception as e:
        raise Exception("Error: Workflow nodes checking failed, likely missing nodes")


def check_error_occurs(driver):
    elements = driver.find_elements(By.CLASS_NAME, "comfy-modal-content")

    desired_element = None
    for element in elements:
        element_text = element.text
        if "Error occurred when" in element_text:
            print(element.text)
            raise Exception(f"{element.text}")


def launch_prompt(driver, comfy_host, comfy_port, workflow, timeout):
    try:
        print(f"connect to ComfyUI: {comfy_host}:{comfy_port}...")
        driver.get(f"http://{comfy_host}:{comfy_port}")
        print(f"ComfyUI connected")
        time.sleep(0.1)
        start_time = time.time()

        wait_until_app_ready(driver)

        print("clear the workflow...")
        clear_curernt_workflow(driver)
        print("workflow cleard")

        print("load the target workflow...")
        load_workflow_graph(driver, read_workflow_json(workflow))
        print(f"{workflow} loaded")

        print("check the nodes type of workflow...")
        check_graph_node_types(driver)
        print(f"{workflow} workflow checked")

        print(f"launch the queue prompt (timeout: {timeout}s) ...")
        launch_and_wait(driver, timeout=timeout)

        duration = time.time() - start_time
        print(f"{workflow} has finished, time elapsed: {duration:.1f}")

        if duration < 2:
            raise ValueError(
                "Execution duration is too short, possible error in workflow execution"
            )

        print(f"check if error occurs...")
        check_error_occurs(driver)
        print(f"no error occurs when executing workflow")
    except TimeoutException:
        print("Time out")
        exit(1)
    except Exception as e:
        print(type(e))
        print(e)
        print("exit with error: 1")
        exit(1)
    finally:
        driver.quit()


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


def get_all_examplse_json(base_path):
    with open(os.path.join(base_path, "..", "bizyair_example_menu.json"), "r") as file:
        show_cases_example = json.load(file)
    all_examples = flatten_dict(show_cases_example)
    return all_examples


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
    all_examples_json = get_all_examplse_json(base_path)
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
