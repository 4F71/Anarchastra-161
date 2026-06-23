import pytest

from tools.static_analysis import run_mypy, run_pytest, run_ruff


def test_run_ruff_rejects_path_escape():
    with pytest.raises(ValueError):
        run_ruff("../outside.py")


def test_run_mypy_rejects_path_escape():
    with pytest.raises(ValueError):
        run_mypy("../outside.py")


def test_run_pytest_rejects_path_escape():
    with pytest.raises(ValueError):
        run_pytest("../outside.py")
