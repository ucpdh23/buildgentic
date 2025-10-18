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
    Final action to perform once the analysis is done
    """

    #action: str = Field(description="The action to take. Available values are: addCommentToADOWorkItem, updateDescriptionToADOWorkItem, createSubTasksToADOWorkItem, reassignADOWorkItem")
    subtasks: list = Field(description="The subtasks to add to the ADOWorkItem if needed. The list must contain the title and description of each subtask. Otherwise, leave it empty.")
    comment: str = Field(description="Any new comment to add to the workitem. Otherwise, leave it empty.")
    description: str = Field(description="The new description to update to the workitem. Otherwise, leave it empty.")
    assignee: str = Field(description="The new assignee of the workitem. Available values are: Bob (me), developer, tester, business.")

    @staticmethod
    def invoke(args: dict):
        return "answer"

class AddCommentToADOWorkItemFinalAnswer(BaseModel):
    """
    Adds a comment to an AzureDevOps workitem
    """
    comment: str = Field(description="The comment to add to the workitem")

    @staticmethod
    def invoke(args: dict):
        return ""

class UpdateDescriptionToADOWorkItemFinalAnswer(BaseModel):
    """
    Updates the description of an AzureDevOps workitem
    """
    description: str = Field(description="The new description to update to the workitem")

    @staticmethod
    def invoke(args: dict):
        return ""

class CreateSubtasksToADOWorkItemFinalAnswer(BaseModel):
    """
    Creates one or several subtasks to an AzureDevOps workitem
    """
    title: str = Field(description="The title of the subtask")
    description: str = Field(description="The description of the subtask")

    @staticmethod
    def invoke(args: dict):
        return ""

class RequestADOWorkItemReassignmentFinalAnswer(BaseModel):
    """
    Requests a reassignment of an AzureDevOps workitem
    """
    assignee: str = Field(description="The new assignee of the workitem. Available values are: me, developer, tester, business")

    @staticmethod
    def invoke(args: dict):
        return ""


class SourceCodeAnalyzerTool(BaseModel):
    """
    Provides some actions to run in the base source code
    """
    action: str = Field(description="action to perform. Available values are: refresh, get_folder_structure, get_file_content")
    parameter: str = Field(description="parameter to pass to the action if needed")

    @staticmethod
    def invoke(args: dict):
        output = ""
        if args['action'] == "refresh":
            output = git_pull()
        elif args['action'] == "get_folder_structure":
            output = get_directory_structure()
        elif args['action'] == "get_file_content":
            output = read_file_content(args['parameter'])

        return output

class DeveloperFinalAnswer(BaseModel):
    """
    Final action to perform once the task is complete
    """

    action: str = Field(description="The action to take. Available values are: addCommentToADOWorkItem, updateDescriptionToADOWorkItem, createSubTasksToADOWorkItem, reassignADOWorkItem")
    subtasks: list = Field(description="The subtasks to add to the ADOWorkItem if needed. The list must contain the title and description of each subtask. Otherwise, leave it empty.")
    comment: str = Field(description="Any new comment to add to the workitem. Otherwise, leave it empty.")

    @staticmethod
    def invoke(args: dict):
        return "answer"