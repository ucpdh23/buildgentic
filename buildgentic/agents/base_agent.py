from abc import ABC, abstractmethod
import json
import operator
from typing import Annotated, TypedDict

from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import BaseMessage
from langchain_core.agents  import AgentAction

from buildgentic.mqtt_client import MqttClient

import os
from dotenv import load_dotenv
load_dotenv()

LITELLM_BASE_URL=os.getenv("LITELLM_BASE_URL")
LITELLM_APIKEY=os.getenv("LITELLM_APIKEY")
LITELLM_MODEL=os.getenv("LITELLM_MODEL_2")

os.environ["LITELLM_BASE_URL"] = LITELLM_BASE_URL
os.environ["LITELLM_APIKEY"] = LITELLM_APIKEY
os.environ["OPENAI_API_KEY"] = LITELLM_APIKEY
os.environ["LITELLM_PROXY_API_KEY"] = LITELLM_APIKEY
os.environ["LITELLM_MODEL"] = LITELLM_MODEL


class BaseAgent(ABC):
    """Base class for all agents."""

    _first_time_executed = False
    _llm = None

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self._execute_first_time()
        

    @staticmethod
    def _execute_first_time():
        if not BaseAgent._first_time_executed:
            print(LITELLM_MODEL)
            # init the langgraph llm model connector
            BaseAgent._llm = ChatLiteLLM(
                api_base=LITELLM_BASE_URL,
                openai_api_key=LITELLM_APIKEY,
                temperature=0,
                max_tokens=1000,
                model=LITELLM_MODEL)

            # Place the code to be executed only once here
            print("Executing for the first time")
            BaseAgent._first_time_executed = True

    def registerInSevant(self, mqtt_client : MqttClient):
        self.mqtt_client = mqtt_client
        payload = {
            'action': "register",
            'message': "agent is ready to work",
            'data': {
                'name': self.name
            }
        }
        mqtt_client.publish_msg(payload)

    def evaluate(self, topic: str) -> bool:
        """Evaluates if the agent should respond to the message."""
        return topic.endswith(self.name)
        

    @abstractmethod
    def execute(self, message: str):
        """Executes the agent's task if evaluation returns true."""
        print(message)
        pass


class BuildgenticState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]