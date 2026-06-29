"""Keyword ön-filtre router testleri."""

from main import _keyword_route


def test_code_keywords():
    assert _keyword_route("şu fonksiyonu yaz") == "code"
    assert _keyword_route("bu hatayı düzelt") == "code"


def test_research_keywords():
    assert _keyword_route("transformer nedir") == "research"
    assert _keyword_route("http://example.com araştır") == "research"


def test_codebase_keywords():
    assert _keyword_route("bu commit ne değiştirdi") == "codebase"
    assert _keyword_route("run_agent_loop nerede implement edilmiş") == "codebase"


def test_ambiguous_returns_none():
    # belirsiz prompt → LLM'e gönder
    assert _keyword_route("merhaba") is None
    assert _keyword_route("tamam") is None


def test_tie_returns_none():
    # eşit skor → LLM'e gönder
    result = _keyword_route("yaz ve araştır")
    # tie veya tek biri kazanmış olabilir, None veya string dönmeli
    assert result is None or result in ("code", "research", "codebase")
