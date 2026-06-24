import os
from unittest.mock import MagicMock

from tools.memory_ops import MEMORY_DIR, remember, recall, summarize_and_remember

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


def _client_returning(content: str) -> MagicMock:
    client = MagicMock()
    client.chat.return_value = {"message": {"content": content}}
    return client


def test_summarize_and_remember_skips_short_history():
    _cleanup()
    client = _client_returning("onemli bir karar")
    messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": "selam"}]
    result = summarize_and_remember(client, "fake-model", messages, path=TEST_PATH)
    assert result == ""
    client.chat.assert_not_called()
    _cleanup()


def test_summarize_and_remember_skips_when_model_says_yok():
    _cleanup()
    client = _client_returning("YOK")
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "merhaba"},
        {"role": "assistant", "content": "merhaba, nasil yardimci olabilirim"},
    ]
    result = summarize_and_remember(client, "fake-model", messages, path=TEST_PATH)
    assert result == ""
    assert recall(path=TEST_PATH) == "Hafiza bos, henuz kayitli karar yok."
    _cleanup()


def test_summarize_and_remember_saves_real_summary():
    _cleanup()
    client = _client_returning("Coder modeli icin num_ctx 8192 secildi.")
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "num_ctx ne olmali?"},
        {"role": "assistant", "content": "8192 onerdim"},
    ]
    result = summarize_and_remember(client, "fake-model", messages, path=TEST_PATH)
    assert "num_ctx 8192" in result
    assert "num_ctx 8192" in recall(path=TEST_PATH)
    _cleanup()
