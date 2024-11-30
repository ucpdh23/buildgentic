from buildgentic.agents.base_agent import BaseAgent, BuildgenticState
from buildgentic.agents.prompt_templates import DEVELOPER_SYSTEM_PROMPT, MANAGER_PROMPT, MANAGER_SYSTEM_PROMPT
from buildgentic.agents.toolkit import AddCommentToADOWorkItemFinalAnswer, CreateSubtasksToADOWorkItemFinalAnswer, DeveloperFinalAnswer, FinalAnswer, RequestADOWorkItemReassignmentFinalAnswer, SearchInADOTool, SourceCodeAnalyzerTool, UpdateDescriptionToADOWorkItemFinalAnswer
from buildgentic.agents.utils import create_scratchpad
from buildgentic.registry import register_agent

from langgraph.graph import StateGraph, END
from langchain_core.agents import AgentAction
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


import json
import os
from dotenv import load_dotenv
load_dotenv()



#@register_agent
class DeveloperAgent(BaseAgent):

    def __init__(self):
        super().__init__("manager", [SearchInADOTool], MANAGER_PROMPT)
        self.isDebugging = True

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", DEVELOPER_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("assistant", "scratchpad: {scratchpad}"),
        ])



        self.tools = [SourceCodeAnalyzerTool, DeveloperFinalAnswer]
        
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
            if not tool.__name__.endswith("FinalAnswer"):
                workflow.add_node(tool.__name__, self.run_tool)
            else:
                workflow.add_node(tool.__name__, self.final_answer)

        workflow.set_entry_point("oracle")
        workflow.add_conditional_edges(
            source="oracle",
            path=self.router
        )

        for tool in self.tools:
            if not tool.__name__.endswith("FinalAnswer"):
                print(tool.__name__)
                workflow.add_edge(
                    tool.__name__,
                    "oracle"
                )
            else:
                workflow.add_edge(tool.__name__, END)

        self.agent_executor = workflow.compile()
    

    def final_answer(self, args: dict):
        return print(args)


    def run_oracle(self, state: list):
        print("running oracle...")

        out = self.oracle.invoke(state)

        print(out)

        if out.tool_calls is None or len(out.tool_calls) == 0:
            return {
                "intermediate_steps": []
            }

        tool_name = out.tool_calls[0]['name']
        tool_args = out.tool_calls[0]['args']

        action_out = AgentAction(tool=tool_name, tool_input=tool_args, log="TBD")

        return {
            "intermediate_steps": [action_out],
        }

    def router(self, state: list):
        print("routing...", state)

        if isinstance(state["intermediate_steps"], list):
            return state["intermediate_steps"][-1].tool
        else:
            print("Routed invalid format")
            return "FinalAnswer"


    def run_tool(self, state: list):
        print("running tool...", state)

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
        print("received action: ", action)

        output = {"action": "none"}
        if action == "registration":
            output = {"action": "nop", "message": "I'm ok"}
        elif action == "execute":
            query = json_object['query']
            out = self.agent_executor.invoke({"input" : query, "chat_history": []})
            message = json.dumps(out["intermediate_steps"][-1].tool_input)
            output = {"action": "executed", "message": message}
            #output = {"action": "executed", "message": out["intermediate_steps"][-1].tool_input["answer"]}

        return output
        
