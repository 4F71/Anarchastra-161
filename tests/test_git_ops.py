from unittest.mock import MagicMock, patch

from tools.git_ops import git_diff, git_log, git_status


def _fake_completed(stdout="", stderr=""):
    proc = MagicMock()
    proc.stdout = stdout
    proc.stderr = stderr
    return proc


def test_git_status_calls_git_status_short():
    with patch("tools.git_ops.subprocess.run", return_value=_fake_completed(" M foo.py\n")) as run:
        result = git_status()
    args = run.call_args[0][0]
    assert args == ["git", "status", "--short"]
    assert result == "M foo.py"


def test_git_diff_scopes_to_path():
    with patch("tools.git_ops.subprocess.run", return_value=_fake_completed("diff --git ...")) as run:
        git_diff("agents/core.py")
    args = run.call_args[0][0]
    assert args == ["git", "diff", "--", "agents/core.py"]


def test_git_log_caps_max_count():
    with patch("tools.git_ops.subprocess.run", return_value=_fake_completed("abc123 commit")) as run:
        git_log(n=999)
    args = run.call_args[0][0]
    assert args == ["git", "log", "-50", "--oneline"]


def test_empty_output_falls_back_to_placeholder():
    with patch("tools.git_ops.subprocess.run", return_value=_fake_completed("", "")):
        assert git_status() == "(degisiklik yok)"
