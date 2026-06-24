"""Workspace-scoped exact/regex full-text search — complements semantic search_codebase."""

import os
import re

from tools.file_ops import PROJECT_ROOT, resolve_read_path

MAX_RESULTS = 200
SKIP_DIRS = {".git", "__pycache__", ".rag_index", "logs", "venv", ".venv", "node_modules", "free_cli.egg-info"}


def grep_codebase(pattern: str, path: str = ".", max_results: int = 50, ignore_case: bool = False) -> str:
    """Searches file contents for a regex pattern, scoped to path. Returns file:line:text matches."""
    root = resolve_read_path(path)
    capped = max(1, min(max_results, MAX_RESULTS))
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"gecersiz regex deseni: {e}")

    matches: list[str] = []
    targets = [root] if os.path.isfile(root) else None

    if targets is None:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in filenames:
                if len(matches) >= capped:
                    break
                targets_file = os.path.join(dirpath, filename)
                _scan_file(targets_file, regex, matches, capped)
            if len(matches) >= capped:
                break
    else:
        _scan_file(root, regex, matches, capped)

    if not matches:
        return "(eslesme bulunamadi)"
    return "\n".join(matches[:capped])


def _scan_file(filepath: str, regex: re.Pattern, matches: list[str], capped: int) -> None:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                if regex.search(line):
                    rel = os.path.relpath(filepath, PROJECT_ROOT)
                    matches.append(f"{rel}:{lineno}:{line.strip()}")
                    if len(matches) >= capped:
                        return
    except (UnicodeDecodeError, OSError):
        return


GREP_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "grep_codebase",
            "description": (
                "Search file contents for an exact regex pattern across the project (read-only). "
                "Use this instead of search_codebase when you need an exact/literal match "
                "(e.g. a function name, import, or string) rather than semantic similarity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Path relative to the project root to scope the search to. Defaults to the whole project.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max number of matching lines to return (default 50, capped at 200).",
                    },
                    "ignore_case": {
                        "type": "boolean",
                        "description": "Case-insensitive search. Defaults to false.",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]

GREP_TOOL_EXECUTOR = {
    "grep_codebase": grep_codebase,
}
