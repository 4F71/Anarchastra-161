from unittest.mock import MagicMock

import requests

from agents.core import ModelManager


def make_client(loaded_names):
    client = MagicMock()
    client.list_loaded.return_value = [{"name": name} for name in loaded_names]
    return client


def test_no_conflict_when_nothing_loaded():
    client = make_client([])
    manager = ModelManager(client)

    manager.ensure_loaded("mistral-nemo")

    client.unload.assert_not_called()


def test_unloads_other_loaded_model_regardless_of_pool():
    client = make_client(["mistral-nemo:latest"])
    manager = ModelManager(client)

    manager.ensure_loaded("qwen2.5-coder:7b")

    client.unload.assert_called_once_with("mistral-nemo:latest")


def test_does_not_unload_same_model_already_loaded():
    client = make_client(["mistral-nemo:latest"])
    manager = ModelManager(client)

    manager.ensure_loaded("mistral-nemo")

    client.unload.assert_not_called()


def test_two_vram_native_models_still_conflict():
    """Coder (qwen2.5-coder) and Vision (qwen3-vl) both claim the full 8GB
    vram_native slot — loading one must evict the other."""
    client = make_client(["qwen3-vl:8b"])
    manager = ModelManager(client)

    manager.ensure_loaded("qwen2.5-coder:7b")

    client.unload.assert_called_once_with("qwen3-vl:8b")


def test_ps_query_failure_does_not_raise():
    client = MagicMock()
    client.list_loaded.side_effect = requests.RequestException("connection refused")
    manager = ModelManager(client)

    manager.ensure_loaded("mistral-nemo")

    client.unload.assert_not_called()
