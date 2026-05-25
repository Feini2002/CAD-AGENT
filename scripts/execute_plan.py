#!/usr/bin/env python
"""Compatibility wrapper for core.execution.execute_plan."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.execution.execute_plan import *  # noqa: F401,F403
from core.execution.execute_plan import main


if __name__ == "__main__":
    raise SystemExit(main())
