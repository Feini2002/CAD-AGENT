#!/usr/bin/env python
"""Compatibility wrapper for the real CAD COM capability probe."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.cad_capability_probe import main


if __name__ == "__main__":
    raise SystemExit(main())
