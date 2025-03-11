from abc import ABC, abstractmethod
from typing import Any, Dict


class Command(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")


class Processor(ABC):
    @abstractmethod
    def process(
        self,
        url: str,
        prompt,
    ) -> Any:
        pass

    @abstractmethod
    def validate_input(self, input: Any) -> bool:
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if not self.validate_input(*args, **kwds):
            raise ValueError(f"Invalid input {args=} {kwds=}")
        return self.process(*args, **kwds)
