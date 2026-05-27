#!/usr/bin/env python
"""Compatibility wrapper for six-archetype symbol glyph CAD matrix (V-PROOF-32)."""

from __future__ import annotations

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import resolve_under_project_output
from core.verification.symbol_glyph_cad_matrix import main


if __name__ == "__main__":
    import sys

    if "--output-dir" not in sys.argv:
        from datetime import datetime
        from pathlib import Path

        default_out = (
            PROJECT_ROOT
            / "output"
            / "validation_runs"
            / f"symbol-glyph-cad-matrix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        sys.argv.extend(["--output-dir", str(default_out)])
    if "--root" not in sys.argv:
        sys.argv.extend(["--root", str(PROJECT_ROOT)])
    raise SystemExit(main())
