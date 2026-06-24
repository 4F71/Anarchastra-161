import agents.config as config
from agents.core import DEFAULT_NUM_CTX, _num_ctx_for, estimate_context_usage


def test_returns_registry_value_for_known_model():
    config.ctx_override = None
    assert _num_ctx_for("qwen2.5-coder:7b") == 8192


def test_falls_back_to_default_for_unknown_model():
    config.ctx_override = None
    assert _num_ctx_for("hf.co/some/unregistered-model:Q4_K_M") == DEFAULT_NUM_CTX


def test_ctx_override_takes_precedence_over_everything():
    config.ctx_override = 32768
    try:
        assert _num_ctx_for("qwen2.5-coder:7b") == 32768
        assert _num_ctx_for("hf.co/some/unregistered-model:Q4_K_M") == 32768
    finally:
        config.ctx_override = None


def test_estimate_context_usage_computes_percentage():
    config.ctx_override = 1000
    try:
        messages = [{"role": "user", "content": "a" * 4000}]
        tokens, ctx, pct = estimate_context_usage(messages, "qwen2.5-coder:7b")
        assert tokens == 1000
        assert ctx == 1000
        assert pct == 100
    finally:
        config.ctx_override = None


def test_estimate_context_usage_caps_at_100_percent():
    config.ctx_override = 100
    try:
        messages = [{"role": "user", "content": "a" * 40000}]
        _, _, pct = estimate_context_usage(messages, "qwen2.5-coder:7b")
        assert pct == 100
    finally:
        config.ctx_override = None


def test_estimate_context_usage_ignores_empty_content():
    config.ctx_override = None
    messages = [{"role": "system", "content": None}, {"role": "user", "content": "abcd"}]
    tokens, ctx, pct = estimate_context_usage(messages, "qwen2.5-coder:7b")
    assert tokens == 1
    assert ctx == 8192
