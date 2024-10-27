from abc import ABC, abstractmethod
import json

from buildgentic.mqtt_client import MqttClient



class BaseAgent(ABC):

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def registerInSevant(self, mqtt_client : MqttClient):
        payload = {
            'action': "register",
            'message': "agent is ready to work",
            'data': {
                'name': self.name
            }
        }

        mqtt_client.publish_msg(json.dumps(payload))

    def evaluate(self, topic: str) -> bool:
        """Evaluates if the agent should respond to the message."""
        return topic.startswith(self.base_topic)
        

    @abstractmethod
    def execute(self, message: str):
        """Executes the agent's task if evaluation returns true."""
        pass
