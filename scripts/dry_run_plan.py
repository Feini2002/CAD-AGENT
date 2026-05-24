#!/usr/bin/env python
"""Compatibility wrapper for core.plan_engine.dry_run_plan."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.plan_engine.dry_run_plan import *  # noqa: F401,F403
from core.plan_engine.dry_run_plan import main


if __name__ == "__main__":
    raise SystemExit(main())
