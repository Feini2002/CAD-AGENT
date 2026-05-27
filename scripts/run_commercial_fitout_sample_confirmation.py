#!/usr/bin/env python3
"""Run commercial fitout sample confirmation loop (C-CFIT-05)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.agents.commercial_fitout_sample_confirmation import (
    run_fitout_sample_confirmation_loop,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "commercial-fitout-sample-confirmation",
    )
    parser.add_argument(
        "--confirmation",
        type=Path,
        default=None,
        help="Optional proposal_user_confirmation JSON; default builds from design_proposal.",
    )
    args = parser.parse_args()
    result = run_fitout_sample_confirmation_loop(
        args.output_dir,
        args.confirmation,
        project_root=PROJECT_ROOT,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
