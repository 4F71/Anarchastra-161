"""perf_ops — log_turn ve perf_stats."""

import os
import tempfile
import importlib
import tools.perf_ops as perf_ops_module


def _tmp_log(tmp_path):
    path = os.path.join(tmp_path, "perf.jsonl")
    original = perf_ops_module.PERF_LOG_PATH
    perf_ops_module.PERF_LOG_PATH = path
    return path, original


def test_log_turn_writes_file(tmp_path):
    path, original = _tmp_log(tmp_path)
    try:
        perf_ops_module.log_turn("test-model", eval_count=50, eval_duration_ns=1_000_000_000)
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read()
        assert "test-model" in content
        assert "tokens_per_sec" in content
    finally:
        perf_ops_module.PERF_LOG_PATH = original


def test_log_turn_skips_zero(tmp_path):
    path, original = _tmp_log(tmp_path)
    try:
        perf_ops_module.log_turn("model", eval_count=0, eval_duration_ns=0)
        assert not os.path.exists(path)
    finally:
        perf_ops_module.PERF_LOG_PATH = original


def test_perf_stats_no_file(tmp_path):
    path, original = _tmp_log(tmp_path)
    try:
        result = perf_ops_module.perf_stats()
        assert "Henuz" in result or "kaydi" in result
    finally:
        perf_ops_module.PERF_LOG_PATH = original


def test_perf_stats_returns_summary(tmp_path):
    path, original = _tmp_log(tmp_path)
    try:
        perf_ops_module.log_turn("mymodel", eval_count=100, eval_duration_ns=2_000_000_000)
        result = perf_ops_module.perf_stats()
        assert "mymodel" in result
        assert "50.0" in result  # 100 tokens / 2s = 50 tok/s
    finally:
        perf_ops_module.PERF_LOG_PATH = original


def test_perf_stats_model_filter(tmp_path):
    path, original = _tmp_log(tmp_path)
    try:
        perf_ops_module.log_turn("qwen", eval_count=80, eval_duration_ns=1_000_000_000)
        perf_ops_module.log_turn("hermes", eval_count=40, eval_duration_ns=1_000_000_000)
        result = perf_ops_module.perf_stats("qwen")
        assert "qwen" in result
        assert "hermes" not in result
    finally:
        perf_ops_module.PERF_LOG_PATH = original
