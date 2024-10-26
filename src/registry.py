glob_var = []

def register_agent(cls):
    """Decorator to automatically register agent classes."""

    global glob_var
    glob_var.append(cls)
    return cls


def get_registered_agents():
    """Return instances of all registered agents."""

    return [agent() for agent in glob_var]