"""Kriptografik denetim izi — hash-zincirli, degistirilmesi fark edilebilir (tamper-evident)
kayit defteri. Air-gapped mod (#4) ile birlikte kullanildiginda "disariya hic istek gitmedi"
iddiasini kanitlar; bagimsiz olarak da tool_call/model yukleme gibi olaylari denetlemek icin kullanilabilir.

logs/free.log'dan kasitli olarak ayri tutulur: o dosya RotatingFileHandler kullanir ve eski
yedekleri siler, bu da kirilmaz bir hash zinciriyle uyumsuzdur.
"""

import hashlib
import json
import os

AUDIT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "audit")
)
AUDIT_PATH = os.path.join(AUDIT_DIR, "audit.jsonl")
GENESIS_HASH = "0" * 64


def _read_entries(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _compute_hash(prev_hash: str, seq: int, ts: str, event: str, data: dict) -> str:
    payload = json.dumps(
        {"seq": seq, "ts": ts, "event": event, "data": data, "prev_hash": prev_hash},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append_event(event: str, data: dict, path: str = AUDIT_PATH) -> dict:
    """Zincire yeni bir olay ekler; onceki kaydin hash'ini prev_hash olarak kullanir."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    import time

    entries = _read_entries(path)
    prev_hash = entries[-1]["hash"] if entries else GENESIS_HASH
    seq = len(entries)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry_hash = _compute_hash(prev_hash, seq, ts, event, data)
    entry = {"seq": seq, "ts": ts, "event": event, "data": data, "prev_hash": prev_hash, "hash": entry_hash}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def verify_chain(path: str = AUDIT_PATH) -> str:
    """Zinciri bastan sona yeniden hesaplayip dogrular; ilk kirilma noktasini raporlar."""
    entries = _read_entries(path)
    if not entries:
        return "Denetim kaydi yok."

    prev_hash = GENESIS_HASH
    for entry in entries:
        if entry.get("prev_hash") != prev_hash:
            return f"BOZULMA TESPIT EDILDI: kayit #{entry.get('seq')} prev_hash uyusmuyor."
        expected = _compute_hash(prev_hash, entry["seq"], entry["ts"], entry["event"], entry["data"])
        if expected != entry.get("hash"):
            return f"BOZULMA TESPIT EDILDI: kayit #{entry.get('seq')} hash uyusmuyor (icerik degistirilmis olabilir)."
        prev_hash = entry["hash"]

    return f"Zincir saglam: {len(entries)} kayit dogrulandi, degistirilme tespit edilmedi."


def audit_tail(n: int = 10, path: str = AUDIT_PATH) -> str:
    """Son n kaydi en yeniden eskiye listeler (dogrulama yapmaz)."""
    entries = _read_entries(path)
    if not entries:
        return "Denetim kaydi yok."

    n = max(1, min(n, len(entries)))
    lines = []
    for entry in reversed(entries[-n:]):
        lines.append(f"[{entry['ts']}] #{entry['seq']} {entry['event']} {json.dumps(entry['data'], ensure_ascii=False)}")
    return "\n".join(lines)
