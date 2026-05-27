#!/usr/bin/env python
"""LCAD-14 wrapper: strict guard-chain rollup for write guard, negative CAD, and capability probe."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.guard_full_cad_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
