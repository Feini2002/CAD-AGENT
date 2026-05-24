"""Compatibility wrapper for core.cad_io.autocad_com."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.cad_io.autocad_com import *  # noqa: F401,F403
