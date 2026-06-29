"""scaffold_ops — sablon uretimi."""

import os
import tempfile
import tools.scaffold_ops as scaffold_module


def test_scaffold_generic(tmp_path):
    original = scaffold_module.WORKSPACE_ROOT if hasattr(scaffold_module, "WORKSPACE_ROOT") else None
    # workspace root'u gecici klasore yonlendir
    import tools.file_ops as file_ops_module
    orig_root = file_ops_module.WORKSPACE_ROOT
    file_ops_module.WORKSPACE_ROOT = str(tmp_path)
    scaffold_module_ws = scaffold_module
    # scaffold_ops icindeki WORKSPACE_ROOT referansini da guncelle
    orig_scf = scaffold_module.WORKSPACE_ROOT
    scaffold_module.WORKSPACE_ROOT = str(tmp_path)
    try:
        result = scaffold_module.scaffold("myproject", "generic")
        assert "myproject" in result
        assert os.path.exists(os.path.join(str(tmp_path), "myproject", "main.py"))
    finally:
        scaffold_module.WORKSPACE_ROOT = orig_scf
        file_ops_module.WORKSPACE_ROOT = orig_root


def test_scaffold_torch_experiment(tmp_path):
    import tools.scaffold_ops as sm
    orig = sm.WORKSPACE_ROOT
    sm.WORKSPACE_ROOT = str(tmp_path)
    try:
        result = sm.scaffold("myexp", "torch-experiment")
        assert "torch-experiment" in result
        assert os.path.exists(os.path.join(str(tmp_path), "myexp", "train.py"))
        assert os.path.exists(os.path.join(str(tmp_path), "myexp", "config.py"))
    finally:
        sm.WORKSPACE_ROOT = orig


def test_scaffold_unknown_type(tmp_path):
    import tools.scaffold_ops as sm
    orig = sm.WORKSPACE_ROOT
    sm.WORKSPACE_ROOT = str(tmp_path)
    try:
        result = sm.scaffold("x", "nonexistent")
        assert "Bilinmeyen" in result
    finally:
        sm.WORKSPACE_ROOT = orig


def test_scaffold_existing_dir_error(tmp_path):
    import tools.scaffold_ops as sm
    orig = sm.WORKSPACE_ROOT
    sm.WORKSPACE_ROOT = str(tmp_path)
    os.makedirs(os.path.join(str(tmp_path), "existing"))
    try:
        result = sm.scaffold("existing", "generic")
        assert "zaten var" in result
    finally:
        sm.WORKSPACE_ROOT = orig
