from buildgentic.agents.base_agent import BaseAgent, BuildgenticState
from buildgentic.agents.prompt_templates import CHATBOT_SYSTEM_PROMPT
from buildgentic.agents.toolkit import FinalAnswer
from buildgentic.agents.utils import create_scratchpad
from buildgentic.mqtt_client import MqttClient
from buildgentic.registry import register_agent

from langgraph.graph import StateGraph, END
from langchain_core.agents import AgentAction
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_litellm import ChatLiteLLM

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent

import json
import os
from dotenv import load_dotenv
load_dotenv()


@register_agent
class ChatbotAgent:
    async def build():
        """Builds the Chatbot agent."""

        print("building chatbot agent tools...")
        tools = await ChatbotAgent._resolveTools()
        print("resolved tools: ", tools)

        return ChatbotAgent(tools)

    def __init__(self, tools):
        self.name = "chatbot"
        self.tools = tools

        #http_client = httpx.Client(verify=False)

        llm = ChatOpenAI(
            api_key=os.getenv("CURRENT_API_KEY")
        )


        self.agent = create_react_agent(
            model=llm,
            tools=self.tools,

        )

    
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

    def evaluate(self, topic):
        print("evaluating topic: ", topic, topic.endswith(self.name))
        # Check if the topic is related to the chatbot
        return topic.endswith(self.name)
    
    def execute(self, message):
        json_object = json.loads(message)
        action = json_object['action']
        print("received action: ", action)

        output = {"action": "none"}
        if action == "registration":
            output = {"action": "nop", "message": "I'm ok"}
        elif action == "execute":
            query = json_object['query']
            out = self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )
            output = {"action": "executed", "message": str(out)}

        return output



    async def _resolveTools():
        mcpClient = MultiServerMCPClient(
            {
                "servant": {
                    "url" : os.getenv("SERVANT_MCP_URL"),
                    "transport" : "sse"
                }
            }
        )

        tools = await mcpClient.get_tools()
        output = [tool for tool in tools]
        output.append(FinalAnswer)

        return output
