"""Entry point for Memory Allocation Simulation."""

import sys

from memory_allocator.cli import cli_main
from memory_allocator.console import configure_console_encoding


def _launch_gui() -> int:
    try:
        from memory_allocator.gui import launch_gui
    except ImportError as exc:
        print("برای اجرای GUI ابتدا وابستگی‌ها را نصب کنید:")
        print("  pip install -r requirements.txt")
        print("  یا در ویندوز: setup.bat")
        print(f"خطا: {exc}")
        return 1
    launch_gui()
    return 0


def main() -> int:
    args = sys.argv[1:]

    if "--cli" in args:
        configure_console_encoding()
        return cli_main()

    if not args or "--gui" in args or "-g" in args:
        return _launch_gui()

    configure_console_encoding()
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
