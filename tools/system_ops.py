"""Gercek VRAM/RAM olcumu — nvidia-smi ve ollama ps ciktilarini parse eder.

CLAUDE.md'deki MODEL_VRAM_ESTIMATES_GB sabit/tahmini degerlerdir (HF model
kartlarindan); bu modul donanimdan canli okunan gercek degerleri saglar.
"""

import shutil
import subprocess

import psutil

from agents.core import OllamaClient


def get_gpu_status() -> str:
    """nvidia-smi --query-gpu ile VRAM kullanim/toplam (MiB) ve GPU yuk yuzdesini okur."""
    if shutil.which("nvidia-smi") is None:
        return "nvidia-smi bulunamadi (NVIDIA suruculeri kurulu degil veya PATH'te yok)"

    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return f"nvidia-smi calistirilamadi: {exc}"

    lines = []
    for row in out.stdout.strip().splitlines():
        name, used, total, util = (p.strip() for p in row.split(","))
        lines.append(f"{name}: {used}MiB / {total}MiB VRAM kullanimda  ({util}% GPU yuk)")
    return "\n".join(lines) if lines else "GPU bulunamadi"


def get_ram_status() -> str:
    """psutil ile sistem RAM kullanimini okur."""
    vm = psutil.virtual_memory()
    used_gb = (vm.total - vm.available) / (1024 ** 3)
    total_gb = vm.total / (1024 ** 3)
    return f"RAM: {used_gb:.1f}GB / {total_gb:.1f}GB kullanimda  (%{vm.percent})"


def get_loaded_models() -> str:
    """ollama ps karsiligi olan /api/ps ile su an yuklu modelleri ve gercek boyutlarini okur."""
    client = OllamaClient()
    try:
        loaded = client.list_loaded()
    except Exception as exc:
        return f"Ollama'ya ulasilamadi: {exc}"

    if not loaded:
        return "Su anda yuklu model yok."

    lines = []
    for entry in loaded:
        name = entry.get("name") or entry.get("model") or "?"
        size_vram = entry.get("size_vram", 0)
        size = entry.get("size", 0)
        size_gb = size / (1024 ** 3) if size else 0
        vram_gb = size_vram / (1024 ** 3) if size_vram else 0
        lines.append(f"{name}: {size_gb:.1f}GB toplam, ~{vram_gb:.1f}GB VRAM'de")
    return "\n".join(lines)


def run_doctor() -> str:
    """GPU/RAM/yuklu-model durumunun tam raporunu dondurur."""
    sections = [
        "== GPU (nvidia-smi) ==",
        get_gpu_status(),
        "",
        "== RAM ==",
        get_ram_status(),
        "",
        "== Ollama'da Yuklu Modeller ==",
        get_loaded_models(),
    ]
    return "\n".join(sections)
