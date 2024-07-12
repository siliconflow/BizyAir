import requests


class DiffusersServerClient:
    def __init__(self, create_task_url, get_result_url):
        self.create_task_url = create_task_url
        self.get_result_url = get_result_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def create_task(self, payload):
        response = requests.post(
            self.create_task_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            print(f"Failed to create task: {response.status_code}")
            return None
        task_id = response.json()["task_id"]
        tasks_in_queue = response.json().get("tasks_in_queue", "N/A")
        print(f"Tasks in queue: {tasks_in_queue}")
        return task_id

    def get_task_result(self, task_id):
        result_url = self.get_result_url.format(task_id=task_id)
        response = requests.get(result_url)
        if response.status_code != 200:
            print(f"Failed to get task result: {response.status_code}")
            return None
        return response.json()
