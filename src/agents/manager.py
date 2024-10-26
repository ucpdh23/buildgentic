from agents.base_agent import BaseAgent
from agents.prompt_templates import MANAGER_PROMPT
from agents.toolkit import TOOLS
from registry import register_agent

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI


@register_agent
class ManagerAgent(BaseAgent):

    def __init__(self):
        super.__init__(self, "manager")
        self.isDebugging = True

        self.name = "Manager"
 
        self.tools = TOOLS
        self.prompt = MANAGER_PROMPT
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0
        )

        self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt,
                stop_sequence=self.isDebugging,
        )

        self.agent_executor = AgentExecutor.from_Agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=self.isDebugging,
        )


    def execute(self, message: str):
        response = self.agent_executor.invoke({"input" : message})
        return response
        
