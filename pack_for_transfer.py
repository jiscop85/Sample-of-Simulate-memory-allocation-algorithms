#!/usr/bin/env python3
"""Create a portable ZIP of the project (cross-platform, safe paths)."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "MemoryAllocatorSim_Portable"
ZIP_PATH = ROOT / "MemoryAllocatorSim_Portable.zip"
