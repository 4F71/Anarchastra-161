"""free — zero-cost local multi-agent CLI (Ollama-backed)."""

import sys

import click

from agents.coder import CoderAgent
from agents.core import (
    DEFAULT_CODER_MODEL,
    DEFAULT_RESEARCH_MODEL,
    DEFAULT_VISION_MODEL,
    MODEL_REGISTRY,
    OllamaClient,
)
from agents.research import ResearchAgent
from agents.reviewer import ReviewerAgent
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

console = Console()

LOGO = """[bold red]
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣧⣶⣶⣶⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣾⢿⣿⣿⣿⣏⠉⠉⠛⠛⠿⣷⣕⠀⠀⠀⠀⠀⠀⢀⡀
⠀⠀⠀⠀⣠⣾⢝⠄⢀⣿⡿⠻⣿⣄⠀⠀⠀⠀⠈⢿⣧⡀⣀⣤⡾⠀⠀⠀
⠀⠀⠀⢰⣿⡡⠁⠀⠀⣿⡇⠀⠸⣿⣾⡆⠀⠀⣀⣤⣿⣿⠋⠁⠀⠀⠀⠀
⠀⠀⢀⣷⣿⠃⠀⠀⢸⣿⡇⠀⠀⠹⣿⣷⣴⡾⠟⠉⠸⣿⡇⠀⠀⠀⠀⠀
⠀⠀⢸⣿⠗⡀⠀⠀⢸⣿⠃⣠⣶⣿⠿⢿⣿⡀⠀⠀⢀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠘⡿⡄⣇⠀⣀⣾⣿⡿⠟⠋⠁⠀⠈⢻⣷⣆⡄⢸⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⢻⣷⣿⣿⠿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠻⣿⣷⣿⡟⠀⠀⠀⠀⠀⠀
⢀⣰⣾⣿⠿⣿⣿⣾⣿⠇⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣅⠀⠀⠀⠀⠀⠀
⠀⠰⠊⠁⠀⠙⠪⣿⣿⣶⣤⣄⣀⣀⣀⣤⣶⣿⠟⠋⠙⢿⣷⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣿⡟⠺⠭⠭⠿⠿⠿⠟⠋⠁⠀⠀⠀⠀⠙⠏⣦⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]"""

def print_banner():
    table = Table.grid(padding=2)
    table.add_column()
    table.add_column()
    
    info = Text()
    info.append("\n\n")
    info.append("free CLI ", style="bold white")
    info.append("v0.1.0\n", style="dim")
    info.append("Ollama tabanli yerel multi-agent arac · ", style="dim")
    info.append("Offline\n", style="bold cyan")
    cwd = os.path.basename(os.getcwd())
    info.append(f"~/{cwd}", style="dim")
    
    table.add_row(LOGO, info)
    
    console.print("\n")
    console.rule(style="dim")
    console.print(table)
    console.rule(style="dim")
    console.print("\n    [dim]Terminal REPL Session Started...[/]\n")

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
def code(prompt: str, model: str):
    agent = CoderAgent(model=model)
    try:
        print_result(agent.run(prompt, mode="code"))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
def debug(prompt: str, model: str):
    agent = CoderAgent(model=model)
    try:
        print_result(agent.run(prompt, mode="debug"))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_RESEARCH_MODEL, show_default=True)
def research(prompt: str, model: str):
    agent = ResearchAgent(model=model)
    try:
        print_result(agent.run(prompt))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


@free.command()
@click.argument("prompt")
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
def review(prompt: str, model: str):
    agent = ReviewerAgent(model=model)
    try:
        print_result(agent.run(prompt))
    except KeyboardInterrupt:
        click.echo("\n[free] durduruldu.")


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
from tools.file_ops import FILE_TOOLS_SCHEMA, TOOL_EXECUTOR
from agents.coder import CODE_SYSTEM_PROMPT
from agents.core import run_agent_loop

@free.command()
@click.option("--model", default=DEFAULT_CODER_MODEL, show_default=True)
def shell(model: str):
    """Sürekli calisan, etkilesimli REPL modunu baslatir."""
    client = OllamaClient()
    manager = ModelManager(client)
    
    try:
        manager.ensure_loaded(model)
    except Exception as exc:
        console.print(f"[bold red]Ollama hatasi:[/] {exc}")
        return

    messages = [{"role": "system", "content": CODE_SYSTEM_PROMPT}]
    
    def bottom_toolbar():
        return HTML(' <b>?</b> for help  <b>/exit</b> to quit  <b>/clear</b> to clear screen ')

    session = PromptSession()
    print_banner()

    while True:
        try:
            prompt = session.prompt("❯ ", bottom_toolbar=bottom_toolbar)
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
        elif prompt == "?":
            console.print("[dim]Commands: /exit, /clear, or just type a prompt to chat with the agent.[/]")
            continue
            
        messages.append({"role": "user", "content": prompt})
        
        result = run_agent_loop(
            client,
            model,
            messages,
            tools_schema=FILE_TOOLS_SCHEMA,
            tool_executor=TOOL_EXECUTOR
        )
        print_result(result)


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
        click.echo(f"{name}  [{pool}]")


def cli_main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    free()


if __name__ == "__main__":
    cli_main()
