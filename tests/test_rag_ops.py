from unittest.mock import patch

from tools.rag_ops import EXCLUDE_DIRS, INCLUDE_EXTENSIONS, search_codebase


def test_search_codebase_without_index_returns_error():
    with patch("tools.rag_ops.INDEX_DIR", "definitely_does_not_exist_dir"):
        result = search_codebase("bu hic indexlenmemis bir sorgu")
    assert result.startswith("ERROR")


def test_private_and_generated_dirs_are_excluded():
    assert "private" in EXCLUDE_DIRS
    assert "workspace" in EXCLUDE_DIRS
    assert ".git" in EXCLUDE_DIRS


def test_only_source_like_extensions_are_indexed():
    assert ".py" in INCLUDE_EXTENSIONS
    assert ".md" in INCLUDE_EXTENSIONS
    assert ".bak" not in INCLUDE_EXTENSIONS
