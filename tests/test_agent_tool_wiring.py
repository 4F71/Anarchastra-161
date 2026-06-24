from agents.coder import CODER_TOOL_EXECUTOR
from agents.reviewer import REVIEWER_TOOL_EXECUTOR


def test_coder_can_check_system_resources_and_query_audit_rollback():
    assert "check_system_resources" in CODER_TOOL_EXECUTOR
    assert "audit_tail" in CODER_TOOL_EXECUTOR
    assert "verify_audit_chain" in CODER_TOOL_EXECUTOR
    assert "rollback_history" in CODER_TOOL_EXECUTOR
    assert "rollback" not in CODER_TOOL_EXECUTOR  # destructive undo stays human-only


def test_reviewer_can_check_system_resources_and_query_audit_rollback():
    assert "check_system_resources" in REVIEWER_TOOL_EXECUTOR
    assert "audit_tail" in REVIEWER_TOOL_EXECUTOR
    assert "verify_audit_chain" in REVIEWER_TOOL_EXECUTOR
    assert "rollback_history" in REVIEWER_TOOL_EXECUTOR
    assert "rollback" not in REVIEWER_TOOL_EXECUTOR
