"""free — zero-cost local multi-agent CLI (Ollama-backed)."""

import sys

import click

from agents.coder import CoderAgent
from agents.core import (
    DEFAULT_CODEBASE_MODEL,
    DEFAULT_CODER_MODEL,
    DEFAULT_RESEARCH_MODEL,
    DEFAULT_VISION_MODEL,
    MODEL_REGISTRY,
    MODEL_VRAM_ESTIMATES_GB,
    OllamaClient,
)
from agents.research import ResearchAgent
from agents.reviewer import ReviewerAgent
from agents.vision import VisionAgent
import os
import agents.config as agent_config
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory

console = Console()

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(HISTORY_DIR, exist_ok=True)
HISTORY_PATH = os.path.join(HISTORY_DIR, ".free_history")
MAX_HISTORY_MESSAGES = 20  # sistem promptu disinda tutulacak son mesaj sayisi

def print_splash():
    """Initial splash: copyleft logo + info, side by side."""
    click.clear()

    R = "bold #DC2626"  # kırmızı
    B = "bold white"    # beyaz (iç Ɔ sembolü)

    logo = Text()
    logo.append("   \u25e4\u2588\u2588\u2588\u2588\u25e5   \n", style=R)
    logo.append("  \u2588\u2588    \u2588\u2588  \n", style=R)
    logo.append(" \u2588\u2588 ", style=R)
    logo.append("\u25e4\u2588\u2588\u2588 ", style=B)
    logo.append(" \u2588\u2588 \n", style=R)
    logo.append(" \u2588\u2588 ", style=R)
    logo.append("\u2588\u2588   ", style=B)
    logo.append(" \u2588\u2588 \n", style=R)
    logo.append(" \u2588\u2588 ", style=R)
    logo.append("\u25be\u2588\u2588\u2588 ", style=B)
    logo.append(" \u2588\u2588 \n", style=R)
    logo.append("  \u2588\u2588    \u2588\u2588  \n", style=R)
    logo.append("   \u25be\u2588\u2588\u2588\u2588\u25bf   ", style=R)

    info = Text()
    info.append("free CLI ", style="bold white")
    info.append("v0.1.0\n", style="dim")
    info.append("Yerel Multi-Agent Cowork · ", style="dim")
    info.append("Offline\n\n", style="bold cyan")
    info.append("Coder      ", style="bold")
    info.append("VRAM (8GB)\n", style="dim")
    info.append("Research   ", style="bold")
    info.append("RAM (32GB)\n", style="dim")
    info.append("Vision     ", style="bold")
    info.append("VRAM (8GB)\n\n", style="dim")

    cwd = os.getcwd()
    home = os.path.expanduser("~")
    display_path = ("~" + cwd[len(home):] if cwd.startswith(home) else cwd).replace("/", "\\")
    info.append(display_path, style="dim")

    grid = Table.grid(padding=(0, 2))
    grid.add_column()
    grid.add_column()
    grid.add_row(logo, info)
    console.print(grid)
    console.print()

def _build_info_text() -> Text:
    """Splash sonrası /clear gibi yerlerde gösterilen tek satırlık özet (logo'suz)."""
    info = Text()
    info.append("free CLI ", style="bold white")
    info.append("v0.1.0 · ", style="dim")
    info.append("Yerel Multi-Agent Cowork · ", style="dim")
    info.append("Offline\n", style="bold cyan")

    cwd = os.getcwd()
    home = os.path.expanduser("~")
    display_path = ("~" + cwd[len(home):] if cwd.startswith(home) else cwd).replace("/", "\\")
    info.append(display_path, style="dim")
    return info

def _print_info_line():
    console.print(_build_info_text())
    console.print()

def print_banner():
    click.clear()
    _print_info_line()

def print_result(text: str):
    console.print(Markdown(text))
    console.print()


@click.group(invoke_without_command=True)
@click.pass_context
def free(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(shell)


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
@click.option("--confirm-writes", is_flag=True, help="write_file/edit_file calistirilmadan once onay sor.")
@click.option("--no-network", is_flag=True, help="Air-gapped mod: web araclarini kapat, sadece localhost'a izin ver.")
def code(prompt: str, model: str, confirm_writes: bool, no_network: bool):
    agent_config.confirm_writes = confirm_writes
    agent_config.no_network = no_network
    agent = CoderAgent(model=model)
    try:
        print_result(agent.run(prompt, mode="code"))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
@click.option("--confirm-writes", is_flag=True, help="write_file/edit_file calistirilmadan once onay sor.")
@click.option("--no-network", is_flag=True, help="Air-gapped mod: web araclarini kapat, sadece localhost'a izin ver.")
def debug(prompt: str, model: str, confirm_writes: bool, no_network: bool):
    agent_config.confirm_writes = confirm_writes
    agent_config.no_network = no_network
    agent = CoderAgent(model=model)
    try:
        print_result(agent.run(prompt, mode="debug"))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_RESEARCH_MODEL, show_default=True)
@click.option("--confirm-writes", is_flag=True, help="write_file/edit_file calistirilmadan once onay sor.")
@click.option("--no-network", is_flag=True, help="Air-gapped mod: web araclarini kapat, sadece localhost'a izin ver.")
def research(prompt: str, model: str, confirm_writes: bool, no_network: bool):
    agent_config.confirm_writes = confirm_writes
    agent_config.no_network = no_network
    agent = ResearchAgent(model=model)
    try:
        print_result(agent.run(prompt))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
@click.option("--confirm-writes", is_flag=True, help="write_file/edit_file calistirilmadan once onay sor.")
@click.option("--no-network", is_flag=True, help="Air-gapped mod: web araclarini kapat, sadece localhost'a izin ver.")
def review(prompt: str, model: str, confirm_writes: bool, no_network: bool):
    agent_config.confirm_writes = confirm_writes
    agent_config.no_network = no_network
    agent = ReviewerAgent(model=model)
    try:
        print_result(agent.run(prompt))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.option("--steps", default=1, show_default=True, help="Geri alinacak islem sayisi.")
@click.option("--list", "show_list", is_flag=True, help="Gecmisi listele, geri alma yapma.")
def rollback(steps: int, show_list: bool):
    """write_file/edit_file ile yapilan son degisiklikleri geri alir."""
    from tools.rollback_ops import rollback as do_rollback, rollback_history
    if show_list:
        console.print(rollback_history())
    else:
        console.print(do_rollback(steps))


@free.command()
@click.argument("text")
@click.option("--tag", default="", help="Opsiyonel kisa etiket, orn: 'model-secimi'.")
def remember(text: str, tag: str):
    """Bir karari/notu kalici proje hafizasina kaydeder."""
    from tools.memory_ops import remember as do_remember
    console.print(do_remember(text, tag))


@free.command()
@click.option("--query", default="", help="Aranacak anahtar kelime (bossa son kayitlari listeler).")
@click.option("--n", default=10, show_default=True, help="Gosterilecek maksimum kayit sayisi.")
def memory(query: str, n: int):
    """Kayitli proje kararlarini listeler/arar."""
    from tools.memory_ops import recall
    console.print(recall(query, n))


@free.command()
@click.option("--verify", is_flag=True, help="Hash zincirini dogrula.")
@click.option("--lines", default=10, show_default=True, help="Gosterilecek son kayit sayisi.")
def audit(verify: bool, lines: int):
    """Kriptografik denetim izini gosterir veya dogrular."""
    from tools.audit_ops import audit_tail, verify_chain
    if verify:
        console.print(verify_chain())
    else:
        console.print(audit_tail(lines))


@free.command()
@click.option("--paths", default="", help="Virgülle ayrılmış, indexlenecek dosya yolları (boşsa tüm proje taranır).")
def index(paths: str):
    """Kod tabanını anlamsal arama (search_codebase) için yerel vektör veritabanına indexler."""
    from tools.rag_ops import index_codebase
    with console.status("[bold cyan]Indexleniyor (nomic-embed-text ile)...[/]"):
        result = index_codebase(paths)
    console.print(f"[dim]{result}[/]")


@free.command()
@click.argument("image_path")
@click.argument("prompt")
@click.option("--model", default=DEFAULT_VISION_MODEL, show_default=True)
def vision(image_path: str, prompt: str, model: str):
    agent = VisionAgent(model=model)
    try:
        print_result(agent.run(prompt, image_path))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


from agents.core import ModelManager
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR, WORKSPACE_ROOT, read_image_b64
from agents.coder import CODE_SYSTEM_PROMPT, CODER_TOOLS_SCHEMA, CODER_TOOL_EXECUTOR
from agents.research import RESEARCH_SYSTEM_PROMPT, RESEARCH_TOOLS_SCHEMA, RESEARCH_TOOL_EXECUTOR
from agents.vision import VISION_SYSTEM_PROMPT
from agents.core import run_agent_loop
import json
import time
from PIL import ImageGrab
from prompt_toolkit.key_binding import KeyBindings

CODEBASE_SYSTEM_PROMPT = (
    "Sen bu projenin ('free' CLI, Stirner-73) KENDİ KOD TABANINI analiz eden OTONOM bir ajansın.\n\n"
    "KURAL 1: Araç çağırmadan ÖNCE HİÇBİR ŞEY YAZMA. İlk çıktın mutlaka bir JSON araç çağrısı olmalı.\n"
    "KURAL 2: Önce search_codebase(query='...') ile ilgili kod parçalarını bul. Bulduğun chunk yetersizse "
    "ilgili dosyayı read_file(path='...') ile tam olarak oku.\n"
    "KURAL 3: whois_lookup/web_search/fetch_url bu görev için KULLANILMAZ — soru bu projenin kendi "
    "kaynak koduyla ilgili, dış dünyayla değil.\n"
    "KURAL 4: Araç sonucunu aynen kullan, uydurma. Dosya yolunu ve fonksiyon/sınıf adlarını tam ver.\n"
    "KURAL 5: YANIT YALNIZCA TÜRKÇE.\n\n"
    "Araç çağırma formatı (SADECE BU JSON, başka hiçbir şey yazma):\n"
    "{\n"
    "  \"name\": \"search_codebase\",\n"
    "  \"arguments\": {\"query\": \"...\"}\n"
    "}\n"
)

def route_prompt(client: OllamaClient, current_model: str, user_prompt: str) -> str:
    sys_msg = (
        "You are a strict intent classifier. Return ONLY a valid JSON object with a single key 'intent', "
        "one of 'code', 'codebase', or 'research'. "
        "All agents can call tools, so the mere mention of a tool name does NOT by itself determine intent — "
        "focus on what the user ultimately wants. "
        "If the user wants code WRITTEN, MODIFIED, or DEBUGGED (new files, edits, fixes, running scripts), intent is 'code'. "
        "If the user wants something about THIS project's OWN codebase EXPLAINED, FOUND, or ANALYZED "
        "(how an existing function/class/file in this repo works, where something is implemented, architecture "
        "questions about this project), intent is 'codebase'. "
        "If the user wants general information, web research, or abstract explanations unrelated to this "
        "project's own source code (like physics, history, current events), intent is 'research'. "
        "Example output: {\"intent\": \"code\"}, {\"intent\": \"codebase\"}, or {\"intent\": \"research\"}"
    )
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": user_prompt}
    ]
    try:
        options = {"temperature": 0.0}
        with console.status("[dim]Yönlendiriliyor (Router)...[/]"):
            response = client.chat(current_model, messages, format="json", options=options)
            content = response.get("message", {}).get("content", "{}")
            parsed = json.loads(content)
            return parsed.get("intent", "code").lower()
    except Exception as exc:
        # Fallback to code
        return "code"

def capture_snipping_tool(save_path: str) -> bool:
    """Terminali minimize edip ms-screenclip başlatır, seçim sonrası geri döner."""
    import ctypes
    SW_MINIMIZE = 6
    SW_RESTORE  = 9

    # Terminali minimize et (başka ekranlar görünsün)
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
    time.sleep(0.3)

    # Panoyu temizle (eski resim kalmasın)
    try:
        ctypes.windll.user32.OpenClipboard(None)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    except Exception:
        pass

    # Ekran Alıntısı Aracı'nı başlat
    os.system("start ms-screenclip:")

    console.print("\n[bold cyan]📸 Ekran Alıntısı Aracı başlatıldı.[/] [dim]Analiz edilecek alanı seçin. İptal için Ctrl+C.[/]")

    try:
        for _ in range(60):  # 30 saniye bekleme
            time.sleep(0.5)
            img = ImageGrab.grabclipboard()
            if img is not None and hasattr(img, "save"):
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                img.save(save_path)
                ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
                return True
    except KeyboardInterrupt:
        console.print("\n[dim]İptal edildi.[/]")

    # Süre doldu veya iptal edildi — terminali geri getir
    ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
    return False


@free.command()
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
@click.option("--confirm-writes", is_flag=True, help="write_file/edit_file calistirilmadan once onay sor.")
@click.option("--no-network", is_flag=True, help="Air-gapped mod: web araclarini kapat, sadece localhost'a izin ver.")
def shell(model: str, confirm_writes: bool, no_network: bool):
    """Sürekli calisan, etkilesimli REPL modunu baslatir."""
    agent_config.confirm_writes = confirm_writes
    agent_config.no_network = no_network
    client = OllamaClient()
    manager = ModelManager(client)
    
    try:
        manager.ensure_loaded(model)
    except Exception as exc:
        console.print(f"[bold red]Ollama hatasi:[/] {exc}")
        return

    messages = [{"role": "system", "content": CODE_SYSTEM_PROMPT}]

    # Key bindings
    kb = KeyBindings()

    @kb.add('f2')
    def toggle_verbose(event):
        agent_config.toggle_verbose()
        event.app.invalidate()  # toolbar'u yenile

    def bottom_toolbar():
        mode = " 🔍 ON" if agent_config.verbose else ""
        confirm_mode = " ⚠️ ON" if agent_config.confirm_writes else ""
        airgap_mode = " 🔒 ON" if agent_config.no_network else ""
        return HTML(
            f' <b>?</b> help  <b>/exit</b> quit  <b>/clear</b> clear  '
            f'<b>F2</b> thinking{mode}  <b>/confirm</b> writes{confirm_mode}  '
            f'<b>/airgap</b> network{airgap_mode} '
        )

    placeholder = HTML('<style fg="#5f5f5f">Bana ne yaptırmak istersin? · yardım için "?"</style>')

    session = PromptSession(key_bindings=kb, history=FileHistory(HISTORY_PATH))
    print_splash()
    pinned_model = None

    def _memory_context() -> str:
        from tools.memory_ops import recall
        recent = recall(n=5)
        if "bos" in recent or "bulunamadi" in recent:
            return ""
        return "\n\nBu projede daha once alinan bazi kararlar:\n" + recent

    while True:
        try:
            prompt = session.prompt("❯ ", bottom_toolbar=bottom_toolbar, placeholder=placeholder)
        except (KeyboardInterrupt, EOFError):
            break
            
        prompt = prompt.strip()
        if not prompt:
            continue
            
        if prompt == "/exit":
            break
        elif prompt == "/clear":
            click.clear()
            print_banner()
            continue
        elif prompt == "/verbose":
            state = agent_config.toggle_verbose()
            label = "AÇIK ✅" if state else "KAPALI ❌"
            console.print(f"[dim]🔍 Thinking log: {label}[/]")
            continue
        elif prompt == "/confirm":
            state = agent_config.toggle_confirm_writes()
            label = "AÇIK ✅" if state else "KAPALI ❌"
            console.print(f"[dim]⚠️  write_file/edit_file onayi: {label}[/]")
            continue
        elif prompt == "/airgap":
            state = agent_config.toggle_no_network()
            label = "AÇIK 🔒" if state else "KAPALI 🌐"
            console.print(f"[dim]Air-gapped mod: {label}[/]")
            continue
        elif prompt.startswith("/remember"):
            from tools.memory_ops import remember as do_remember
            text = prompt[len("/remember"):].strip()
            if not text:
                console.print("[dim]Kullanim: /remember <kaydedilecek karar/not>[/]")
            else:
                console.print(f"[dim]🧠 {do_remember(text)}[/]")
                messages[0]["content"] += f"\n[Hatirlanan: {text}]"
            continue
        elif prompt.startswith("/memory"):
            from tools.memory_ops import recall
            arg = prompt[len("/memory"):].strip()
            n = int(arg) if arg.isdigit() else 10
            console.print(f"[dim]{recall(n=n)}[/]")
            continue
        elif prompt.startswith("/audit"):
            from tools.audit_ops import audit_tail, verify_chain
            arg = prompt[len("/audit"):].strip()
            if arg == "verify":
                console.print(f"[dim]{verify_chain()}[/]")
            else:
                console.print(f"[dim]{audit_tail()}[/]")
            continue
        elif prompt == "/save":
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"session_{ts}.md"
            save_path = os.path.join(WORKSPACE_ROOT, save_name)
            os.makedirs(WORKSPACE_ROOT, exist_ok=True)
            lines = []
            for m in messages:
                if m["role"] == "system" or not m.get("content"):
                    continue
                lines.append(f"### {m['role']}\n\n{m['content']}\n")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            console.print(f"[dim]💾 Kaydedildi: workspace/{save_name}[/]")
            continue
        elif prompt.startswith("/rollback"):
            from tools.rollback_ops import rollback as do_rollback, rollback_history
            arg = prompt[len("/rollback"):].strip()
            if arg == "list":
                console.print(f"[dim]{rollback_history()}[/]")
            else:
                steps = int(arg) if arg.isdigit() else 1
                console.print(f"[dim]↩️  {do_rollback(steps)}[/]")
            continue
        elif prompt.startswith("/index"):
            from tools.rag_ops import index_codebase
            target_paths = prompt[len("/index"):].strip()
            with console.status("[bold cyan]Indexleniyor (nomic-embed-text ile)...[/]"):
                result = index_codebase(target_paths)
            console.print(f"[dim]📚 {result}[/]")
            continue
        elif prompt.startswith("/model"):
            target = prompt[len("/model"):].strip()
            if not target:
                pin_status = f" (SABITLENMIS)" if pinned_model else ""
                console.print(f"[bold cyan]Aktif Model:[/] {model}{pin_status}")
                try:
                    models = client.list_models()
                    if models:
                        console.print("\n[dim]Kullanılabilir Modeller:[/]")
                        for m in models:
                            m_name = m.get("name", "Bilinmeyen")
                            marker = "[bold green]👉[/]" if m_name == model else "  "
                            console.print(f"{marker} {m_name}")
                except Exception as e:
                    console.print(f"[dim]Modeller listelenemedi: {e}[/]")
                continue
            try:
                if target == "clear":
                    pinned_model = None
                    console.print("[dim]🔄 Model sabitlemesi kaldirildi, otomatik secim (router) devrede.[/]")
                    continue
                manager.ensure_loaded(target)
                model = target
                pinned_model = target
                console.print(f"[dim]🔄 Model manuel olarak sabitlendi: {model} (kaldırmak için: /model clear)[/]")
            except Exception as e:
                console.print(f"[bold red]Model yuklenemedi:[/] {e}")
            continue
        elif prompt == "?":
            console.print(
                "[dim]Komutlar: /exit, /clear, /verbose (thinking log), /confirm (yazma onayi), "
                "/save (oturumu kaydet), /index [yollar] (kod tabanini indexle), "
                "/rollback [N|list] (son N write_file/edit_file islemini geri al), "
                "/airgap (air-gapped mod ac/kapa), /remember <metin> (karar kaydet), "
                "/memory [N] (kayitli kararlari listele), /audit [verify] (denetim izini goster/dogrula), "
                "/model <isim> (manuel model degisimi), /look <soru>, "
                "veya direkt yaz.[/]"
            )
            continue
            
        is_vision = False
        image_b64 = None
        if prompt.startswith("/look"):
            import tempfile
            prompt_text = prompt[5:].strip() or "Bu görüntüde ne görüyorsun? Hataları veya ilginç noktaları Türkçe açıkla."
            temp_path = tempfile.mktemp(suffix=".png", prefix="free_look_")
            if capture_snipping_tool(temp_path):
                try:
                    image_b64 = read_image_b64(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                prompt = prompt_text
                is_vision = True
            else:
                console.print("[bold red]Ekran alıntısı alınamadı veya iptal edildi.[/]")
                continue

        image_message = None
        if is_vision:
            image_message = {"role": "user", "content": prompt, "images": [image_b64]}
            messages.append(image_message)
            target_model = DEFAULT_VISION_MODEL
            intent = "vision"
        else:
            messages.append({"role": "user", "content": prompt})
            if pinned_model:
                intent = "pinned"
                target_model = pinned_model
            else:
                intent = route_prompt(client, model, prompt)
                if intent == "codebase":
                    target_model = DEFAULT_CODEBASE_MODEL
                elif intent == "research":
                    target_model = DEFAULT_RESEARCH_MODEL
                else:
                    target_model = DEFAULT_CODER_MODEL
        
        if target_model != model:
            console.print(f"[dim]🔄 Ajan değiştiriliyor: {intent.upper()} ({target_model})[/]")
            try:
                manager.ensure_loaded(target_model)
                model = target_model
            except Exception as e:
                console.print(f"[bold red]Model yüklenemedi:[/] {e}")
                
        # Swap system prompt + tool set based on current model
        if model == DEFAULT_CODEBASE_MODEL and not pinned_model:
            messages[0] = {"role": "system", "content": CODEBASE_SYSTEM_PROMPT}
            tools_schema, tool_executor = RESEARCH_TOOLS_SCHEMA, RESEARCH_TOOL_EXECUTOR
        elif model == DEFAULT_RESEARCH_MODEL and not pinned_model:
            messages[0] = {"role": "system", "content": RESEARCH_SYSTEM_PROMPT}
            tools_schema, tool_executor = FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
        elif model == DEFAULT_VISION_MODEL and not pinned_model:
            messages[0] = {"role": "system", "content": VISION_SYSTEM_PROMPT}
            tools_schema, tool_executor = FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
        else:
            messages[0] = {"role": "system", "content": CODE_SYSTEM_PROMPT}
            tools_schema, tool_executor = CODER_TOOLS_SCHEMA, CODER_TOOL_EXECUTOR

        messages[0]["content"] += _memory_context()

        try:
            result = run_agent_loop(
                client,
                model,
                messages,
                tools_schema=tools_schema,
                tool_executor=tool_executor
            )
        except KeyboardInterrupt:
            console.print("\n[dim]İptal edildi.[/]")
            continue
        print_result(result)

        # Goruntu base64'unu history'den cikar — yoksa her turn'da tekrar gonderilir
        if image_message is not None:
            image_message.pop("images", None)

        # Mesaj gecmisini sinirla (sistem promptu + son MAX_HISTORY_MESSAGES mesaj)
        if len(messages) > MAX_HISTORY_MESSAGES + 1:
            messages[:] = [messages[0]] + messages[-MAX_HISTORY_MESSAGES:]


@free.command()
def status():
    client = OllamaClient()
    try:
        loaded = client.list_loaded()
    except Exception as exc:
        click.echo(f"[free] Ollama'ya ulasilamadi: {exc}")
        return

    if not loaded:
        click.echo("Yuklu model yok.")
        return

    for entry in loaded:
        name = entry.get("name") or entry.get("model") or "?"
        base = name.split(":")[0]
        pool = MODEL_REGISTRY.get(base, {}).get("pool", "bilinmiyor")
        vram = MODEL_VRAM_ESTIMATES_GB.get(base)
        vram_str = f"~{vram}GB VRAM" if vram else "VRAM tahmini yok"
        click.echo(f"{name}  [{pool}]  {vram_str}")


@free.command()
@click.option("--lines", default=30, show_default=True, help="Gosterilecek son satir sayisi.")
@click.option("--tool-calls-only", is_flag=True, help="Sadece tool_call satirlarini goster.")
def log(lines: int, tool_calls_only: bool):
    """free.log dosyasini bicimli sekilde gosterir."""
    from agents.core import LOG_PATH
    if not os.path.exists(LOG_PATH):
        click.echo("Henuz log yok.")
        return
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    if tool_calls_only:
        all_lines = [l for l in all_lines if "tool_call" in l]
    for line in all_lines[-lines:]:
        console.print(line.rstrip())


@free.command()
def models():
    """Registry'deki modelleri ve Ollama'da cekilip cekilmedigini gosterir."""
    client = OllamaClient()
    try:
        pulled = {m.get("name") for m in client.list_models()}
    except Exception as exc:
        click.echo(f"[free] Ollama'ya ulasilamadi: {exc}")
        return

    targets = [
        (DEFAULT_CODER_MODEL, "coder"),
        (DEFAULT_RESEARCH_MODEL, "research"),
        (DEFAULT_VISION_MODEL, "vision"),
    ]
    for full_name, role in targets:
        info = MODEL_REGISTRY.get(full_name.split(":")[0], {})
        pool = info.get("pool", "bilinmiyor")
        if full_name in pulled:
            status_str = "[green]cekilmis[/]"
        else:
            status_str = f"[red]cekilmemis -> ollama pull {full_name}[/]"
        console.print(f"{full_name}  [{role}/{pool}]  {status_str}")


def cli_main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    free()


if __name__ == "__main__":
    cli_main()
