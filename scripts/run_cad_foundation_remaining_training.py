#!/usr/bin/env python3
"""Run CAD foundation-operation batch training items."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.run_cad_foundation_remaining_training.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.foundation_batch_training import (  # noqa: E402
    FOUNDATION_BATCH_CONFIGS,
    QUEUE_ID,
    run_foundation_remaining_training_batch,
)
from core.training.streaming_demo import SleepFn, StreamingCadDemoConfig  # noqa: E402
from scripts import build_capability_map_data  # noqa: E402
from scripts.run_training_queue import _artifact_retention_summary, _post_sync_summary  # noqa: E402


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "training_queues" / QUEUE_ID / "remaining-21-chinese"


def _batch_config(batch_preset: str) -> dict[str, Any]:
    return FOUNDATION_BATCH_CONFIGS[batch_preset]


def _default_output_dir(batch_preset: str) -> Path:
    config = _batch_config(batch_preset)
    queue_id = str(config["queueId"])
    folder = "all-31-retrain" if batch_preset == "all-31" else "remaining-21-chinese"
    return PROJECT_ROOT / "output" / "training_queues" / queue_id / folder


def _focused_output_dir(capability_ids: list[str], *, batch_preset: str = "remaining-21") -> Path:
    config = _batch_config(batch_preset)
    queue_id = str(config["queueId"])
    name = "_".join(capability_ids) if capability_ids else "all"
    safe_name = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in name)
    return PROJECT_ROOT / "output" / "training_queues" / queue_id / "focused" / safe_name


def _parse_hatch_scales(value: str) -> list[float]:
    scales: list[float] = []
    for raw in value.split(","):
        raw = raw.strip()
        if raw:
            scales.append(float(raw))
    return scales


def _driver(fake_cad: bool) -> Any:
    if fake_cad:
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver()
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def run_remaining_training(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fake_cad: bool = False,
    timeout_seconds: int = 30,
    post_sync: bool = True,
    capture_preview: bool = True,
    selected_capability_ids: list[str] | None = None,
    scope_reason: str = "",
    training_options: dict[str, Any] | None = None,
    anchor_output_dir: Path | None = None,
    stream_demo: bool = False,
    stream_item_delay_seconds: float = 0.35,
    stream_operation_delay_seconds: float = 0.12,
    stream_operation_budget: int = 5,
    stream_zoom_each_item: bool = True,
    sleep_fn: SleepFn | None = None,
    sync_func=None,
    artifact_retention: bool = True,
    artifact_retention_write: bool = False,
    artifact_retention_func=None,
    batch_preset: str = "remaining-21",
    replay_mode: str = "smoke_replay",
    profile_source: Path | None = None,
    allow_low_expression: bool = False,
    project_root: Path | None = PROJECT_ROOT,
) -> dict[str, Any]:
    streaming_config = (
        StreamingCadDemoConfig.hybrid(
            item_delay_seconds=stream_item_delay_seconds,
            operation_delay_seconds=stream_operation_delay_seconds,
            operation_budget_per_item=stream_operation_budget,
            zoom_each_item=stream_zoom_each_item,
        )
        if stream_demo
        else StreamingCadDemoConfig.disabled()
    )
    report = run_foundation_remaining_training_batch(
        programs=build_capability_map_data.build_data()["trainingPrograms"],
        driver=_driver(fake_cad),
        output_dir=output_dir,
        timeout_seconds=timeout_seconds,
        capture_preview=capture_preview,
        selected_capability_ids=selected_capability_ids,
        scope_reason=scope_reason,
        training_options=training_options,
        anchor_output_dir=anchor_output_dir,
        streaming_config=streaming_config,
        sleep_fn=sleep_fn,
        batch_preset=batch_preset,
        replay_mode=replay_mode,
        profile_source=profile_source,
        allow_low_expression=allow_low_expression,
        project_root=project_root,
    )
    report["postTrainingSync"] = {"status": "not_required", "reason": "Training report did not pass."}
    report["postTrainingArtifactRetention"] = {
        "status": "not_required",
        "reason": "Training report did not pass.",
    }
    if report.get("status") != "pass" or not post_sync:
        if not post_sync:
            report["postTrainingSync"] = {"status": "skipped", "reason": "Caller requested --no-post-sync."}
            report["postTrainingArtifactRetention"] = {
                "status": "skipped",
                "reason": "Post-sync was skipped.",
            }
        return report
    if selected_capability_ids:
        report["postTrainingSync"] = {
            "status": "not_required",
            "reason": "Focused lightweight retraining does not replace full-batch acceptance.",
        }
        report["postTrainingArtifactRetention"] = {
            "status": "not_required",
            "reason": "Focused lightweight retraining does not replace full-batch acceptance.",
        }
        artifact_prefix = str(_batch_config(batch_preset)["artifactPrefix"])
        report_path = output_dir / f"{artifact_prefix}_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    if sync_func is None:
        from scripts.sync_training_workbench import sync_training_workbench

        sync_func = sync_training_workbench
    sync_report = sync_func(skip_coverage=False)
    report["postTrainingSync"] = _post_sync_summary(sync_report)
    if artifact_retention:
        if artifact_retention_func is None:
            from scripts.run_training_artifact_retention import run_default_training_artifact_retention

            artifact_retention_func = run_default_training_artifact_retention
        retention_report = artifact_retention_func(write=artifact_retention_write)
        report["postTrainingArtifactRetention"] = _artifact_retention_summary(retention_report)
    else:
        report["postTrainingArtifactRetention"] = {
            "status": "skipped",
            "reason": "Caller requested --no-artifact-retention.",
        }

    artifact_prefix = str(_batch_config(batch_preset)["artifactPrefix"])
    report_path = output_dir / f"{artifact_prefix}_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and accept CAD foundation-operation items.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--batch-preset",
        choices=sorted(FOUNDATION_BATCH_CONFIGS),
        default="remaining-21",
        help="Batch preset to run. Defaults to the historical remaining 21 items.",
    )
    parser.add_argument("--all-31", action="store_true", help="Shortcut for --batch-preset all-31.")
    parser.add_argument("--fake-cad", action="store_true", help="Use the in-memory fake CAD driver for tests.")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--no-post-sync", action="store_true", help="Skip training workbench sync after pass.")
    parser.add_argument("--no-artifact-retention", action="store_true", help="Skip the training screenshot retention dry-run after pass.")
    parser.add_argument(
        "--artifact-retention-write",
        action="store_true",
        help="Archive unreferenced old screenshots after full-batch pass. Defaults to dry-run.",
    )
    parser.add_argument("--no-capture-preview", action="store_true", help="Skip AutoCAD zoom/capture preparation.")
    parser.add_argument("--stream-demo", action="store_true", help="Enable hybrid streaming demo delays and per-item zoom.")
    parser.add_argument("--stream-item-delay", type=float, default=0.35, help="Delay between completed demo items.")
    parser.add_argument("--stream-operation-delay", type=float, default=0.12, help="Delay after critical drawing operations.")
    parser.add_argument("--stream-operation-budget", type=int, default=5, help="Max operation delays per item.")
    parser.add_argument("--stream-no-zoom", action="store_true", help="Disable per-item zoom during streaming demo mode.")
    parser.add_argument(
        "--replay-mode",
        choices=["smoke_replay", "growth_replay", "standard_replay"],
        default="smoke_replay",
        help="Adaptive replay contract mode. Defaults to legacy smoke replay.",
    )
    parser.add_argument(
        "--profile-source",
        type=Path,
        help="Repo-local adaptive capability profile JSON. Only read as planning context.",
    )
    parser.add_argument(
        "--allow-low-expression",
        action="store_true",
        help="Allow an explicitly recorded low-expression exemption in adaptive regression guard.",
    )
    parser.add_argument(
        "--only",
        action="append",
        dest="only",
        help="Focused retraining for one capability id. Repeat for multiple explicit ids.",
    )
    parser.add_argument("--scope-reason", default="", help="Human reason for focused retraining scope.")
    parser.add_argument("--hatch-pattern", help="For cad-hatch-boundary focused drills, test only this hatch pattern.")
    parser.add_argument(
        "--hatch-scales",
        help="Comma-separated hatch scales for --hatch-pattern, for example 0.25,0.5,1,2.",
    )
    parser.add_argument(
        "--hatch-full-fill",
        action="store_true",
        help="Focused cad-hatch-boundary drill for SOLID full-fill hatches.",
    )
    args = parser.parse_args()

    batch_preset = "all-31" if args.all_31 else args.batch_preset
    output_dir_was_default = args.output_dir == DEFAULT_OUTPUT_DIR
    output_dir = _default_output_dir(batch_preset) if output_dir_was_default else args.output_dir
    anchor_output_dir = None
    if args.only and output_dir_was_default:
        output_dir = _focused_output_dir(args.only, batch_preset=batch_preset)
        anchor_output_dir = _default_output_dir(batch_preset)

    training_options: dict[str, Any] = {}
    if args.hatch_full_fill:
        training_options["hatch_full_fill"] = True
    if args.hatch_pattern:
        training_options["hatch_pattern_focus"] = args.hatch_pattern
    if args.hatch_scales:
        training_options["hatch_scales"] = _parse_hatch_scales(args.hatch_scales)
    if args.hatch_full_fill and (args.hatch_pattern or args.hatch_scales):
        parser.error("--hatch-full-fill cannot be combined with --hatch-pattern/--hatch-scales")
    if training_options and "cad-hatch-boundary" not in (args.only or []):
        parser.error("hatch focused options require --only cad-hatch-boundary")

    report = run_remaining_training(
        output_dir=output_dir,
        fake_cad=args.fake_cad,
        timeout_seconds=args.timeout_seconds,
        post_sync=not args.no_post_sync,
        capture_preview=not args.no_capture_preview,
        selected_capability_ids=args.only,
        scope_reason=args.scope_reason,
        training_options=training_options,
        anchor_output_dir=anchor_output_dir,
        stream_demo=args.stream_demo,
        stream_item_delay_seconds=args.stream_item_delay,
        stream_operation_delay_seconds=args.stream_operation_delay,
        stream_operation_budget=args.stream_operation_budget,
        stream_zoom_each_item=not args.stream_no_zoom,
        artifact_retention=not args.no_artifact_retention,
        artifact_retention_write=args.artifact_retention_write,
        batch_preset=batch_preset,
        replay_mode=args.replay_mode,
        profile_source=args.profile_source,
        allow_low_expression=args.allow_low_expression,
        project_root=PROJECT_ROOT,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sync_status = report.get("postTrainingSync", {}).get("status")
    return 0 if report.get("status") == "pass" and sync_status != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
