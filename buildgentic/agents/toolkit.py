from pydantic import BaseModel, Field

from buildgentic.code_operations.filesystem_resolver import git_pull, get_directory_structure, read_file_content


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


class SourceCodeAnalyzerTool(BaseModel):
    """
    Provides some actions to run in the base source code
    """
    action: str = Field(description="action to perform. Available values are: refresh, get_folder_structure, get_file_content")

    @staticmethod
    def invoke(args: dict):
        output = ""
        if args['action'] == "refresh":
            output = git_pull()
        elif args['action'] == "get_folder_structure":
            output = get_directory_structure()
        elif args['action'] == "get_file_content":
            output = read_file_content()

        return output