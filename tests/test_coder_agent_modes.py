from unittest.mock import MagicMock, patch

from agents.coder import CoderAgent, SOCRATIC_SYSTEM_PROMPT, SOCRATIC_TOOLS_SCHEMA


def test_socratic_mode_uses_socratic_prompt_and_tools():
    fake_client = MagicMock()
    agent = CoderAgent(model="qwen2.5-coder:7b", client=fake_client)
    agent.manager.ensure_loaded = MagicMock()

    with patch("agents.coder.run_agent_loop", return_value="ilk soru") as mock_loop:
        result = agent.run("core.py'daki run_agent_loop'u inceleyelim", mode="socratic")

    assert result == "ilk soru"
    _, kwargs = mock_loop.call_args
    messages = mock_loop.call_args.args[2]
    assert messages[0]["content"] == SOCRATIC_SYSTEM_PROMPT
    assert kwargs["tools_schema"] == SOCRATIC_TOOLS_SCHEMA
