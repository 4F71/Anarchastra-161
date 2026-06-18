"""ReviewerAgent — static-analysis-backed code review (reuses the coder model)."""

from agents.core import DEFAULT_CODER_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
from tools.static_analysis import STATIC_ANALYSIS_EXECUTOR, STATIC_ANALYSIS_TOOLS_SCHEMA

REVIEWER_SYSTEM_PROMPT = (
    "Sen 'free review' ajanisin. Kod kalitesi denetlemesi yaparsin. Once list_workspace/"
    "read_file ile ilgili dosyalari oku, sonra run_ruff ve run_mypy araclarini calistirip "
    "ciktilarini yorumla. Bulgularini onem sirasina gore (hata > uyari > stil) maddeler "
    "halinde sun; somut duzeltme onerileri ekle. write_file'i sadece kullanicinin acikca "
    "istedigi duzeltmeleri uygularken kullan."
)

REVIEWER_TOOLS_SCHEMA = FILE_TOOLS_SCHEMA + STATIC_ANALYSIS_TOOLS_SCHEMA
REVIEWER_TOOL_EXECUTOR = {**TOOL_EXECUTOR, **STATIC_ANALYSIS_EXECUTOR}


class ReviewerAgent:
    def __init__(self, model: str = DEFAULT_CODER_MODEL, client: OllamaClient | None = None):
        self.model = model
        self.client = client or OllamaClient()
        self.manager = ModelManager(self.client)

    def run(self, prompt: str) -> str:
        self.manager.ensure_loaded(self.model)
        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return run_agent_loop(
            self.client,
            self.model,
            messages,
            tools_schema=REVIEWER_TOOLS_SCHEMA,
            tool_executor=REVIEWER_TOOL_EXECUTOR,
        )
