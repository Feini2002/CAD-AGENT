#!/usr/bin/env python
"""Compatibility wrapper for the local CAD Session Host bridge."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.cad_io.cad_session_host import main


if __name__ == "__main__":
    raise SystemExit(main())
