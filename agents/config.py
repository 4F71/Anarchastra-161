"""Global çalışma zamanı konfigürasyonu — verbose/thinking modu ve yazma onayı."""

verbose: bool = False
confirm_writes: bool = False


def toggle_verbose() -> bool:
    global verbose
    verbose = not verbose
    return verbose


def toggle_confirm_writes() -> bool:
    global confirm_writes
    confirm_writes = not confirm_writes
    return confirm_writes
