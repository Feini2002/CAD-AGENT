from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.training.learning_promotion import ROUND_GATE_STAGES, run_training_round_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a training-case round gate.")
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--round", required=True, dest="round_id")
    parser.add_argument("--stage", choices=sorted(ROUND_GATE_STAGES), default="visual_contract")
    parser.add_argument("--fail-on-blocked", action="store_true")
    args = parser.parse_args()

    case_dir = args.case_dir
    if not case_dir.is_absolute():
        case_dir = PROJECT_ROOT / case_dir

    report = run_training_round_gate(case_dir, args.round_id, stage=args.stage)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_blocked and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
