from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cad_agent.adapters.autocad_backend import AutoCadBackend
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.primitives import Primitive


SCHEMA_VERSION = "cad-agent-real-cad-smoke/v1"


def build_smoke_patch(*, run_id: str, transaction_id: str) -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id=run_id,
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
        operations=[
            PatchOperation(
                op_id="create-rectangle",
                action="create",
                semantic_object_id="smoke_rectangle",
                primitives=[
                    Primitive(
                        primitive_id="smoke_rectangle_body",
                        semantic_object_id="smoke_rectangle",
                        primitive_type="rectangle",
                        geometry={"origin": [0, 0], "width": 120, "depth": 70},
                        layer="CODEX_PREVIEW",
                        style_token="preview.default",
                        expected_entity_type="LWPOLYLINE",
                    )
                ],
            ),
            PatchOperation(
                op_id="create-circle",
                action="create",
                semantic_object_id="smoke_circle",
                primitives=[
                    Primitive(
                        primitive_id="smoke_circle_body",
                        semantic_object_id="smoke_circle",
                        primitive_type="circle",
                        geometry={"center": [180, 35], "radius": 25},
                        layer="CODEX_PREVIEW",
                        style_token="preview.default",
                        expected_entity_type="CIRCLE",
                    )
                ],
            ),
            PatchOperation(
                op_id="create-text",
                action="create",
                semantic_object_id="smoke_text",
                primitives=[
                    Primitive(
                        primitive_id="smoke_text_label",
                        semantic_object_id="smoke_text",
                        primitive_type="text",
                        geometry={"position": [0, 95], "text": "SMOKE"},
                        layer="CODEX_PREVIEW",
                        style_token="preview.default",
                        expected_entity_type="TEXT",
                    )
                ],
            ),
        ],
    )


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"real-cad-smoke-{timestamp}"
    transaction_id = args.transaction_id or f"{run_id}-txn"
    output_dir = Path(args.output_dir or Path(".cad_agent_runs") / run_id)
    report_path = output_dir / "real_cad_backend_smoke.json"

    blockers = _preflight_blockers(args)
    if blockers:
        report = _base_report(
            run_id=run_id,
            transaction_id=transaction_id,
            status="blocked",
            blocking_reasons=blockers,
            output_dir=output_dir,
        )
        return _write_report(report, report_path)

    try:
        backend = _backend_from_args(args)
        patch = build_smoke_patch(run_id=run_id, transaction_id=transaction_id)
        receipt = backend.apply_patch(patch)
        readback = backend.readback(transaction_id=transaction_id)
        visual_aid = backend.capture_view(transaction_id=transaction_id, output_path=str(output_dir / "visual_aid.json"))
        rollback = backend.rollback(rollback_token=receipt.rollback_token or "") if args.rollback_after_check else None
    except Exception as exc:
        report = _base_report(
            run_id=run_id,
            transaction_id=transaction_id,
            status="blocked",
            blocking_reasons=[f"backend_unavailable:{type(exc).__name__}:{exc}"],
            output_dir=output_dir,
        )
        return _write_report(report, report_path)

    checks = _checks(receipt=receipt, readback=readback, rollback=rollback)
    status = "succeeded" if all(item["status"] == "pass" for item in checks) else "blocked"
    report = _base_report(
        run_id=run_id,
        transaction_id=transaction_id,
        status=status,
        blocking_reasons=[item["name"] for item in checks if item["status"] != "pass"],
        output_dir=output_dir,
    )
    report.update(
        {
            "backend": receipt.backend,
            "createdHandles": list(receipt.created_handles),
            "semanticToHandles": dict(receipt.semantic_to_handles),
            "receiptStatus": receipt.status,
            "readbackEntityCount": len(readback.entities),
            "rollbackStatus": rollback.status if rollback is not None else "not_requested",
            "savedCurrentDwg": receipt.saved_current_dwg,
            "visualAid": visual_aid,
            "checks": checks,
        }
    )
    return _write_report(report, report_path)


def _preflight_blockers(args: argparse.Namespace) -> list[str]:
    blockers: list[str] = []
    if not args.preview_only:
        blockers.append("preview_only_flag_required")
    if not args.rollback_after_check:
        blockers.append("rollback_after_check_flag_required")
    return blockers


def _backend_from_args(args: argparse.Namespace) -> AutoCadBackend:
    return AutoCadBackend.from_existing_autocad()


def _checks(
    *,
    receipt: Any,
    readback: Any,
    rollback: Any,
) -> list[dict[str, str]]:
    expected_handle_count = 3
    checks = [
        ("receipt_succeeded", receipt.status == "succeeded"),
        ("handles_count_expected", len(receipt.created_handles) == expected_handle_count),
        ("readback_count_expected", len(readback.entities) == expected_handle_count),
        ("all_layers_preview", all(entity.layer == "CODEX_PREVIEW" for entity in readback.entities)),
        ("all_bbox_non_empty", all(entity.bbox is not None for entity in readback.entities)),
        ("saved_current_dwg_false", receipt.saved_current_dwg is False),
        ("rollback_succeeded", rollback is not None and rollback.status == "succeeded"),
    ]
    return [{"name": name, "status": "pass" if passed else "blocked"} for name, passed in checks]


def _base_report(
    *,
    run_id: str,
    transaction_id: str,
    status: str,
    blocking_reasons: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
            "package": "cleanroom",
        "status": status,
        "runId": run_id,
        "transactionId": transaction_id,
        "outputDir": str(output_dir),
        "blockingReasons": blocking_reasons,
        "previewOnly": True,
        "savedCurrentDwg": False,
        "screenshotRole": "visual_aid_only",
        "notEvidenceFor": ["production_native_plugin", "formal_layer_write", "dwg_save"],
    }


def _write_report(report: dict[str, Any], report_path: Path) -> dict[str, Any]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report["reportPath"] = str(report_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the cleanroom real CAD backend smoke.")
    parser.add_argument("--backend", choices=["existing-autocad"], default="existing-autocad")
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument("--rollback-after-check", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--transaction-id", default="")
    parser.add_argument("--output-dir", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_smoke(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "succeeded":
        return 0
    return 2 if report["status"] == "blocked" else 1


if __name__ == "__main__":
    sys.exit(main())
