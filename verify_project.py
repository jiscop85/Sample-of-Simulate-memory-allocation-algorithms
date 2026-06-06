#!/usr/bin/env python3
"""Full project verification — run before delivery."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = ROOT / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
if not PY.exists():
    PY = Path(sys.executable)
