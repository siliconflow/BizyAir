
from bizyair.common.task_manager.task_base import TaskStateStorageBase, TaskContextBase
import os
import json
from threading import Lock

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
            with open(file_path, 'w') as file:
                json.dump(context.__dict__, file, default=str, indent=4)

    def load_task_context(self, task_id):
        file_path = self._get_file_path(task_id)
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None