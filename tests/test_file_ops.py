import os

import pytest

from tools.file_ops import WORKSPACE_ROOT, edit_file, write_file
from tools.rollback_ops import rollback


def test_write_file_overwrite_is_rollback_recoverable():
    write_file("edit_target.txt", "v1")
    write_file("edit_target.txt", "v2")
    rollback(1)
    with open(os.path.join(WORKSPACE_ROOT, "edit_target.txt"), encoding="utf-8") as f:
        assert f.read() == "v1"


def test_edit_file_replaces_unique_match():
    write_file("edit_unique.txt", "hello world")
    edit_file("edit_unique.txt", "world", "free")
    with open(os.path.join(WORKSPACE_ROOT, "edit_unique.txt"), encoding="utf-8") as f:
        assert f.read() == "hello free"


def test_edit_file_rejects_ambiguous_match():
    write_file("edit_dup.txt", "x = 1\nx = 1\n")
    with pytest.raises(ValueError):
        edit_file("edit_dup.txt", "x = 1", "x = 2")


def test_edit_file_rejects_missing_match():
    write_file("edit_nomatch.txt", "hello world")
    with pytest.raises(ValueError):
        edit_file("edit_nomatch.txt", "not present", "x")
