#!/usr/bin/env python3
"""Cross-platform installer and launcher for Memory Allocation Simulator."""

from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd: list[str], **kwargs) -> None:
    print(f"  > {' '.join(str(c) for c in cmd)}")
    subprocess.check_call(cmd, cwd=ROOT, **kwargs)


def ensure_venv() -> Path:
    py = venv_python()
    if py.exists():
        print("[OK] Virtual environment (.venv) already exists")
        return py

    print("[..] Creating virtual environment...")
    venv.create(VENV_DIR, with_pip=True, clear=False)
    if not py.exists():
        raise RuntimeError("Failed to create virtual environment.")
    print("[OK] Virtual environment created")
    return py


def install_deps(py: Path) -> None:
    print("[..] Installing dependencies...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    run([str(py), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    print("[OK] Dependencies installed")

