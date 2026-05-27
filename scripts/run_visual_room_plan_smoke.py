#!/usr/bin/env python3
"""Run VCAD-02 visual room plan smoke."""

from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.visual_room_plan_smoke import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
