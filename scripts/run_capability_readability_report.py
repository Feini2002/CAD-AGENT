#!/usr/bin/env python3
"""Build a readable CAD capability coverage report."""

from __future__ import annotations

try:
    from _bootstrap import ensure_project_root_on_path
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_readability import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
