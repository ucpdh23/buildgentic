from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol

from buildgentic.tools.tools_azureDevOps import load_context

manager_context = load_context("Wilson")

def get_manager_agent(model_name) -> Agent:
    """Creates and returns the manager agent."""
    return Agent(
        model=LiteLlm(model=model_name),
        name='manager',
        description=manager_context['description'],
        instruction=manager_context['instruction'],
        sub_agents=[
            RemoteA2aAgent(
                name="architect",
                description="Architect",
                agent_card=(
                    f"http://localhost:8008/a2a/architect{AGENT_CARD_WELL_KNOWN_PATH}"
                ),
            ),
            RemoteA2aAgent(
                name="developer",
                description="Developer",
                agent_card=(
                    f"http://localhost:8008/a2a/developer{AGENT_CARD_WELL_KNOWN_PATH}"
                ),
            ),
            RemoteA2aAgent(
                name="qa",
                description="QA",
                agent_card=(
                    f"http://localhost:8008/a2a/qa{AGENT_CARD_WELL_KNOWN_PATH}"
                ),
            ),
            RemoteA2aAgent(
                name="compliance",
                description="Compliance",
                agent_card=(
                    f"http://localhost:8008/a2a/compliance{AGENT_CARD_WELL_KNOWN_PATH}"
                ),
            ),
        ]
    )


def get_manager_agent_card(agent_url: str) -> AgentCard:
    """Creates and returns the manager agent card."""

    return AgentCard(
        name="Manager Agent",
        description=manager_context["description"],
        url=agent_url,
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="manager_agent",
                name=manager_context["name"],
                description=manager_context['description'],
                tags=[]
            )
        ],
    )


root_agent = get_manager_agent("openai/gpt-4o")
