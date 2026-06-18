"""ResearchAgent — deep code review and architecture analysis."""

from agents.core import DEFAULT_RESEARCH_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR

RESEARCH_SYSTEM_PROMPT = (
    "Sen 'free research' ajanısın. Otonom bir araştırmacısın. Kullanıcıya 'sen oku', 'sen yap' "
    "DİYEMEZSİN! KENDİN YAPMAK ZORUNDASIN! Projeyi incelemek için read_file ve list_workspace "
    "araçlarını KULLANMALISIN.\n\n"
    "DİKKAT: ASLA 'Ben bir yapay zekayım, dosyalara erişemem' deme! SENİN DOSYALARA ERİŞİMİN VAR! "
    "Araç kullanmak için SADECE aşağıdaki JSON formatını çıktında bulundur. "
    "Başka HİÇBİR ŞEY YAZMA:\n"
    "{\n"
    "  \"name\": \"list_workspace\",\n"
    "  \"arguments\": {\"path\": \".\"}\n"
    "}\n"
    "Araçları arka arkaya çağırarak dosyaları oku. Okuduğun raw dosyaları veya kodları "
    "KULLANICIYA YAZDIRMA. Sadece kendi içinde analiz et ve işin bitince "
    "kapsamlı bir raporu write_file aracı ile kaydet!"
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
            tools_schema=FILE_TOOLS_SCHEMA,
            tool_executor=TOOL_EXECUTOR,
        )
