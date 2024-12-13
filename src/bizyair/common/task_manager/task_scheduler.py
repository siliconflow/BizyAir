from threading import Lock

from .task_base import TaskRunnerBase, TaskSchedulerBase


class TaskScheduler(TaskSchedulerBase):
    def __init__(self) -> None:
        super().__init__()
        self.task_contexts = {}
        self._lock = Lock()

    def add_task(self, task_id: str, task_runner: TaskRunnerBase):
        with self._lock:
            self.task_contexts[task_id] = task_runner

    def schedule(self, task_id: str):
        self.task_contexts[task_id].execute()
