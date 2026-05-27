#!/usr/bin/env python3
"""Run visual CAD smoke: richer office-corner drawing, not table-C coverage."""

from __future__ import annotations

import sys

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.visual_cad_smoke import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
