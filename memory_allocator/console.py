"""Console encoding helpers for Windows compatibility."""

from __future__ import annotations

import sys


def configure_console_encoding() -> None:
    """Ensure UTF-8 output on Windows terminals when possible."""
    if sys.platform != "win32":
        return

    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass
