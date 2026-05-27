#!/usr/bin/env python3
"""Apply RCAD / verification report evidence to cad_capability_registry rows (V-PROOF-03)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_registry import DEFAULT_REGISTRY_PATH  # noqa: E402
from core.verification.capability_registry_writeback import (  # noqa: E402
    WritebackRequest,
    run_registry_writeback,
    suggest_writebacks_from_regression_output,
)


def _load_requests(path: Path) -> list[WritebackRequest]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "requests" in payload:
        items = payload["requests"]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError("Batch file must be a list or an object with requests[].")
    requests: list[WritebackRequest] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each writeback request must be an object.")
        requests.append(
            WritebackRequest(
                capability_id=str(item["capability_id"]),
                report_path=str(item["report_path"]),
                claim_level=str(item.get("claim_level", "verified")),
                last_verified_at=item.get("last_verified_at"),
                note=item.get("note"),
            )
        )
    return requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Write geometry-verified evidence into capability registry rows.")
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--batch",
        type=Path,
        help="JSON file: list of {capability_id, report_path, claim_level?} or {requests: [...]}",
    )
    parser.add_argument("--capability-id", type=str, help="Single-row writeback capability_id")
    parser.add_argument("--report", type=Path, help="Verification report path for single-row writeback")
    parser.add_argument(
        "--suggest-from-regression",
        type=Path,
        metavar="OUTPUT_DIR",
        help="Scan a local CAD regression output dir and build writeback requests from manifest cases.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist registry changes (default is dry-run).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/validation_runs/capability-lab/cad_capability_writeback.json"),
        help="Write batch result JSON under project output/",
    )
    args = parser.parse_args()

    requests: list[WritebackRequest] = []
    if args.batch:
        requests.extend(_load_requests(args.batch))
    if args.capability_id and args.report:
        requests.append(
            WritebackRequest(
                capability_id=args.capability_id,
                report_path=str(args.report).replace("\\", "/"),
            )
        )
    if args.suggest_from_regression:
        requests.extend(
            suggest_writebacks_from_regression_output(
                PROJECT_ROOT,
                output_dir=args.suggest_from_regression,
            )
        )
    if not requests:
        parser.error("Provide --batch, (--capability-id and --report), or --suggest-from-regression.")

    batch = run_registry_writeback(
        PROJECT_ROOT,
        registry_path=args.registry_path,
        requests=requests,
        dry_run=not args.apply,
        save_registry_file=args.apply,
        batch_output_path=args.output,
    )
    print(json.dumps(batch.to_dict(), ensure_ascii=False, indent=2))
    return 0 if batch.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
