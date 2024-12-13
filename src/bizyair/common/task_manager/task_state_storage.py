import json
import os
from threading import Lock

from bizyair.common.task_manager.task_base import TaskContextBase, TaskStateStorageBase


class TaskStateStorage(TaskStateStorageBase):

    def __init__(self):
        self.storage_directory = "task_storage"
        self._lock = Lock()
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def _get_file_path(self, task_id):
        return os.path.join(self.storage_directory, f"{task_id}.json")

    def save_task_context(self, task_id, context: TaskContextBase):
        file_path = self._get_file_path(task_id)
        with self._lock:
            with open(file_path, "w") as file:
                json.dump(context.__dict__, file, default=str, indent=4)

    def load_task_context(self, task_id):
        file_path = self._get_file_path(task_id)
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    def list_tasks(self):
        return os.listdir(self.storage_directory)

    def delete_task(self, task_id):
        file_path = self._get_file_path(task_id)
        if os.path.exists(file_path):
            os.remove(file_path)
