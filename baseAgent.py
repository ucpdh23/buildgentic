from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def evaluate(self, message: str) -> bool:
        """Evaluates if the agent should respond to the message."""
        pass

    @abstractmethod
    def execute(self, message: str):
        """Executes the agent's task if evaluation returns true."""
        pass
