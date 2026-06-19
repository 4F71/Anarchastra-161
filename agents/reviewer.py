"""ReviewerAgent — static-analysis-backed code review (reuses the coder model)."""

from agents.core import DEFAULT_CODER_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
from tools.static_analysis import STATIC_ANALYSIS_EXECUTOR, STATIC_ANALYSIS_TOOLS_SCHEMA
from tools.exec_ops import EXEC_TOOLS_SCHEMA, EXEC_TOOL_EXECUTOR
from tools.git_ops import GIT_TOOLS_SCHEMA, GIT_TOOL_EXECUTOR

REVIEWER_SYSTEM_PROMPT = (
    "Sen 'free review' ajanisin. Kod kalitesi denetlemesi yaparsin. Once list_workspace/"
    "read_file ile ilgili dosyalari oku, git_diff/git_log ile son degisiklikleri gor, sonra "
    "run_ruff ve run_mypy araclarini calistirip ciktilarini yorumla. Supheli bir davranisi "
    "run_python ile calistirip dogrula. Bulgularini onem sirasina gore (hata > uyari > stil) "
    "maddeler halinde sun; somut duzeltme onerileri ekle. write_file/edit_file'i sadece "
    "kullanicinin acikca istedigi duzeltmeleri uygularken kullan (kucuk degisiklik icin "
    "edit_file'i tercih et).\n\n"
    "Mevcut araclar: 'read_file', 'write_file', 'edit_file', 'list_workspace', 'run_python', "
    "'git_diff', 'git_log', 'web_search', 'fetch_url', 'whois_lookup', 'run_ruff', 'run_mypy'.\n"
    "Bir arac cagirmak icin SADECE asagidaki JSON formatini ciktinda bulundur, BASKA HICBIR SEY YAZMA:\n"
    "{\n"
    "  \"name\": \"run_ruff\",\n"
    "  \"arguments\": {\"path\": \".\"}\n"
    "}\n"
    "Arac calistiktan sonra sonucunu goreceksin.\n\n"
    "YANITLARINI KESINLIKLE VE SADECE TURKCE DILINDE VERECEKSIN."
)

REVIEWER_TOOLS_SCHEMA = FILE_TOOLS_SCHEMA + STATIC_ANALYSIS_TOOLS_SCHEMA + EXEC_TOOLS_SCHEMA + GIT_TOOLS_SCHEMA
REVIEWER_TOOL_EXECUTOR = {**TOOL_EXECUTOR, **STATIC_ANALYSIS_EXECUTOR, **EXEC_TOOL_EXECUTOR, **GIT_TOOL_EXECUTOR}


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
