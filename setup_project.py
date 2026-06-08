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

def run_tests(py: Path) -> bool:
    print("[..] Running tests...")
    result = subprocess.run(
        [str(py), "-m", "unittest", "tests.test_simulator", "-q"],
        cwd=ROOT,
    )
    if result.returncode == 0:
        print("[OK] All tests passed")
        return True
    print("[!!] Some tests failed")
    return False


def launch_gui(py: Path) -> None:
    print("[..] Launching GUI...")
    run([str(py), str(ROOT / "main.py"), "--gui"])


def launch_cli(py: Path) -> None:
    run([str(py), str(ROOT / "main.py")])


def cmd_install(args: argparse.Namespace) -> int:
    print("\n=== Memory Allocation Simulator - Setup ===\n")
    try:
        py = ensure_venv()
        install_deps(py)
        run_tests(py)
        print("\n=== Setup completed successfully ===\n")
        print("Run GUI:")
        print(f"  {py} main.py --gui")
        print("\nWindows: double-click start.bat")
        print("Linux/Mac: ./start.sh\n")
        if args.run:
            launch_gui(py)
        return 0
    except Exception as exc:
        print(f"\n[ERROR] {exc}\n", file=sys.stderr)
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    py = venv_python()
    if not py.exists():
        print("Run setup first: python setup_project.py install")
        return 1
    try:
        if args.cli:
            launch_cli(py)
        else:
            launch_gui(py)
        return 0
    except subprocess.CalledProcessError:
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install and run Memory Allocation Simulator",
    )
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="Create venv and install dependencies")
    p_install.add_argument("--run", action="store_true", help="Launch GUI after install")
    p_install.set_defaults(func=cmd_install)

    p_run = sub.add_parser("run", help="Run application (requires prior install)")
    p_run.add_argument("--cli", action="store_true", help="Run CLI mode")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if not args.command:
        return cmd_install(argparse.Namespace(run=True))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

