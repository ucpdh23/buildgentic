import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from buildgentic.code_operations.filesystem_resolver import git_pull, get_directory_structure, summarize_python_file, read_file_content

def test_git_pull_no_repo_path():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="The environment variable 'REPO_PATH' is not set."):
            git_pull()

def test_git_pull_invalid_directory():
    with patch.dict(os.environ, {'REPO_PATH': '/invalid/path'}):
        with pytest.raises(ValueError, match="The path /invalid/path is not a valid directory."):
            git_pull()

def test_git_pull_not_git_repo():
    with patch.dict(os.environ, {'REPO_PATH': '/tmp'}):
        with pytest.raises(ValueError, match="The path /tmp is not a valid git repository."):
            git_pull()

def test_get_directory_structure_no_path():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Environment variable 'DIRECTORY_PATH' is not set"):
            get_directory_structure()

def test_get_directory_structure():
    with patch.dict(os.environ, {'REPO_PATH': './buildgentic'}):
        structure = get_directory_structure()
        print(structure)

def test_summarize_python_file_no_file():
    with patch.dict(os.environ, {'REPO_PATH': '/valid/path'}):
        with pytest.raises(ValueError, match="The file /valid/path/nonexistent.py does not exist"):
            summarize_python_file('/nonexistent.py')

def test_summarize_python_file():
    with patch.dict(os.environ, {'REPO_PATH': '/valid/path'}):
        with patch('builtins.open', patch('io.StringIO', return_value=MagicMock(readlines=lambda: [
            'def foo():\n',
            '    """This is foo"""\n',
            '    pass\n',
            'def bar():\n',
            '    """This is bar"""\n',
            '    pass\n'
        ]))):
            summary = summarize_python_file('/test.py')
            expected_summary = "Method: foo\nDocumentation:\n\"\"\"This is foo\"\"\"\n\nMethod: bar\nDocumentation:\n\"\"\"This is bar\"\"\""
            assert summary == expected_summary

def test_read_file_content_no_file():
    with patch.dict(os.environ, {'REPO_PATH': '/valid/path'}):
        with pytest.raises(ValueError, match="The file /valid/path/nonexistent.txt does not exist"):
            read_file_content('/nonexistent.txt')

def test_read_file_content():
    with patch.dict(os.environ, {'REPO_PATH': '/valid/path'}):
        with patch('builtins.open', patch('io.StringIO', return_value=MagicMock(read=lambda: 'file content'))):
            content = read_file_content('/test.txt')
            assert content == 'file content'