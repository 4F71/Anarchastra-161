from agents.vision import VISION_TOOL_EXECUTOR, VISION_TOOLS_SCHEMA


def test_vision_agent_can_search_and_grep_codebase():
    assert "search_codebase" in VISION_TOOL_EXECUTOR
    assert "grep_codebase" in VISION_TOOL_EXECUTOR


def test_vision_agent_can_use_memory():
    assert "remember_decision" in VISION_TOOL_EXECUTOR
    assert "recall_decisions" in VISION_TOOL_EXECUTOR


def test_vision_tools_schema_names_match_executor_keys():
    schema_names = {t["function"]["name"] for t in VISION_TOOLS_SCHEMA}
    assert schema_names == set(VISION_TOOL_EXECUTOR.keys())
