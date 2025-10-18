import asyncio

from typing import List
from buildgentic.agents.base_agent import BaseAgent


glob_var = []

def register_agent(cls):
    """Decorator to automatically register agent classes."""

    global glob_var
    glob_var.append(cls)
    return cls


def build_registered_agents() -> List[BaseAgent]:
    """Return instances of all registered agents."""
    output = []
    for agent in glob_var:
        builder_method = getattr(agent, "build", None)
        if callable(builder_method):
            output.append(asyncio.run(builder_method()))
        else:
            agent = agent()
            output.append(agent)

    return output