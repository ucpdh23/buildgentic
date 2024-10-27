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

    return [agent() for agent in glob_var]