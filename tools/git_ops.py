"""Read-only git tools — gives agents recent-change context without touching history."""

import subprocess

from tools.file_ops import PROJECT_ROOT

TIMEOUT_SECONDS = 15


def _run_git(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git"] + args, cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return "ERROR: git not installed"
    except subprocess.TimeoutExpired:
        return f"ERROR: git timed out after {TIMEOUT_SECONDS}s"

    output = (proc.stdout + proc.stderr).strip()
    return output or "(degisiklik yok)"


def git_diff(path: str = "") -> str:
    """Shows unstaged changes, optionally scoped to one path."""
    args = ["diff"]
    if path:
        args += ["--", path]
    return _run_git(args)


def git_log(path: str = "", max_count: int = 10) -> str:
    """Shows recent commit history, optionally scoped to one path."""
    capped = max(1, min(max_count, 50))
    args = ["log", f"-{capped}", "--oneline"]
    if path:
        args += ["--", path]
    return _run_git(args)


GIT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show unstaged git changes in the project (read-only). Use to see what was just edited.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Optional path (relative to project root) to scope the diff to.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Show recent commit history (read-only, oneline format).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Optional path (relative to project root) to scope the log to.",
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Max number of commits to show (default 10, capped at 50).",
                    },
                },
                "required": [],
            },
        },
    },
]

GIT_TOOL_EXECUTOR = {
    "git_diff": git_diff,
    "git_log": git_log,
}
