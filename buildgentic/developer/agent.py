from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol

from buildgentic.tools.tools_azureDevOps import load_context



manager_context = load_context("Anna")

def get_developer_agent(model_name) -> Agent:
    """Creates and returns the developer agent."""

    return Agent(
        model=LiteLlm(model=model_name),
        name='developer',
        description=manager_context['description'],
        instruction=manager_context['instruction'],
    )


def get_developer_agent_card(agent_url: str) -> AgentCard:
    """Creates and returns the developer agent card."""
    return AgentCard(
        name="Developer Agent",
        description=manager_context['description'],
        url=agent_url,
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="conversational_agent",
                name="Conversational Agent",
                description="A Smart Conversational Agent Enhanced with Web Search Capabilities",
                tags=[]
            )
        ],
    )


root_agent = get_developer_agent("openai/gpt-4o")
