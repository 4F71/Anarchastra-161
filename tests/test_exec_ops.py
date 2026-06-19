import pytest

from tools.exec_ops import run_python


def test_run_python_rejects_path_escape():
    with pytest.raises(ValueError):
        run_python("../outside.py")


def test_run_python_rejects_missing_file():
    with pytest.raises(ValueError):
        run_python("definitely_does_not_exist.py")
