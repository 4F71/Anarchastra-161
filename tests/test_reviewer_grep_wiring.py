"""ReviewerAgent grep_codebase wiring ve /debug modu kontrolleri."""

from agents.reviewer import REVIEWER_TOOLS_SCHEMA, REVIEWER_TOOL_EXECUTOR
from agents.coder import DEBUG_SYSTEM_PROMPT, CODER_TOOLS_SCHEMA


def test_reviewer_has_grep_codebase_schema():
    names = [t["function"]["name"] for t in REVIEWER_TOOLS_SCHEMA]
    assert "grep_codebase" in names


def test_reviewer_has_grep_codebase_executor():
    assert "grep_codebase" in REVIEWER_TOOL_EXECUTOR


def test_debug_system_prompt_exists():
    assert isinstance(DEBUG_SYSTEM_PROMPT, str)
    assert len(DEBUG_SYSTEM_PROMPT) > 10


def test_debug_mode_uses_coder_tools():
    # debug modu coder araçlarını kullanır — schema boş olmamalı
    assert len(CODER_TOOLS_SCHEMA) > 0
