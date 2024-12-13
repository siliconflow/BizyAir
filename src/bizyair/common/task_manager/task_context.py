from datetime import datetime

from .task_base import TaskContextBase, TaskRunnerBase, TaskStateStorageBase


class TaskContext(TaskContextBase):
    def __init__(self, task_id: str, task_data: any, storage: TaskStateStorageBase):
        """TaskContext is the context of the bizyair task
        parameters:
            task_id: the id of the task
            task_data: the data that the task needs to process
            storage: the storage of the task
        """
        self.task_id = task_id
        self.task_data = (
            task_data  # task_data is the data that the task needs to process
        )
        self.created_at = datetime.now()
        self.storage = storage

    def save_context(self):
        self.storage.save_task_context(self.task_id, self)

    def get_context(self):
        return self.storage.load_task_context(self.task_id)
