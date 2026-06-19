"""Web arama ve URL fetch araçları — ajanlara internet erişimi sağlar."""

import json
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo üzerinden arama yapar, sonuçları metin olarak döndürür."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "Arama sonucu bulunamadı."
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"[{i}] {r.get('title', '')}\n    URL: {r.get('href', '')}\n    {r.get('body', '')}")
        return "\n\n".join(output)
    except Exception as e:
        return f"Arama hatası: {e}"


def fetch_url(url: str, max_chars: int = 8000) -> str:
    """Bir URL'yi GET ile çekip saf metni döndürür (HTML soyulur)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.splitlines() if l.strip()]
        result = "\n".join(lines)
        if len(result) > max_chars:
            result = result[:max_chars] + f"\n\n... (içerik kısaltıldı, toplam {len(result)} karakter)"
        return result
    except Exception as e:
        return f"URL fetch hatası: {e}"


def whois_lookup(domain: str) -> str:
    """RDAP (IANA bootstrap) ile domain kayıt bilgisini sorgular.
    Kaydın alınıp alınmadığını, tarihleri ve registrar bilgisini döndürür."""
    domain = domain.strip().lower()
    for prefix in ("www.", "http://", "https://"):
        domain = domain.removeprefix(prefix)

    # IANA RDAP bootstrap — tüm TLD'leri destekler
    try:
        resp = requests.get(f"https://rdap.iana.org/domain/{domain}", timeout=10)
        if resp.status_code == 404:
            return f"✅ '{domain}' domaini ALINMAMIŞ (müsait)."
        resp.raise_for_status()
        data = resp.json()
        name = data.get("ldhName", domain)
        status = data.get("status", [])
        events = {e["eventAction"]: e["eventDate"] for e in data.get("events", [])}
        registrar = ""
        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [None, []])[1]
                for field in vcard:
                    if isinstance(field, list) and field[0] == "fn":
                        registrar = field[3]
                        break
        lines = [
            f"🔴 '{name}' domaini ALINMIŞ.",
            f"Durum       : {', '.join(status) or 'bilinmiyor'}",
            f"Registrar   : {registrar or 'bilinmiyor'}",
            f"Kayıt tarihi: {events.get('registration', 'bilinmiyor')}",
            f"Son güncell.: {events.get('last changed', 'bilinmiyor')}",
            f"Bitiş tarihi: {events.get('expiration', 'bilinmiyor')}",
        ]
        return "\n".join(lines)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return f"✅ '{domain}' domaini ALINMAMIŞ (müsait)."
        # Fallback: who.is sayfasını çek
        try:
            return f"[who.is]\n{fetch_url(f'https://who.is/whois/{domain}', max_chars=2000)}"
        except Exception:
            return f"Domain sorgusu başarısız: {e}"
    except Exception as e:
        return f"Domain sorgusu hatası: {e}"


WEB_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "whois_lookup",
            "description": (
                "Bir domainin kayıtlı olup olmadığını, kayıt tarihini ve registrar bilgisini sorgular. "
                "Domain durumu, whois, müsaitlik kontrolü için ÖNCE bu aracı kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Sorgulanacak domain adı, örn: tilki.dev veya example.com",
                    },
                },
                "required": ["domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "DuckDuckGo ile internet araması yapar. Güncel haber, teknik bilgi "
                "veya genel sorgular için kullan. Domain sorgusu için whois_lookup tercih et."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Arama sorgusu, mümkün olduğunca spesifik olsun.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Döndürülecek maksimum sonuç sayısı (varsayılan: 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": (
                "Bir web sayfasını okur ve içeriğini düz metin olarak döndürür. "
                "web_search ile bulduğun bir URL'yi daha detaylı incelemek için kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Okunacak URL (https:// ile başlamalı).",
                    },
                },
                "required": ["url"],
            },
        },
    },
]

WEB_TOOL_EXECUTOR = {
    "whois_lookup": whois_lookup,
    "web_search": web_search,
    "fetch_url": fetch_url,
}
