"""Workspace-scoped static analysis tools (ruff, mypy) for the ReviewerAgent."""

import subprocess

from tools.file_ops import WORKSPACE_ROOT, resolve_read_path

TIMEOUT_SECONDS = 60


def _run(cmd: list[str], target: str) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return f"ERROR: {cmd[0]} not installed (pip install -r requirements.txt)"
    except subprocess.TimeoutExpired:
        return f"ERROR: {cmd[0]} timed out after {TIMEOUT_SECONDS}s on {target}"

    output = (proc.stdout + proc.stderr).strip()
    return output or f"{cmd[0]}: no issues found"


def run_ruff(path: str = ".") -> str:
    target = resolve_read_path(path)
    return _run(["ruff", "check", target], path)


def run_mypy(path: str = ".") -> str:
    target = resolve_read_path(path)
    return _run(["mypy", "--ignore-missing-imports", target], path)


STATIC_ANALYSIS_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_ruff",
            "description": "Run ruff (lint) on a file or directory inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root. Defaults to root.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_mypy",
            "description": "Run mypy (static type check) on a file or directory inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root. Defaults to root.",
                    }
                },
                "required": [],
            },
        },
    },
]

STATIC_ANALYSIS_EXECUTOR = {
    "run_ruff": run_ruff,
    "run_mypy": run_mypy,
}
