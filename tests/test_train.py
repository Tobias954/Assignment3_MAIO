import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, env=None):
    assert subprocess.run(cmd, check=True, env=env).returncode == 0


def test_train_v01_and_v02(tmp_path):
    env = os.environ.copy()
    env["OUT_DIR"] = str(tmp_path / "models")
    env["VERSION"] = "v0.1"
    run([sys.executable, "src/train.py"], env=env)
    env["VERSION"] = "v0.2"
    run([sys.executable, "src/train.py"], env=env)
