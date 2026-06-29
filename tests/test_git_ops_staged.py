"""git_diff_staged — schema ve executor varligi."""

from tools.git_ops import GIT_TOOLS_SCHEMA, GIT_TOOL_EXECUTOR, git_diff_staged


def test_git_diff_staged_in_schema():
    names = [t["function"]["name"] for t in GIT_TOOLS_SCHEMA]
    assert "git_diff_staged" in names


def test_git_diff_staged_in_executor():
    assert "git_diff_staged" in GIT_TOOL_EXECUTOR


def test_git_diff_staged_returns_string():
    result = git_diff_staged()
    assert isinstance(result, str)
