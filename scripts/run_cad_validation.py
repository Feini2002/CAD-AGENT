#!/usr/bin/env python
"""Compatibility wrapper for autonomous CAD validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.verification.cad_validation_runner import *  # noqa: F401,F403
from core.verification.cad_validation_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
