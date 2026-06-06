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

CHECKS: list[tuple[str, list[str]]] = [
    ("Unit tests", [str(PY), "-m", "unittest", "tests.test_simulator", "-v"]),
    (
        "CLI simulation",
        [
            str(PY),
            "main.py",
            "--sample",
            "classic",
            "--no-interactive",
            "--report",
            "output/report.txt",
            "--chart",
            "output/comparison_chart.png",
            "--memory-maps",
        ],
    ),
]

IMPORTS = [
    "memory_allocator.simulator",
    "memory_allocator.gui.app",
    "memory_allocator.report",
    "memory_allocator.visualization",
]


def check_files() -> bool:
    required = [
        "main.py",
        "requirements.txt",
        "INSTALL_AND_RUN.bat",
        "start.bat",
        "setup.bat",
        "memory_allocator/simulator.py",
        "memory_allocator/gui/app.py",
        "samples/classic.json",
        "docs",
        "verify_project.py",
    ]
    ok = True
    for rel in required:
        path = ROOT / rel
        exists = path.exists()
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {rel}")
        if not exists:
            ok = False
    report_docs = list((ROOT / "docs").glob("*.md")) if (ROOT / "docs").exists() else []
    has_report = len(report_docs) >= 2
    print(f"  [{'OK' if has_report else 'MISSING'}] docs/*.md (report + slides)")
    return ok and has_report


def check_imports() -> bool:
    ok = True
    for mod in IMPORTS:
        try:
            __import__(mod)
            print(f"  [OK] import {mod}")
        except Exception as exc:
            print(f"  [FAIL] import {mod}: {exc}")
            ok = False
    return ok


def main() -> int:
    print("\n=== Memory Allocator — Project Verification ===\n")
    failed = 0

    print("1) Required files:")
    if not check_files():
        failed += 1

    print("\n2) Python imports:")
    if not check_imports():
        failed += 1

    print("\n3) Subprocess checks:")
    for name, cmd in CHECKS:
        print(f"  Running: {name}...")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"  [FAIL] {name}")
            failed += 1
        else:
            print(f"  [OK] {name}")

    print("\n4) Output artifacts:")
    for rel in [
        "output/report.txt",
        "output/comparison_chart.png",
        "output/memory_maps/best_fit_map.png",
    ]:
        p = ROOT / rel
        print(f"  [{'OK' if p.exists() else 'MISSING'}] {rel}")

    print()
    if failed:
        print(f"=== FAILED ({failed} check groups) ===\n")
        return 1
    print("=== ALL CHECKS PASSED ===\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
