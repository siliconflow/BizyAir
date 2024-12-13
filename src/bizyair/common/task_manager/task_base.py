from abc import ABC, abstractmethod


class TaskStateStorageBase(ABC):
    @abstractmethod
    def save_task_context(self, task_id, context: TaskContextBase):
        pass
    
    @abstractmethod
    def load_task_context(self, task_id):
        pass
    
    @abstractmethod
    def delete_task_context(self, task_id):
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


class TaskContextBase(ABC):
    
    @abstractmethod
    def set_storage(self, storage: TaskStateStorageBase):
        pass
    @abstractmethod
    def update_context(self, context: dict):
        pass


class TaskRunnerBase(ABC):
    @abstractmethod
    def load_context(self, context: TaskContextBase):
        self.context = context

    @abstractmethod
    def execute(self):
        pass
        # if self.context is None:
        #     raise ValueError("Context is not loaded, please call load_context first")
        
        # # self.context.update_context(state="running", registers={"PC": 200, "SP": 300}, memory={"data": [7, 8, 9]})
        # task_data = self.context.task_data
        # # 执行任务
        # self.context.save_context()
