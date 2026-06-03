from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def configure_utf8_stdio(stdout: TextIO | None = None, stderr: TextIO | None = None) -> None:
    """Keep JSON CLI output stable in non-UTF-8 Windows consoles."""

    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    for stream in [stdout or sys.stdout, stderr or sys.stderr]:
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def ensure_project_root_on_path() -> Path:
    root_text = str(PROJECT_ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return PROJECT_ROOT


configure_utf8_stdio()
ensure_project_root_on_path()
