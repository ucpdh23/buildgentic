from buildgentic.agents.base_agent import BaseAgent, BuildgenticState
from buildgentic.agents.prompt_templates import MANAGER_PROMPT, MANAGER_SYSTEM_PROMPT
from buildgentic.agents.toolkit import FinalAnswer, SearchInADOTool
from buildgentic.agents.utils import create_scratchpad
from buildgentic.registry import register_agent

from langgraph.graph import StateGraph, END
from langchain_core.agents import AgentAction
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


import json
import os
from dotenv import load_dotenv
load_dotenv()



@register_agent
class ManagerAgent(BaseAgent):

    def __init__(self):
        super().__init__("manager", [SearchInADOTool], MANAGER_PROMPT)
        self.isDebugging = True

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", MANAGER_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("assistant", "scratchpad: {scratchpad}"),
        ])

        self.tools = [SearchInADOTool, FinalAnswer]
        self.oracle = (
            {
                "input": lambda x: x['input'],
                "chat_history": lambda x: x['chat_history'],
                "scratchpad": lambda x: create_scratchpad(
                    intermediate_steps=x['intermediate_steps']
                )
            }
            | self.prompt
            | BaseAgent._llm.bind_tools(self.tools)
        )

        workflow = StateGraph(BuildgenticState)
        workflow.add_node("oracle", self.run_oracle)
        for tool in self.tools:
            if tool.__name__ != "FinalAnswer":
                workflow.add_node(tool.__name__, self.run_tool)
        workflow.add_node("FinalAnswer", self.final_answer)
        workflow.set_entry_point("oracle")
        workflow.add_conditional_edges(
            source="oracle",
            path=self.router
        )

        for tool in self.tools:
            if tool.__name__ != "FinalAnswer":
                print(tool.__name__)
                workflow.add_edge(
                    tool.__name__,
                    "oracle"
                )
        
        workflow.add_edge("FinalAnswer", END)

        self.agent_executor = workflow.compile()
    

    def final_answer(self, args: dict):
        print(args)


    def run_oracle(self, state: list):
        out = self.oracle.invoke(state)

        print(out)

        tool_name = out.tool_calls[0]['name']
        tool_args = out.tool_calls[0]['args']

        action_out = AgentAction(tool=tool_name, tool_input=tool_args, log="TBD")

        return {
            "intermediate_steps": [action_out],
        }

    def router(state: list):
        if isinstance(state["intermediate_steps"], list):
            return state["intermediate_steps"][-1].tool
        else:
            print("Routed invalid format")
            return "FinalAnswer"


    def run_tool(self, state: list):
        tool_name = state["intermediate_steps"][-1].tool
        tool_args = state["intermediate_steps"][-1].tool_input

        #invoke the tool. load a class by name
        for clazz in self.tools:
            if clazz.__name__ == tool_name:
                out = getattr(clazz, "invoke")(tool_args)
                break


        return {
            "intermediate_steps": [
                AgentAction(
                    tool=tool_name,
                    tool_input=tool_args,
                    log=str(out)
                )
            ]
        }
    

    def execute(self, message: str):
        json_object = json.loads(message)
        action = json_object['action']

        output = {"action": "none"}
        if action == "registration":
            output = {"action": "nop", "message": "I'm ok"}
        elif action == "execute":
            query = json_object['query']
            out = self.agent_executor.invoke({"input" : query, "chat_history": []})
#            output = out["intermediate_steps"][-1].tool_input
            output = {"action": "executed", "message": out}

        return output
        
