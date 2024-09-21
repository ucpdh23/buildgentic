from baseAgent import BaseAgent
from registry import register_agent


@register_agent
class KeywordAgent(BaseAgent):
    def __init__(self):
        self.keyword = "keyword"

    def evaluate(self, message: str) -> bool:
        # If the keyword is in the message, the agent will respond
        return self.keyword in message

    def execute(self, message: str):
        print(f"KeywordAgent: Executing because '{self.keyword}' was found in the message '{message}'.")
