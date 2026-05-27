#!/usr/bin/env python
"""LCAD-10.2 wrapper: negative CAD_PLAN suite + preview write-guard checks."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.write_guard_cad_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
