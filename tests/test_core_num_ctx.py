import agents.config as config
from agents.core import DEFAULT_NUM_CTX, _num_ctx_for


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
