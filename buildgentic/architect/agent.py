from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from a2a.types import AgentCapabilities, AgentCard, AgentSkill, TransportProtocol

from buildgentic.tools.tools_azureDevOps import add_comment_to_ticket, download_attachment, get_tickets_assigned_to_me, get_work_item_details, load_context, update_ticket_description, update_ticket_status



manager_context = load_context("Jonathan")

def get_architect_agent(model_name) -> Agent:
    """Creates and returns the architect agent."""

    return Agent(
        model=LiteLlm(model=model_name),
        name='architect',
        description=manager_context['description'],
        instruction=manager_context['instruction'],
        tools=[
            get_tickets_assigned_to_me,
            get_work_item_details,
            update_ticket_description,
            add_comment_to_ticket,
            download_attachment,
            update_ticket_status
        ],
    )


def get_architect_agent_card(agent_url: str) -> AgentCard:
    """Creates and returns the architect agent card."""
    return AgentCard(
        name="Architect Agent",
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


root_agent = get_architect_agent("openai/gpt-4o")
