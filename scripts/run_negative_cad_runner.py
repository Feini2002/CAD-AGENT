#!/usr/bin/env python
"""LCAD-10.3 wrapper: real/fake negative CAD safety runner."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.negative_cad_runner import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
