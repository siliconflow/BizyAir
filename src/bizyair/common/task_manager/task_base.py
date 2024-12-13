from abc import ABC, abstractmethod


class TaskContextBase(ABC):
    @abstractmethod
    def save_context(self):
        pass

    @abstractmethod
    def get_context(self):
        pass


class TaskRunnerBase(ABC):
    @abstractmethod
    def load_context(self, context: TaskContextBase):
        self.context = context

    @abstractmethod
    def execute(self):
        pass


class TaskStateStorageBase(ABC):
    @abstractmethod
    def save_task_context(self, task_id, context: TaskContextBase):
        pass

    @abstractmethod
    def load_task_context(self, task_id):
        pass


class TaskSchedulerBase(ABC):
    @abstractmethod
    def schedule(self, task_id: str):
        pass

    @abstractmethod
    def add_task(self, task_id: str, task_data: dict, task_runner: TaskRunnerBase):
        pass


class TaskManagerBase(ABC):
    @abstractmethod
    def create_task(self, task_id: str, task_data: dict, task_runner: TaskRunnerBase):
        pass

    @abstractmethod
    def start_task(self, task_id: str):
        pass

    @abstractmethod
    def stop_task(self, task_id: str):
        pass

    @abstractmethod
    def delete_task(self, task_id: str):
        pass
