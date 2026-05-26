#!/usr/bin/env python
"""Compatibility wrapper for the complex CAD smoke test."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.complex_cad_smoke import main


if __name__ == "__main__":
    raise SystemExit(main())
