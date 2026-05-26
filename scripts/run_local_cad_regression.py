#!/usr/bin/env python
"""Compatibility wrapper for local CAD regression matrix."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.local_cad_regression import main


if __name__ == "__main__":
    raise SystemExit(main())
