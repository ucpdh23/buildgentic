from langchain_core.agents import AgentAction


def create_scratchpad(intermediate_steps: list[AgentAction]):
    print("create_scratchpad", len(intermediate_steps))

    if len(intermediate_steps) == 0:
        return ""

    research_steps = []
    for i, action in enumerate(intermediate_steps):
        if action.log != "TBD":
            research_steps.append(
                f"Tool: {action.tool}, input: {action.tool_input}\n"
                f"Output: {action.log}\n"
            )
    
    print("\n---\n".join(research_steps))
    return "\n---\n".join(research_steps)