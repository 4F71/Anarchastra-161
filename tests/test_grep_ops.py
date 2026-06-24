import pytest

from tools.grep_ops import grep_codebase


def test_grep_rejects_path_escape():
    with pytest.raises(ValueError):
        grep_codebase("foo", path="../outside")


def test_grep_rejects_invalid_regex():
    with pytest.raises(ValueError):
        grep_codebase("foo(", path=".")


def test_grep_finds_known_symbol():
    result = grep_codebase("def grep_codebase", path="tools/grep_ops.py")
    assert "grep_ops.py" in result
    assert "def grep_codebase" in result


def test_grep_no_match_returns_placeholder():
    result = grep_codebase("definitely_not_a_real_symbol_xyz123", path="tools/grep_ops.py")
    assert result == "(eslesme bulunamadi)"


def test_grep_respects_max_results():
    result = grep_codebase("import", path="tools", max_results=1)
    assert len(result.splitlines()) == 1
