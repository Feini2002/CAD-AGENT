#!/usr/bin/env python
"""Compatibility wrapper for core.verification.render_preview."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.verification.render_preview import *  # noqa: F401,F403
from core.verification.render_preview import main


if __name__ == "__main__":
    raise SystemExit(main())
