from abc import ABC, abstractmethod

class BaseAgent(ABC):

    def __init__(self, base_topic: str) -> None:
        super().__init__()
        self.base_topic = base_topic


    def evaluate(self, topic: str) -> bool:
        """Evaluates if the agent should respond to the message."""
        return topic.startswith(self.base_topic)
        

    @abstractmethod
    def execute(self, message: str):
        """Executes the agent's task if evaluation returns true."""
        pass
