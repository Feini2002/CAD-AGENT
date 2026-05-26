#!/usr/bin/env python3
"""Run blank-shell workflow for a project sample (BETA-PROJECT-SAMPLE-03)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.project_samples.workflow import (  # noqa: E402
    DEFAULT_SAMPLE_ID,
    run_sample_blank_shell_workflow,
    validate_sample_workflow_result,
    write_sample_workflow_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run project sample blank-shell workflow.")
    parser.add_argument("--sample-id", default=DEFAULT_SAMPLE_ID)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/test_artifacts/project_samples/beta_project_sample_03"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    result = run_sample_blank_shell_workflow(
        args.sample_id,
        project_root=root,
        output_dir=output_dir,
    )
    report_path = write_sample_workflow_report(result, output_dir=output_dir)
    print(json.dumps({"report_path": str(report_path), **result}, ensure_ascii=False, indent=2))

    contract_errors = validate_sample_workflow_result(result)
    if result.get("status") != "ok" or contract_errors:
        if contract_errors:
            print("Contract errors:", file=sys.stderr)
            for error in contract_errors:
                print(f"  - {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
