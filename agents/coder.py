"""CoderAgent — code completion and debug/reverse-engineering modes."""

from agents.core import DEFAULT_CODER_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR

CODE_SYSTEM_PROMPT = (
    "Sen 'free' otonom kodlama ajanısın. Sadece konuşmakla kalmaz, EYLEM yaparsın! "
    "Mevcut araçlar: 'read_file', 'write_file', 'list_workspace'.\n\n"
    "DİKKAT: ASLA 'Ben bir yapay zekayım, dosyalara erişemem' gibi bahaneler üretme! "
    "SENİN DOSYALARA ERİŞİMİN VAR! Eğer kullanıcı dosya okuma, tarama veya proje inceleme "
    "istiyorsa, MUTLAKA ARAÇ KULLANMALISIN. Ancak 'sen kimsin' gibi sadece sohbete dayalı "
    "sorular soruyorsa normal cevap verebilirsin.\n\n"
    "Bir araç çağırmak için SADECE aşağıdaki JSON formatını çıktında bulundur, BAŞKA HİÇBİR ŞEY YAZMA:\n"
    "{\n"
    "  \"name\": \"list_workspace\",\n"
    "  \"arguments\": {\"path\": \".\"}\n"
    "}\n"
    "Araç çalıştıktan sonra sonucunu göreceksin. Gördüğün kodları veya raw dosya "
    "içeriklerini KULLANICIYA YAZDIRMA. Sadece özet geç veya gereken değişikliği "
    "write_file ile yap."
)

DEBUG_SYSTEM_PROMPT = (
    "Sen 'free debug' ajanisin. workspace/ icindeki mevcut dosyalari list_workspace ve "
    "read_file ile inceleyip hatalari tersine muhendislikle (reverse-engineering) "
    "teshis edersin. Gerekirse write_file ile duzeltilmis halini yazarsin. Bulgularini "
    "kisa ve net acikla."
)


class CoderAgent:
    def __init__(self, model: str = DEFAULT_CODER_MODEL, client: OllamaClient | None = None):
        self.model = model
        self.client = client or OllamaClient()
        self.manager = ModelManager(self.client)

    def run(self, prompt: str, mode: str = "code") -> str:
        system_prompt = DEBUG_SYSTEM_PROMPT if mode == "debug" else CODE_SYSTEM_PROMPT
        self.manager.ensure_loaded(self.model)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        return run_agent_loop(
            self.client,
            self.model,
            messages,
            tools_schema=FILE_TOOLS_SCHEMA,
            tool_executor=TOOL_EXECUTOR,
        )
