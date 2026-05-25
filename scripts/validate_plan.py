#!/usr/bin/env python
"""Compatibility wrapper for core.plan_engine.validate_plan."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.plan_engine.validate_plan import *  # noqa: F401,F403
from core.plan_engine.validate_plan import main


if __name__ == "__main__":
    raise SystemExit(main())
