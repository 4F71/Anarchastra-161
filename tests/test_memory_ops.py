import os

from tools.memory_ops import MEMORY_DIR, remember, recall

TEST_PATH = os.path.join(MEMORY_DIR, "test_decisions.jsonl")


def _cleanup():
    if os.path.isfile(TEST_PATH):
        os.remove(TEST_PATH)


def test_remember_and_recall_roundtrip():
    _cleanup()
    remember("Qwen2.5-Coder abliterated coder icin secildi", tag="model-secimi", path=TEST_PATH)
    result = recall(n=5, path=TEST_PATH)
    assert "Qwen2.5-Coder" in result
    assert "model-secimi" in result
    _cleanup()


def test_recall_filters_by_query():
    _cleanup()
    remember("RAG icin ChromaDB kullanildi", tag="rag", path=TEST_PATH)
    remember("Rollback insan-only tutuldu", tag="rollback", path=TEST_PATH)
    result = recall(query="rollback", path=TEST_PATH)
    assert "Rollback insan-only" in result
    assert "ChromaDB" not in result
    _cleanup()


def test_recall_empty_store_returns_friendly_message():
    _cleanup()
    assert "bos" in recall(path=TEST_PATH)
    assert "bulunamadi" not in recall(path=TEST_PATH)


def test_recall_no_match_returns_friendly_message():
    _cleanup()
    remember("alakasiz bir not", path=TEST_PATH)
    result = recall(query="hicbiryerde-gecmeyen-kelime", path=TEST_PATH)
    assert "bulunamadi" in result
    _cleanup()
