import os

from tools.file_ops import WORKSPACE_ROOT, write_file
from tools.rollback_ops import ROLLBACK_TOOL_EXECUTOR, rollback, rollback_history


def test_rollback_restores_previous_content():
    write_file("rollback_existing.txt", "v1")
    write_file("rollback_existing.txt", "v2")
    result = rollback(1)
    assert "geri alindi" in result
    with open(os.path.join(WORKSPACE_ROOT, "rollback_existing.txt"), encoding="utf-8") as f:
        assert f.read() == "v1"


def test_rollback_deletes_newly_created_file():
    write_file("rollback_new.txt", "hello")
    target = os.path.join(WORKSPACE_ROOT, "rollback_new.txt")
    assert os.path.isfile(target)
    result = rollback(1)
    assert "silindi" in result
    assert not os.path.isfile(target)


def test_rollback_tool_executor_exposes_only_history_not_rollback_itself():
    assert ROLLBACK_TOOL_EXECUTOR["rollback_history"] is rollback_history
    assert "rollback" not in ROLLBACK_TOOL_EXECUTOR


def test_rollback_multiple_steps_in_sequence():
    write_file("rollback_seq.txt", "v1")
    write_file("rollback_seq.txt", "v2")
    write_file("rollback_seq.txt", "v3")
    rollback(2)
    with open(os.path.join(WORKSPACE_ROOT, "rollback_seq.txt"), encoding="utf-8") as f:
        assert f.read() == "v1"


def test_rollback_empty_journal_returns_friendly_message():
    # Drain any leftover journal entries from other tests first.
    while "gecmisi bos" not in rollback(1):
        pass
    assert "gecmisi bos" in rollback(1)


def test_rollback_history_lists_recent_entries():
    write_file("rollback_hist.txt", "v1")
    history = rollback_history(5)
    assert "rollback_hist.txt" in history
    rollback(1)  # cleanup
