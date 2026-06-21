"""Air-gapped mod (#4) icin ag erisimi koruyucusu.

requests.Session.request'i (ve varsa httpx.Client.send'i) import-time'da tek sefer yamalar.
Patch her zaman kuruludur ama gercek engelleme kontrolu her cagrida config.no_network okunarak
dinamik yapilir, yani /airgap toggle'i acmak/kapatmak icin ayri bir enable/disable fonksiyonuna
gerek yoktur.

Bilinen sinir: ddgs kutuphanesi requests yerine httpx kullanabilir; bu yuzden ayrica httpx.Client.send
da defansif olarak yamalanir. Birincil savunma agents/core.py::run_agent_loop'taki arac-semasi
temizligidir (whois_lookup/web_search/fetch_url modelin gorebildigi araclardan tamamen cikarilir);
bu modul ikincil/defense-in-depth katmanidir.
"""

import urllib.parse

import requests

import agents.config as config
from tools.audit_ops import append_event

_ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _check_and_log(method: str, url: str) -> None:
    host = urllib.parse.urlsplit(url).hostname
    allowed = host in _ALLOWED_HOSTS
    if config.audit_enabled:
        append_event(
            "network_request",
            {"method": method, "host": host, "url": url, "outcome": "allowed" if allowed else "blocked"},
        )
    if not allowed:
        raise RuntimeError(
            f"Air-gapped mod aktif: '{host}' adresine istek engellendi (sadece localhost izinli)."
        )


_original_request = requests.sessions.Session.request


def _guarded_request(self, method, url, *args, **kwargs):
    if config.no_network:
        _check_and_log(method, url)
    return _original_request(self, method, url, *args, **kwargs)


if not getattr(requests.sessions.Session.request, "_freeguard_patched", False):
    _guarded_request._freeguard_patched = True
    requests.sessions.Session.request = _guarded_request


try:
    import httpx

    _original_httpx_send = httpx.Client.send

    def _guarded_httpx_send(self, request, *args, **kwargs):
        if config.no_network:
            _check_and_log(request.method, str(request.url))
        return _original_httpx_send(self, request, *args, **kwargs)

    if not getattr(httpx.Client.send, "_freeguard_patched", False):
        _guarded_httpx_send._freeguard_patched = True
        httpx.Client.send = _guarded_httpx_send
except ImportError:
    pass
