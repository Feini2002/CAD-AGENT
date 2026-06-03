#!/usr/bin/env python3
"""Refresh the training workbench data snapshot and validate its evidence boundary."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.sync_training_workbench.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_coverage import DEFAULT_OUTPUT_PATH, DEFAULT_REGISTRY_PATH, run_capability_coverage  # noqa: E402
from core.training.learning_promotion import promote_training_acceptance  # noqa: E402
from scripts import build_capability_map_data  # noqa: E402
from scripts.run_training_workbench_agent_check import run_agent_check  # noqa: E402


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "validation_runs" / "training-workbench-sync"


def display_path(path: Path, root: Path = PROJECT_ROOT) -> str:
    resolved = path if path.is_absolute() else root / path
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def write_markdown_report(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Training Workbench Sync Report",
        "",
        f"- status: `{report['status']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- coverage_status: `{report['coverage']['status']}`",
        f"- learning_promotion: `{report['learning_promotion']['status']}`",
        f"- data_output: `{report['data_output']}`",
        f"- agent_check: `{report['agent_check']['status']}`",
        "",
        "## Agent Check",
        "",
    ]
    for item in report["agent_check"].get("checks", []):
        lines.append(f"- `{item['status']}` {item['name']}: {item['detail']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_training_workbench(
    *,
    root: Path = PROJECT_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    data_output: Path = build_capability_map_data.OUTPUT,
    skip_coverage: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()

    if skip_coverage:
        coverage = {
            "status": "skipped",
            "output_path": display_path(DEFAULT_OUTPUT_PATH, root),
            "reason": "Caller requested --skip-coverage.",
        }
    else:
        coverage = run_capability_coverage(
            root,
            registry_path=DEFAULT_REGISTRY_PATH,
            output_path=DEFAULT_OUTPUT_PATH,
        )

    report_paths = [path for path in build_capability_map_data.training_acceptance_report_paths() if path.exists()]
    if report_paths:
        learning_promotion = promote_training_acceptance(
            root=root,
            report_paths=report_paths,
            programs=build_capability_map_data.training_programs(),
            ledger_path=build_capability_map_data.training_learning_ledger_path(),
        )
    else:
        learning_promotion = {
            "status": "skipped",
            "reason": "No accepted training report paths exist.",
            "acceptedItemCount": 0,
            "promotedAgentCount": 0,
        }

    build_capability_map_data.write_data(data_output)
    agent_check = run_agent_check(root, data_path=data_output, html_path=root / "capability-map.html")

    status = "pass"
    if coverage.get("status") not in {"pass", "skipped"}:
        status = "fail"
    if agent_check.get("status") != "pass":
        status = "fail"
    if report_paths and learning_promotion.get("status") != "promoted":
        status = "fail"

    report = {
        "version": "0.1",
        "status": status,
        "generated_at": generated_at,
        "root": str(root),
        "coverage": {
            "status": coverage.get("status"),
            "summary": coverage.get("summary", {}),
            "output_path": display_path(DEFAULT_OUTPUT_PATH, root),
            "skipped": skip_coverage,
        },
        "data_output": str(data_output),
        "html_path": str(root / "capability-map.html"),
        "learning_promotion": {
            "status": learning_promotion.get("status"),
            "acceptedItemCount": learning_promotion.get("acceptedItemCount", 0),
            "promotedAgentCount": learning_promotion.get("promotedAgentCount", 0),
            "promotionGate": learning_promotion.get("promotionGate", {}),
        },
        "agent_check": agent_check,
        "next_actions": [
            "打开 start_training_workbench.bat 可先同步再启动本地页面。",
            "训练、registry 或 coverage 改动后重新运行本脚本，避免 HTML 快照变旧。",
        ],
    }

    json_path = output_dir / "training_workbench_sync_report.json"
    md_path = output_dir / "training_workbench_sync_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_report(report, md_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh capability-map-data.js and validate the training workbench.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--data-output", type=Path, default=build_capability_map_data.OUTPUT)
    parser.add_argument("--skip-coverage", action="store_true", help="Only rebuild the workbench snapshot and agent-check it.")
    args = parser.parse_args()

    report = sync_training_workbench(
        output_dir=args.output_dir,
        data_output=args.data_output,
        skip_coverage=args.skip_coverage,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
