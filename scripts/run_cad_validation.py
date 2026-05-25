#!/usr/bin/env python
"""Compatibility wrapper for autonomous CAD validation."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.cad_validation_runner import *  # noqa: F401,F403
from core.verification.cad_validation_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
