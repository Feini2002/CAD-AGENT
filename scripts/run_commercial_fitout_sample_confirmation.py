#!/usr/bin/env python3
"""Run commercial fitout sample confirmation loop (C-CFIT-05)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.agents.commercial_fitout_sample_confirmation import (  # noqa: E402
    run_fitout_sample_confirmation_loop,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "commercial-fitout-sample-confirmation",
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
        project_root=ROOT,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
