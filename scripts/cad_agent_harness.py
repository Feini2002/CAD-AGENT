#!/usr/bin/env python
"""Compatibility wrapper for the Phase 9 CAD Agent harness facade."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.contracts.cad_agent_harness import main


if __name__ == "__main__":
    raise SystemExit(main())
