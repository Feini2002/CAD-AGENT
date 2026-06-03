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

from core.training.queue_runner import QUEUE_PRESETS, run_training_queue_step
from scripts import build_capability_map_data


DEFAULT_STATE = PROJECT_ROOT / "output" / "training_queues" / "cad-foundation-first-10" / "queue_state.json"


def resolve_state_path(path: Path) -> Path:
    resolved = path if path.is_absolute() else PROJECT_ROOT / path
    resolved = resolved.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"state path must stay under project root: {resolved}") from exc
    return resolved


def _post_sync_summary(sync_report: dict) -> dict:
    return {
        "status": sync_report.get("status", "unknown"),
        "coverageStatus": sync_report.get("coverage", {}).get("status", ""),
        "learningPromotionStatus": sync_report.get("learning_promotion", {}).get("status", ""),
        "acceptedItemCount": sync_report.get("learning_promotion", {}).get("acceptedItemCount", 0),
        "promotedAgentCount": sync_report.get("learning_promotion", {}).get("promotedAgentCount", 0),
        "agentCheckStatus": sync_report.get("agent_check", {}).get("status", ""),
    }


def _artifact_retention_summary(retention_report: dict) -> dict:
    return {
        "status": retention_report.get("status", "unknown"),
        "write": bool(retention_report.get("write", False)),
        "candidateCount": retention_report.get("candidateCount", 0),
        "keptCount": retention_report.get("keptCount", 0),
        "archivePlannedCount": retention_report.get("archivePlannedCount", 0),
        "archivedCount": retention_report.get("archivedCount", 0),
        "outputPath": retention_report.get("outputPath", ""),
    }


def run_training_queue(
    *,
    state_path: Path,
    preset: str = "cad-foundation-first-10",
    mode: str = "supervised",
    decision: str | None = None,
    feedback: str = "",
    reset: bool = False,
    post_sync: bool = True,
    sync_func=None,
    artifact_retention: bool = True,
    artifact_retention_write: bool = False,
    artifact_retention_func=None,
) -> dict:
    programs = build_capability_map_data.build_data()["trainingPrograms"]
    report = run_training_queue_step(
        programs,
        state_path=state_path,
        preset=preset,
        mode=mode,
        decision=decision,
        feedback=feedback,
        reset=reset,
    )
    report["postTrainingSync"] = {"status": "not_required", "reason": "No pass decision was recorded in this run."}
    report["postTrainingArtifactRetention"] = {
        "status": "not_required",
        "reason": "No pass decision was recorded in this run.",
    }
    if not post_sync:
        report["postTrainingSync"] = {"status": "skipped", "reason": "Caller requested --no-post-sync."}
        report["postTrainingArtifactRetention"] = {
            "status": "skipped",
            "reason": "Post-sync was skipped.",
        }
        return report
    if decision != "pass" and report.get("status") != "completed":
        return report

    if sync_func is None:
        from scripts.sync_training_workbench import sync_training_workbench

        sync_func = sync_training_workbench
    sync_report = sync_func(skip_coverage=report.get("status") != "completed")
    report["postTrainingSync"] = _post_sync_summary(sync_report)
    if not artifact_retention:
        report["postTrainingArtifactRetention"] = {
            "status": "skipped",
            "reason": "Caller requested --no-artifact-retention.",
        }
        return report
    if artifact_retention_func is None:
        from scripts.run_training_artifact_retention import run_default_training_artifact_retention

        artifact_retention_func = run_default_training_artifact_retention
    retention_report = artifact_retention_func(write=artifact_retention_write)
    report["postTrainingArtifactRetention"] = _artifact_retention_summary(retention_report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a supervised CAD training queue.")
    parser.add_argument("--preset", choices=sorted(QUEUE_PRESETS), default="cad-foundation-first-10")
    parser.add_argument("--mode", choices=["supervised"], default="supervised")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--decision", choices=["pass", "fail"], default=None)
    parser.add_argument("--feedback", default="")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--no-post-sync", action="store_true", help="Do not refresh the training workbench after a pass decision.")
    parser.add_argument("--no-artifact-retention", action="store_true", help="Skip the training screenshot retention dry-run after pass.")
    parser.add_argument(
        "--artifact-retention-write",
        action="store_true",
        help="Archive unreferenced old screenshots after pass. Defaults to dry-run.",
    )
    args = parser.parse_args()

    state_path = resolve_state_path(args.state)
    report = run_training_queue(
        state_path=state_path,
        preset=args.preset,
        mode=args.mode,
        decision=args.decision,
        feedback=args.feedback,
        reset=args.reset,
        post_sync=not args.no_post_sync,
        artifact_retention=not args.no_artifact_retention,
        artifact_retention_write=args.artifact_retention_write,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("postTrainingSync", {}).get("status") != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
