import pytest
import requests

import agents.config as config
import tools.network_guard as network_guard


def test_blocked_host_raises_when_no_network():
    config.no_network = True
    config.audit_enabled = False
    try:
        with pytest.raises(RuntimeError, match="Air-gapped"):
            requests.get("http://example.com")
    finally:
        config.no_network = False


def test_allowed_localhost_passes_through_guard(monkeypatch):
    calls = []

    def fake_request(self, method, url, *args, **kwargs):
        calls.append(url)
        return "OK"

    monkeypatch.setattr(network_guard, "_original_request", fake_request)
    config.no_network = True
    config.audit_enabled = False
    try:
        result = requests.sessions.Session().request("GET", "http://localhost:11434/api/tags")
        assert result == "OK"
        assert calls == ["http://localhost:11434/api/tags"]
    finally:
        config.no_network = False


def test_network_unrestricted_when_no_network_off(monkeypatch):
    calls = []

    def fake_request(self, method, url, *args, **kwargs):
        calls.append(url)
        return "OK"

    monkeypatch.setattr(network_guard, "_original_request", fake_request)
    config.no_network = False
    result = requests.sessions.Session().request("GET", "http://example.com")
    assert result == "OK"
    assert calls == ["http://example.com"]
