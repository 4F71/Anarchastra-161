"""Global çalışma zamanı konfigürasyonu — verbose/thinking modu, yazma onayı, air-gapped mod ve denetim izi."""

verbose: bool = False
confirm_writes: bool = False
no_network: bool = False
audit_enabled: bool = False
ctx_override: int | None = None
last_prompt_eval_count: int = 0  # Ollama'dan gelen gercek prompt token sayisi


def toggle_verbose() -> bool:
    global verbose
    verbose = not verbose
    return verbose


def toggle_confirm_writes() -> bool:
    global confirm_writes
    confirm_writes = not confirm_writes
    return confirm_writes


def toggle_no_network() -> bool:
    """Air-gapped modu acar/kapatir. Acilirken denetim izini (audit_enabled) de otomatik acar."""
    global no_network, audit_enabled
    no_network = not no_network
    if no_network:
        audit_enabled = True
    return no_network


def toggle_audit() -> bool:
    global audit_enabled
    audit_enabled = not audit_enabled
    return audit_enabled
