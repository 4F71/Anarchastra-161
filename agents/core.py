"""Ollama HTTP client, VRAM/RAM model discipline, and the agentic tool-call loop."""

import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import agents.config as config

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "free.log")
logger = logging.getLogger("free")
logger.setLevel(logging.INFO)
_log_handler = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
_log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(_log_handler)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Donanım dogrulamasi (HF model kartlari) sonrasi gercekci registry:
# GLM-5.2 (753B), MiniMax-M3 (428B) ve Kimi-K2.7-Code (1T) 8GB VRAM/32GB RAM'e
# sigmiyor; coder icin Qwen2.5-Coder-7B, research icin Hermes3-8B, vision
# icin Qwen3-VL-8B ile degistirildi (hepsi Ollama'da tool-calling destekli).
MODEL_REGISTRY = {
    "qwen2.5-coder": {"pool": "vram_native", "max_ctx": None, "role": "coder"},
    "hermes3": {"pool": "vram_heavy", "max_ctx": None, "role": "research"},
    "qwen3-vl": {"pool": "vram_native", "max_ctx": None, "role": "vision"},
    "mistral-nemo": {"pool": "vram_heavy", "max_ctx": None, "role": "codebase"},
}

# Yaklasik VRAM kullanim tahmini (GB) — CLAUDE.md model_registry runtime_profile
# notlarindan alindi, sadece `free status` icinde bilgilendirme amacli.
MODEL_VRAM_ESTIMATES_GB = {
    "qwen2.5-coder": 5.9,
    "hermes3": 5.0,
    "qwen3-vl": 6.5,
    "mistral-nemo": 7.1,
}

DEFAULT_CODER_MODEL = "hf.co/yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF:Q3_K_M"
DEFAULT_RESEARCH_MODEL = "hermes3:8b"
DEFAULT_VISION_MODEL = "qwen3-vl:8b"
# search_codebase (RAG) sentezinde hermes3/qwen2.5-coder denemelerinden daha iyi sonuc verdi
# (bkz. agents/research.py RESEARCH_SYSTEM_PROMPT) — bu yuzden codebase sorulari icin ayri rol.
DEFAULT_CODEBASE_MODEL = "mistral-nemo:latest"

MAX_TURNS_DEFAULT = 8


def _base_name(model_id: str) -> str:
    return model_id.split(":")[0]


class OllamaClient:
    def __init__(self, host: str | None = None):
        self.host = host or OLLAMA_HOST

    def list_loaded(self) -> list[dict]:
        resp = requests.get(f"{self.host}/api/ps", timeout=10)
        resp.raise_for_status()
        return resp.json().get("models", [])

    def list_models(self) -> list[dict]:
        """Lists all locally pulled models (not just ones currently loaded in memory)."""
        resp = requests.get(f"{self.host}/api/tags", timeout=10)
        resp.raise_for_status()
        return resp.json().get("models", [])

    def unload(self, model_id: str) -> None:
        requests.post(
            f"{self.host}/api/generate",
            json={"model": model_id, "prompt": "", "keep_alive": 0},
            timeout=30,
        )
        logger.info("unloaded model=%s", model_id)

    def embed(self, model: str, text: str) -> list[float]:
        resp = requests.post(
            f"{self.host}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("embedding", [])

    def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None,
              options: dict | None = None, format: str | None = None) -> dict:
        payload = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        if options:
            payload["options"] = options
        if format:
            payload["format"] = format
        resp = requests.post(f"{self.host}/api/chat", json=payload, timeout=600)
        resp.raise_for_status()
        return resp.json()

    def chat_stream(self, model: str, messages: list[dict],
                    options: dict | None = None) -> dict:
        """Streams tokens to stdout in real-time, returns assembled message dict."""
        payload = {"model": model, "messages": messages, "stream": True}
        if options:
            payload["options"] = options
        resp = requests.post(f"{self.host}/api/chat", json=payload,
                             timeout=600, stream=True)
        resp.raise_for_status()

        full_content = ""
        final_message = {}
        console.print(f"\n[bold cyan]🤖 {model}[/] [dim](streaming)[/]")
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            try:
                chunk = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            token = chunk.get("message", {}).get("content", "")
            if token:
                print(token, end="", flush=True)
                full_content += token
            if chunk.get("done"):
                final_message = chunk.get("message", {})
                break
        print()  # newline after streaming
        final_message["content"] = full_content
        return {"message": final_message}


class ModelManager:
    """Enforces: only one model loaded at a time — 8GB VRAM is a hard ceiling
    regardless of pool (vram_native models conflict with each other too, e.g.
    coder vs. vision)."""

    def __init__(self, client: OllamaClient, registry: dict | None = None):
        self.client = client
        self.registry = registry or MODEL_REGISTRY

    def _info(self, model_id: str) -> dict:
        return self.registry.get(_base_name(model_id), {"pool": "vram_heavy", "max_ctx": None})

    def ensure_loaded(self, model_id: str) -> dict:
        info = self._info(model_id)
        target = _base_name(model_id)

        try:
            loaded = self.client.list_loaded()
        except requests.RequestException as exc:
            logger.warning("could not query /api/ps: %s", exc)
            return info

        for entry in loaded:
            name = entry.get("name") or entry.get("model") or ""
            base = _base_name(name)
            if not base or base == target:
                continue
            logger.info("unloading model=%s to free VRAM for %s", base, target)
            self.client.unload(name)

        return info


from rich.console import Console
console = Console()


def _find_first_balanced_json_object(text: str) -> tuple[int, str | None]:
    """Scans for the first balanced {...} object in text, ignoring braces inside
    string literals. Returns (start_index, json_str) or (-1, None) if none found.
    Needed because a naive find('{')/rfind('}') grabs everything between the FIRST
    '{' and the LAST '}' — if the model writes two JSON blocks (e.g. an example
    followed by the real call), that span is not valid JSON and the tool call is
    silently dropped."""
    search_from = text.find('{')
    while search_from != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(search_from, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return search_from, text[search_from:i + 1]
        search_from = text.find('{', search_from + 1)
    return -1, None


def run_agent_loop(
    client: OllamaClient,
    model: str,
    messages: list[dict],
    tools_schema: list[dict] | None = None,
    tool_executor: dict | None = None,
    max_turns: int = MAX_TURNS_DEFAULT,
    options: dict | None = None,
) -> str:
    """Drives the chat/tool-call loop until the model returns a final text answer."""
    tool_executor = tool_executor or {}
    options = options or {"temperature": 0.3, "repeat_penalty": 1.2, "top_p": 0.9}
    history = messages

    for turn in range(max_turns):
        t0 = time.time()
        if config.verbose:
            console.print(f"[dim]\u2500\u2500 TUR {turn+1}/{max_turns} | model={model} | mesaj_sayısı={len(history)} \u2500\u2500[/]")
            response = client.chat_stream(model, history, options=options)
        else:
            with console.status(f"[bold cyan]{model} düşünüyor...[/]"):
                response = client.chat(model, history, options=options)
        
        elapsed = time.time() - t0
        
        message = response.get("message", {})
        
        tool_calls = message.get("tool_calls")
        content = message.get("content", "")
        
        # Fallback parser if the model leaks the tool call JSON into content
        if not tool_calls and content:
            start, json_str = _find_first_balanced_json_object(content)
            if json_str is not None:
                try:
                    parsed = json.loads(json_str)
                    if "name" in parsed and "arguments" in parsed:
                        tool_calls = [{"function": parsed}]
                        # Remove the JSON from content so we don't display it raw
                        content = content[:start].strip()
                        message["content"] = content
                except Exception as e:
                    logger.warning("Fallback JSON parse error: %s", e)

        # Append assistant message to history
        history.append(message)

        if config.verbose and content:
            console.print(f"\n[dim]⏱️  Süre: {elapsed:.1f}s[/]")
            console.print(f"[dim]── RAW JSON / TOOL PARSER SONRASI ──\n{content}[/]")
        
        # Print any conversational text if we didn't already stream it
        if content and not config.verbose:
            from rich.markdown import Markdown
            console.print(f"\n[bold cyan]🤖 {model}[/] [dim]({elapsed:.1f}s)[/]")
            console.print(Markdown(content))

        # If no tools called, we are done!
        if not tool_calls:
            return "" # Return empty string since we already printed the content

        for call in tool_calls:
            fn = call.get("function", {})
            name = fn.get("name")
            raw_args = fn.get("arguments") or {}
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

            logger.info("tool_call name=%s args=%s", name, args)
            console.print(f"[dim]⚙️  Çalıştırılıyor: {name}({args})...[/]")

            if name in ("write_file", "edit_file") and config.confirm_writes:
                from rich.prompt import Confirm
                if not Confirm.ask(f"[yellow]⚠️  '{name}' calistirilsin mi?[/]"):
                    result = "ERROR: kullanici onaylamadi, islem iptal edildi"
                    logger.info("tool_call rejected by user name=%s", name)
                    history.append({
                        "role": "user",
                        "content": (
                            f"[SİSTEM ARACI SONUCU - {name}]:\n{result}\n\n"
                            "[ZORUNLU TALİMAT]: Yukarıdaki araç sonucunu KULLAN. "
                            "Cevabını tamamen TÜRKÇE yaz. Kazakça, İngilizce veya başka dil YASAK."
                        ),
                    })
                    continue

            executor = tool_executor.get(name)
            if executor is None:
                result = f"ERROR: unknown tool {name}"
            else:
                try:
                    result = str(executor(**args))
                except Exception as exc:
                    result = f"ERROR: {exc}"
                    logger.warning("tool_call failed name=%s error=%s", name, exc)

            if config.verbose:
                preview = result[:1000] + "..." if len(result) > 1000 else result
                console.print(f"[dim]── ARAÇ SONUCU [{name}] ──\n{preview}[/]")

            # Pass tool result as a user message since native tools are disabled
            # Late Prompt Injection: Türkçe zorunluluğu araç sonucunun tam altına eklenir
            # Böylece model cevap üretmeden hemen önce bu kuralı okur (context fade yok)
            history.append({
                "role": "user",
                "content": (
                    f"[SİSTEM ARACI SONUCU - {name}]:\n{result}\n\n"
                    "[ZORUNLU TALİMAT]: Yukarıdaki araç sonucunu KULLAN. "
                    "Cevabını tamamen TÜRKÇE yaz. Kazakça, İngilizce veya başka dil YASAK."
                ),
            })

    logger.warning("max_turns reached (%d) for model=%s", max_turns, model)
    return f"[free] tur limitine ulasildi (max_turns={max_turns}), islem tamamlanamadan kesildi."
