from .task_base import (
    TaskManagerBase,
    TaskRunnerBase,
    TaskSchedulerBase,
    TaskStateStorageBase,
)
from .task_context import TaskContext


class TaskManager(TaskManagerBase):
    """TaskManager is a class that manages the tasks.


    example:

    task_manager = TaskManager(state_storage, scheduler)
    task_manager.create_task("task_id", {"task_data": "task_data"})
    task_manager.start_task("task_id")
    """

    def __init__(
        self, state_storage: TaskStateStorageBase, scheduler: TaskSchedulerBase
    ):
        self.state_storage = state_storage
        self.scheduler = scheduler

    def create_task(
        self, task_id: str, task_data: dict, *, task_runner: TaskRunnerBase = None
    ) -> str:
        context = TaskContext(task_id, task_data, self.state_storage)
        if task_runner:
            task_runner.load_context(context)
        else:
            assert False, "task_runner is required"
        self.scheduler.add_task(task_id, task_runner)

    def start_task(self, task_id):
        """启动任务"""
        context = self.state_storage.load_task_context(task_id)
        if context:
            self.scheduler.schedule(task_id)
            print(f"Task {task_id} started.")
        else:
            print(f"Task {task_id} not found.")
