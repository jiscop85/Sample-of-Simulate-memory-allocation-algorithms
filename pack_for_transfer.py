#!/usr/bin/env python3
"""Create a portable ZIP of the project (cross-platform, safe paths)."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "MemoryAllocatorSim_Portable"
ZIP_PATH = ROOT / "MemoryAllocatorSim_Portable.zip"

INCLUDE_DIRS = ("memory_allocator", "samples", "tests", "output", "docs")
INCLUDE_FILES = (
    "main.py",
    "requirements.txt",
    "README.md",
    "راهنمای_سریع.txt",
    "setup.bat",
    "start.bat",
    "start_cli.bat",
    "INSTALL_AND_RUN.bat",
    "run_gui.bat",
    "setup.sh",
    "start.sh",
    "setup_project.py",
    "pyproject.toml",
    ".gitignore",
    "verify_project.py",
)

SKIP_DIR_NAMES = {".venv", "__pycache__", ".git", "MemoryAllocatorSim_Portable"}
SKIP_FILE_SUFFIXES = {".pyc", ".pyo"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIR_NAMES:
        return True
    if path.suffix in SKIP_FILE_SUFFIXES:
        return True
    return False


def copy_tree(src: Path, dst: Path) -> None:
    for item in src.rglob("*"):
        if should_skip(item.relative_to(src)):
            continue
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    (OUT_DIR / "output").mkdir(exist_ok=True)

    for name in INCLUDE_DIRS:
        src = ROOT / name
        if src.is_dir():
            copy_tree(src, OUT_DIR / name)

    for name in INCLUDE_FILES:
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, OUT_DIR / name)

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in OUT_DIR.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(OUT_DIR.parent)
                zf.write(file, arcname)

    print(f"Folder: {OUT_DIR}")
    print(f"ZIP:    {ZIP_PATH}")
    print("Done! Transfer the ZIP and run INSTALL_AND_RUN.bat on the other PC.")


if __name__ == "__main__":
    main()
