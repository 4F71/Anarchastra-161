"""CoderAgent — code completion and debug/reverse-engineering modes."""

from agents.core import DEFAULT_CODER_MODEL, ModelManager, OllamaClient, run_agent_loop
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
from tools.exec_ops import EXEC_TOOLS_SCHEMA, EXEC_TOOL_EXECUTOR
from tools.git_ops import GIT_TOOLS_SCHEMA, GIT_TOOL_EXECUTOR
from tools.rag_ops import RAG_TOOLS_SCHEMA, RAG_TOOL_EXECUTOR
from tools.memory_ops import MEMORY_TOOLS_SCHEMA, MEMORY_TOOL_EXECUTOR

CODER_TOOLS_SCHEMA = FILE_TOOLS_SCHEMA + EXEC_TOOLS_SCHEMA + GIT_TOOLS_SCHEMA + RAG_TOOLS_SCHEMA + MEMORY_TOOLS_SCHEMA
CODER_TOOL_EXECUTOR = {**TOOL_EXECUTOR, **EXEC_TOOL_EXECUTOR, **GIT_TOOL_EXECUTOR, **RAG_TOOL_EXECUTOR, **MEMORY_TOOL_EXECUTOR}

CODE_SYSTEM_PROMPT = (
    "Sen 'free' otonom kodlama ajanısın. Sadece konuşmakla kalmaz, EYLEM yaparsın! "
    "Mevcut araçlar: 'read_file', 'write_file', 'edit_file', 'list_workspace', 'run_python', "
    "'git_diff', 'git_log', 'git_status', 'web_search', 'fetch_url', 'whois_lookup', 'search_codebase'.\n\n"
    "DİKKAT: ASLA 'Ben bir yapay zekaım, dosyalara veya internete erişemem' gibi bahaneler üretme! "
    "SENİN DOSYALARA VE İNTERNETE ERİŞİMİN VAR! "
    "Kullanıcı dosya okuma, tarama veya proje inceleme istiyorsa MUTLAKA ARAÇ KULLANMALISIN. "
    "Bir şeyin nerede/nasıl uygulandığını bilmiyorsan tek tek dosya okumak yerine önce "
    "search_codebase ile anlamsal arama yap. "
    "Bilmediğin kütüphane, API veya dış kaynak için web_search ile araştırma yap. "
    "Küçük/hedefli bir değişiklik yapacaksan write_file ile dosyanın tamamını yeniden yazmak yerine "
    "edit_file ile sadece ilgili kısmı değiştir. Bir dosya yazdıktan sonra mutlaka run_python ile "
    "çalıştırıp gerçekten çalıştığını doğrula — varsayımda bulunma.\n\n"
    "Bir araç çağırmak için SADECE aşağıdaki JSON formatını çıktunda bulundur, BAŞKA HİÇBİR ŞEY YAZMA:\n"
    "{\n"
    "  \"name\": \"list_workspace\",\n"
    "  \"arguments\": {\"path\": \".\"}\n"
    "}\n"
    "Araç çalıştıktan sonra sonucunu göreceksin. Gördüğün kodları veya raw dosya "
    "içeriklerini KULLANICIYA YAZDIRMA. Sadece özet geç veya gereken değişikliği "
    "write_file/edit_file ile yap.\n\n"
    "YANITLARINI KESİNLİKLE VE SADECE TÜRKÇE DİLİNDE VERECEKSİN. ASLA BAŞKA BİR DİL (KAZAKÇA, İNGİLİZCE VB.) KULLANMA!"
)

DEBUG_SYSTEM_PROMPT = (
    "Sen 'free debug' ajanisin. workspace/ icindeki mevcut dosyalari list_workspace ve "
    "read_file ile inceleyip hatalari tersine muhendislikle (reverse-engineering) "
    "teshis edersin. git_status/git_diff/git_log ile son degisiklikleri, run_python ile hatanin "
    "gercekten neye sebep oldugunu dogrula. Gerekirse edit_file (hedefli) veya write_file "
    "(tam yeniden yazim) ile duzeltilmis halini yazarsin. Bulgularini kisa ve net acikla.\n\n"
    "Mevcut araclar: 'read_file', 'write_file', 'edit_file', 'list_workspace', 'run_python', "
    "'git_diff', 'git_log', 'git_status', 'web_search', 'fetch_url', 'whois_lookup', 'search_codebase'.\n"
    "Bir arac cagirmak icin SADECE asagidaki JSON formatini ciktinda bulundur, BASKA HICBIR SEY YAZMA:\n"
    "{\n"
    "  \"name\": \"list_workspace\",\n"
    "  \"arguments\": {\"path\": \".\"}\n"
    "}\n"
    "Arac calistiktan sonra sonucunu goreceksin.\n\n"
    "YANITLARINI KESINLIKLE VE SADECE TURKCE DILINDE VERECEKSIN."
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
            tools_schema=CODER_TOOLS_SCHEMA,
            tool_executor=CODER_TOOL_EXECUTOR,
        )
