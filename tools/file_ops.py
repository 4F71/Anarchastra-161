"""Workspace-scoped file tools exposed to agents via Ollama tool-calling."""

import base64
import os

WORKSPACE_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "workspace")
)
PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..")
)

def resolve_read_path(path: str) -> str:
    # Okuma islemleri tum projede (PROJECT_ROOT) yapilabilir.
    target = os.path.realpath(os.path.join(PROJECT_ROOT, path))
    if os.path.commonpath([target, PROJECT_ROOT]) != PROJECT_ROOT:
        raise ValueError(f"read path escapes project root: {path}")
    return target

def resolve_write_path(path: str) -> str:
    # Yazma islemleri SADECE workspace icinde yapilabilir! (Guvenlik)
    target = os.path.realpath(os.path.join(WORKSPACE_ROOT, path))
    if os.path.commonpath([target, WORKSPACE_ROOT]) != WORKSPACE_ROOT:
        raise ValueError(f"write path escapes workspace sandbox: {path}")
    return target


def read_file(path: str) -> str:
    target = resolve_read_path(path)
    if not os.path.isfile(target):
        raise ValueError(f"file not found: {path}")
    with open(target, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    target = resolve_write_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} bytes to {path}"


def list_workspace(path: str = ".") -> list[str]:
    target = resolve_read_path(path)
    if not os.path.isdir(target):
        raise ValueError(f"not a directory: {path}")
    return sorted(os.listdir(target))


def read_image_b64(path: str) -> str:
    target = resolve_path(path)
    if not os.path.isfile(target):
        raise ValueError(f"file not found: {path}")
    with open(target, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


FILE_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file's contents from the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write (overwrite) a text file inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace root.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full text content to write.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_workspace",
            "description": "List files/directories inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to the workspace root. Defaults to root.",
                    }
                },
                "required": [],
            },
        },
    },
]

TOOL_EXECUTOR = {
    "read_file": read_file,
    "write_file": write_file,
    "list_workspace": list_workspace,
}
