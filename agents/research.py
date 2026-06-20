"""ResearchAgent — deep code review and architecture analysis."""

from agents.core import DEFAULT_RESEARCH_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
from tools.rag_ops import RAG_TOOLS_SCHEMA, RAG_TOOL_EXECUTOR

RESEARCH_TOOLS_SCHEMA = FILE_TOOLS_SCHEMA + RAG_TOOLS_SCHEMA
RESEARCH_TOOL_EXECUTOR = {**TOOL_EXECUTOR, **RAG_TOOL_EXECUTOR}

RESEARCH_SYSTEM_PROMPT = (
    "Sen 'free research' ajanısın. Kullanıcının sorusunu doğrudan araştıran OTONOM bir ajansın.\n\n"
    "KURAL 1: Araç çağırmadan ÖNCE HİÇBİR ŞEY YAZMA. İlk çıktın mutlaka bir JSON araç çağrısı olmalı.\n"
    "KURAL 2: ARAÇ SEÇİMİ:\n"
    "  - Domain/alan adı soruları → whois_lookup(domain='example.com') kullan\n"
    "  - Güncel haber/bilgi/teknik sorular → web_search(query='...') kullan\n"
    "  - URL'yi detaylı okumak istiyorsan → fetch_url(url='https://...') kullan\n"
    "  - Bu projenin kod tabanıyla ilgili (mimari, hangi dosyada ne var) sorular → "
    "search_codebase(query='...') kullan\n"
    "KURAL 3: Araç sonucunu aynen kullan. ASLA araç sonucunu yok say veya uydurma!\n"
    "KURAL 4: YANIT YALNIZCA TÜRKÇE.\n\n"
    "Araç çağırma formatı (SADECE BU JSON, başka hiçbir şey yazma):\n"
    "{\n"
    "  \"name\": \"whois_lookup\",\n"
    "  \"arguments\": {\"domain\": \"example.com\"}\n"
    "}\n"
)


class ResearchAgent:
    def __init__(self, model: str = DEFAULT_RESEARCH_MODEL, client: OllamaClient | None = None):
        self.model = model
        self.client = client or OllamaClient()
        self.manager = ModelManager(self.client)

    def run(self, prompt: str) -> str:
        self.manager.ensure_loaded(self.model)
        messages = [
            {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return run_agent_loop(
            self.client,
            self.model,
            messages,
            tools_schema=RESEARCH_TOOLS_SCHEMA,
            tool_executor=RESEARCH_TOOL_EXECUTOR,
        )
