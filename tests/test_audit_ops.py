import json
import os

from tools.audit_ops import (
    AUDIT_DIR,
    AUDIT_TOOL_EXECUTOR,
    GENESIS_HASH,
    append_event,
    audit_tail,
    verify_chain,
)

TEST_PATH = os.path.join(AUDIT_DIR, "test_audit.jsonl")


def _cleanup():
    if os.path.isfile(TEST_PATH):
        os.remove(TEST_PATH)


def test_append_event_chains_to_genesis():
    _cleanup()
    entry = append_event("tool_call", {"name": "read_file"}, path=TEST_PATH)
    assert entry["seq"] == 0
    assert entry["prev_hash"] == GENESIS_HASH
    _cleanup()


def test_verify_chain_reports_intact_after_multiple_appends():
    _cleanup()
    append_event("model_load", {"model": "qwen2.5-coder"}, path=TEST_PATH)
    append_event("tool_call", {"name": "write_file"}, path=TEST_PATH)
    append_event("network_request", {"host": "localhost", "outcome": "allowed"}, path=TEST_PATH)
    result = verify_chain(path=TEST_PATH)
    assert "saglam" in result
    assert "3 kayit" in result
    _cleanup()


def test_verify_chain_detects_tampering():
    _cleanup()
    append_event("tool_call", {"name": "read_file"}, path=TEST_PATH)
    append_event("tool_call", {"name": "write_file"}, path=TEST_PATH)

    with open(TEST_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    tampered = json.loads(lines[0])
    tampered["data"]["name"] = "DELETE_EVERYTHING"
    lines[0] = json.dumps(tampered, ensure_ascii=False) + "\n"
    with open(TEST_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    result = verify_chain(path=TEST_PATH)
    assert "BOZULMA TESPIT EDILDI" in result
    _cleanup()


def test_verify_chain_empty_returns_friendly_message():
    _cleanup()
    assert "Denetim kaydi yok" in verify_chain(path=TEST_PATH)


def test_audit_tail_lists_recent_entries():
    _cleanup()
    append_event("tool_call", {"name": "search_codebase"}, path=TEST_PATH)
    tail = audit_tail(5, path=TEST_PATH)
    assert "search_codebase" in tail
    _cleanup()


def test_audit_tool_executor_exposes_only_read_only_functions():
    assert AUDIT_TOOL_EXECUTOR["audit_tail"] is audit_tail
    assert AUDIT_TOOL_EXECUTOR["verify_audit_chain"] is verify_chain
    assert "append_event" not in AUDIT_TOOL_EXECUTOR
