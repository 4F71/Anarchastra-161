from unittest.mock import MagicMock, patch

from tools.system_ops import get_gpu_status, get_loaded_models, get_ram_status, run_doctor


def test_get_gpu_status_reports_missing_nvidia_smi():
    with patch("tools.system_ops.shutil.which", return_value=None):
        result = get_gpu_status()
    assert "nvidia-smi bulunamadi" in result


def test_get_gpu_status_parses_csv_output():
    fake_run = MagicMock()
    fake_run.stdout = "NVIDIA RTX 4070, 4096, 8192, 55\n"
    with patch("tools.system_ops.shutil.which", return_value="/usr/bin/nvidia-smi"), \
         patch("tools.system_ops.subprocess.run", return_value=fake_run):
        result = get_gpu_status()
    assert "4096MiB / 8192MiB" in result
    assert "55% GPU yuk" in result


def test_get_ram_status_formats_usage():
    fake_vm = MagicMock(total=32 * 1024 ** 3, available=16 * 1024 ** 3, percent=50.0)
    with patch("tools.system_ops.psutil.virtual_memory", return_value=fake_vm):
        result = get_ram_status()
    assert "16.0GB / 32.0GB" in result


def test_get_loaded_models_reports_none_loaded():
    with patch("tools.system_ops.OllamaClient") as MockClient:
        MockClient.return_value.list_loaded.return_value = []
        result = get_loaded_models()
    assert "yuklu model yok" in result


def test_get_loaded_models_formats_sizes():
    with patch("tools.system_ops.OllamaClient") as MockClient:
        MockClient.return_value.list_loaded.return_value = [
            {"name": "qwen2.5-coder:7b", "size": 6 * 1024 ** 3, "size_vram": 5 * 1024 ** 3}
        ]
        result = get_loaded_models()
    assert "qwen2.5-coder:7b" in result
    assert "6.0GB toplam" in result


def test_run_doctor_includes_all_sections():
    with patch("tools.system_ops.get_gpu_status", return_value="gpu-ok"), \
         patch("tools.system_ops.get_ram_status", return_value="ram-ok"), \
         patch("tools.system_ops.get_loaded_models", return_value="models-ok"):
        result = run_doctor()
    assert "gpu-ok" in result
    assert "ram-ok" in result
    assert "models-ok" in result
