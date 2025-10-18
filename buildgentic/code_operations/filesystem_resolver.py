import subprocess
import os


def git_pull():
    """
    Runs 'git pull' in the repository path specified by the environment variable 'REPO_PATH'.
    """
    repo_path = os.getenv('REPO_PATH2')
    print("repo_path", repo_path)

    if not repo_path:
        raise ValueError("The environment variable 'REPO_PATH' is not set.")
    
    if not os.path.isdir(repo_path):
        raise ValueError(f"The path {repo_path} is not a valid directory.")
    
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        raise ValueError(f"The path {repo_path} is not a valid git repository.")
    
    try:
        result = subprocess.run(['git', 'pull'], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running git pull: {e.stderr.decode('utf-8')}")
    
    return "source code updated"

# Example usage:
# Make sure to set the environment variable 'REPO_PATH' before running the function
# os.environ['REPO_PATH'] = '/path/to/your/repo'
# git_pull()

def get_directory_structure():
    """
    Returns a string representing the full structure of files and folders inside the given path.
    This structure includes nested folders and files. The path is retrieved from an environment variable.

    :return: A string representing the directory structure.
    """
    path = os.getenv('REPO_PATH2')
    if not path:
        raise ValueError("Environment variable 'DIRECTORY_PATH' is not set")

    structure = []

    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            structure.append(f"{sub_indent}{f}")

    return "\n".join(structure)

# Example usage:
# Make sure to set the environment variable 'DIRECTORY_PATH' before running the script
# print(get_directory_structure())

def summarize_python_file(file_path):
    """
    Returns a summary of a Python file as a string. The summary includes a list of methods and their documentation.

    :param file_path: Path to the Python file.
    :return: A string representing the summary of the file.
    """

    path = os.getenv('REPO_PATH2')
    file_path = path + file_path

    if not os.path.isfile(file_path):
        raise ValueError(f"The file {file_path} does not exist")

    summary = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    inside_docstring = False
    current_method = None
    docstring_lines = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('def '):
            if current_method:
                summary.append(f"Method: {current_method}")
                if docstring_lines:
                    summary.append("Documentation:")
                    summary.extend(docstring_lines)
                summary.append("")
            current_method = stripped_line.split('(')[0][4:]
            docstring_lines = []
        elif stripped_line.startswith('"""') or stripped_line.startswith("'''"):
            if inside_docstring:
                inside_docstring = False
            else:
                inside_docstring = True
                docstring_lines.append(stripped_line)
        elif inside_docstring:
            docstring_lines.append(stripped_line)

    if current_method:
        summary.append(f"Method: {current_method}")
        if docstring_lines:
            summary.append("Documentation:")
            summary.extend(docstring_lines)

    return "\n".join(summary)


def read_file_content(file_path):
    """
    Returns the content of a file as a string.

    :param file_path: Path to the file.
    :return: A string representing the content of the file.
    """

    path = os.getenv('REPO_PATH2')
    file_path = path + "/" + file_path

    if not os.path.isfile(file_path):
        raise ValueError(f"The file {file_path} does not exist")

    with open(file_path, 'r') as file:
        content = file.read()

    return content

# Example usage:
# print(read_file_content('/path/to/your/file'))