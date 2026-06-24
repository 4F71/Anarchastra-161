from agents.coder import SOCRATIC_TOOL_EXECUTOR, SOCRATIC_TOOLS_SCHEMA


def test_socratic_mode_is_read_only():
    assert "write_file" not in SOCRATIC_TOOL_EXECUTOR
    assert "edit_file" not in SOCRATIC_TOOL_EXECUTOR
    assert "run_python" not in SOCRATIC_TOOL_EXECUTOR
    assert "web_search" not in SOCRATIC_TOOL_EXECUTOR


def test_socratic_mode_can_read_and_search():
    assert "read_file" in SOCRATIC_TOOL_EXECUTOR
    assert "list_workspace" in SOCRATIC_TOOL_EXECUTOR
    assert "grep_codebase" in SOCRATIC_TOOL_EXECUTOR
    assert "search_codebase" in SOCRATIC_TOOL_EXECUTOR


def test_socratic_tools_schema_names_match_executor_keys():
    schema_names = {t["function"]["name"] for t in SOCRATIC_TOOLS_SCHEMA}
    assert schema_names == set(SOCRATIC_TOOL_EXECUTOR.keys())
