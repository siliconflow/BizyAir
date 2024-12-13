from .task_base import TaskRunnerBase, TaskContextBase

class BizyAirTaskRunner(TaskRunnerBase):
    def __init__(self, task_context: TaskContextBase):
        self.task_context = task_context

    def execute(self, task_id: str):
        pass
