"""Ollama HTTP client, VRAM/RAM model discipline, and the agentic tool-call loop."""

import json
import logging
import os

import requests

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "free.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("free")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Donanım dogrulamasi (HF model kartlari) sonrasi gercekci registry:
# GLM-5.2 (753B), MiniMax-M3 (428B) ve Kimi-K2.7-Code (1T) 8GB VRAM/32GB RAM'e
# sigmiyor; coder icin Qwen2.5-Coder-7B, research icin Mistral-Nemo, vision
# icin Qwen3-VL-8B ile degistirildi (hepsi Ollama'da tool-calling destekli).
MODEL_REGISTRY = {
    "hf.co/huihui-ai/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF": {"pool": "vram_native", "max_ctx": None, "role": "coder"},
    "hermes3": {"pool": "vram_heavy", "max_ctx": None, "role": "research"},
    "qwen3-vl": {"pool": "vram_native", "max_ctx": None, "role": "vision"},
}

DEFAULT_CODER_MODEL = "hf.co/huihui-ai/Qwen2.5-Coder-7B-Instruct-abliterated-GGUF:Q6_K"
DEFAULT_RESEARCH_MODEL = "hermes3:8b"
DEFAULT_VISION_MODEL = "qwen3-vl:8b"

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

    def unload(self, model_id: str) -> None:
        requests.post(
            f"{self.host}/api/generate",
            json={"model": model_id, "prompt": "", "keep_alive": 0},
            timeout=30,
        )
        logger.info("unloaded model=%s", model_id)

    def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None,
              options: dict | None = None) -> dict:
        payload = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        if options:
            payload["options"] = options
        resp = requests.post(f"{self.host}/api/chat", json=payload, timeout=600)
        resp.raise_for_status()
        return resp.json()


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
    history = messages

    for turn in range(max_turns):
        with console.status(f"[bold cyan]{model} düşünüyor...[/]"):
            # Disable native tools to prevent Ollama from overriding our strict JSON prompt
            response = client.chat(model, history, options=options)
        message = response.get("message", {})
        
        tool_calls = message.get("tool_calls")
        content = message.get("content", "")
        
        # Fallback parser if the model leaks the tool call JSON into content
        if not tool_calls and content:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                try:
                    json_str = content[start:end+1]
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
        
        # Print any conversational text the agent outputted before the tool call
        if content:
            from rich.markdown import Markdown
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
            
            executor = tool_executor.get(name)
            if executor is None:
                result = f"ERROR: unknown tool {name}"
            else:
                try:
                    result = str(executor(**args))
                except Exception as exc:
                    result = f"ERROR: {exc}"
                    logger.warning("tool_call failed name=%s error=%s", name, exc)

            # Pass tool result as a user message since native tools are disabled
            history.append({"role": "user", "content": f"[SİSTEM ARACI SONUCU - {name}]:\n{result}"})

    logger.warning("max_turns reached (%d) for model=%s", max_turns, model)
    return f"[free] tur limitine ulasildi (max_turns={max_turns}), islem tamamlanamadan kesildi."
