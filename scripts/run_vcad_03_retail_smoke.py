#!/usr/bin/env python3
"""VCAD-03: retail showroom visual plan smoke."""

from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.visual_room_plan_smoke import main  # noqa: E402


if __name__ == "__main__":
    import sys

    if "--scene" not in sys.argv:
        sys.argv[1:1] = ["--scene", "retail"]
    raise SystemExit(main())
