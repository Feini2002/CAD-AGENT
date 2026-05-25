#!/usr/bin/env python
"""Compatibility wrapper for core.verification.render_preview."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.render_preview import *  # noqa: F401,F403
from core.verification.render_preview import main


if __name__ == "__main__":
    raise SystemExit(main())
