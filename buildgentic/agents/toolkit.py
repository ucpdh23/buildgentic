from pydantic import BaseModel, Field


class SearchInADOTool(BaseModel):
    """
    Searchs in AzureDevOps workitems based on the information provided
    """
    query: str = Field(description="The query to search in AzureDevOps")

    @staticmethod
    def invoke(args: dict):
        return ""

class FinalAnswer(BaseModel):
    """
    Final answer to the user
    """
    answer: str = Field(description="The final answer to the user")

    @staticmethod
    def invoke(args: dict):
        return "answer"