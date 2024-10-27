from buildgentic.agents.base_agent import BaseAgent
from buildgentic.agents.prompt_templates import MANAGER_PROMPT
from buildgentic.agents.toolkit import TOOLS
from buildgentic.registry import register_agent


import os
from dotenv import load_dotenv


from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

load_dotenv()


OPENAI_URL=os.getenv("OPENAI_URL")
OPENAI_APIKEY=os.getenv("OPENAI_APIKEY")


@register_agent
class ManagerAgent(BaseAgent):

    def __init__(self):
        super().__init__("manager")
        self.isDebugging = True

        self.tools = TOOLS
        self.prompt = MANAGER_PROMPT

        self.llm = ChatOpenAI(
            base_url=OPENAI_URL,
            api_key=OPENAI_APIKEY,
            temperature=0
        )

        self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt,
                stop_sequence=self.isDebugging,
        )

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=self.isDebugging,
        )


    def execute(self, message: str):
        response = self.agent_executor.invoke({"input" : message})
        return response
        
