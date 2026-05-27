"""Compute CAD capability proof coverage from the capability registry (V-PROOF-02)."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.capability_registry import (
    DEFAULT_REGISTRY_PATH,
    load_capability_registry,
    validate_capability_registry,
)
from core.verification.evidence_trend import (
    build_evidence_trend_report,
    build_evidence_trend_snapshot,
    empty_evidence_state_counts,
    validate_evidence_trend_report,
)

COVERAGE_VERSION = "0.1"
DEFAULT_OUTPUT_PATH = Path("output/validation_runs/capability-lab/cad_capability_coverage.json")
CAPABILITY_COVERAGE_TREND_FILENAME = "capability_coverage_trend.json"

CLAIM_LEVELS = ("none", "deferred", "smoke", "verified", "showcase")
CAD_PROOF_LEVELS = ("verified", "showcase")
LADDER_STRENGTH_WEIGHTS: dict[str, int] = {
    "L0": 5,
    "L1": 15,
    "L2": 30,
    "L3": 50,
    "L4": 75,
    "L5": 100,
}
SCENE_FRAGMENT_LADDER_LEVELS = frozenset({"L3", "L4", "L5"})
LADDER_RANK = {level: index for index, level in enumerate(LADDER_STRENGTH_WEIGHTS)}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _count_table(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = str(row.get(field, "") or "unspecified")
        counter[value] += 1
    return dict(sorted(counter.items()))


def _compute_cad_strength_metrics(
    rows: list[dict[str, Any]],
    *,
    verified_count: int,
    showcase_count: int,
    total_count: int,
) -> dict[str, Any]:
    weight_total = 0
    weight_proven = 0
    scene_total = 0
    scene_proven = 0
    highest_proven_ladder = "L0"

    for row in rows:
        ladder_level = str(row.get("ladder_level") or "L0")
        weight = LADDER_STRENGTH_WEIGHTS.get(ladder_level, 10)
        weight_total += weight
        claim_level = str(row.get("claim_level", "none"))
        if claim_level in CAD_PROOF_LEVELS:
            weight_proven += weight
            if LADDER_RANK.get(ladder_level, -1) > LADDER_RANK.get(highest_proven_ladder, -1):
                highest_proven_ladder = ladder_level
        if ladder_level in SCENE_FRAGMENT_LADDER_LEVELS:
            scene_total += 1
            if claim_level in CAD_PROOF_LEVELS:
                scene_proven += 1

    cad_strength_index_rate = (weight_proven / weight_total) if weight_total else 0.0
    scene_fragment_strength_rate = (scene_proven / scene_total) if scene_total else 0.0
    showcase_readiness_rate = (showcase_count / total_count) if total_count else 0.0
    headline_rate = min(
        cad_strength_index_rate,
        scene_fragment_strength_rate,
        showcase_readiness_rate,
    )

    return {
        "cad_strength_index_rate": cad_strength_index_rate,
        "cad_strength_index_percent": round(cad_strength_index_rate * 100.0, 2),
        "scene_fragment_strength_rate": scene_fragment_strength_rate,
        "scene_fragment_strength_percent": round(scene_fragment_strength_rate * 100.0, 2),
        "scene_fragment_l3_plus_total_count": scene_total,
        "scene_fragment_l3_plus_verified_count": scene_proven,
        "showcase_readiness_rate": showcase_readiness_rate,
        "showcase_readiness_percent": round(showcase_readiness_rate * 100.0, 2),
        "cad_strength_headline_rate": headline_rate,
        "cad_strength_headline_percent": round(headline_rate * 100.0, 2),
        "highest_proven_ladder_level": highest_proven_ladder,
        "verified_count": verified_count,
        "showcase_count": showcase_count,
    }


def _evidence_path_status(rows: list[dict[str, Any]], *, project_root: Path) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        if row.get("claim_level") not in CAD_PROOF_LEVELS:
            continue
        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            counts["missing_evidence"] += 1
            continue
        report_path = evidence.get("report_path")
        if not isinstance(report_path, str) or not report_path.strip():
            counts["missing_report_path"] += 1
            continue
        resolved = (project_root / report_path).resolve()
        if resolved.is_file():
            counts["report_path_exists"] += 1
        else:
            counts["report_path_missing"] += 1
    return dict(counts)


def build_capability_coverage_report(
    registry: dict[str, Any],
    *,
    registry_path: Path,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    capabilities = registry.get("capabilities", [])
    if not isinstance(capabilities, list):
        raise ValueError("registry.capabilities must be a list.")

    claim_counts = Counter(str(row.get("claim_level", "unknown")) for row in capabilities if isinstance(row, dict))
    total_count = len(capabilities)
    verified_count = claim_counts.get("verified", 0)
    showcase_count = claim_counts.get("showcase", 0)
    cad_proof_count = verified_count + showcase_count
    cad_proof_coverage_rate = (cad_proof_count / total_count) if total_count else 0.0

    by_category = _count_table([row for row in capabilities if isinstance(row, dict)], "category")
    category_cad_proof: dict[str, dict[str, int | float]] = {}
    for category in sorted(by_category):
        subset = [row for row in capabilities if isinstance(row, dict) and row.get("category") == category]
        subset_claims = Counter(str(row.get("claim_level")) for row in subset)
        subset_total = len(subset)
        subset_verified = subset_claims.get("verified", 0) + subset_claims.get("showcase", 0)
        category_cad_proof[category] = {
            "total_count": subset_total,
            "verified_count": subset_claims.get("verified", 0),
            "showcase_count": subset_claims.get("showcase", 0),
            "cad_proof_count": subset_verified,
            "cad_proof_coverage_rate": (subset_verified / subset_total) if subset_total else 0.0,
        }

    capability_rows = [row for row in capabilities if isinstance(row, dict)]
    cad_strength = _compute_cad_strength_metrics(
        capability_rows,
        verified_count=verified_count,
        showcase_count=showcase_count,
        total_count=total_count,
    )

    snapshot_at = generated_at or _utc_now_iso()
    rel_registry = str(registry_path.resolve().relative_to(project_root.resolve())).replace("\\", "/")

    return {
        "version": COVERAGE_VERSION,
        "report_id": "cad-capability-coverage",
        "status": "pass",
        "generated_at": snapshot_at,
        "registry_path": rel_registry,
        "registry_id": str(registry.get("registry_id", "")),
        "registry_updated_at": registry.get("updated_at"),
        "summary": {
            "total_count": total_count,
            "verified_count": verified_count,
            "showcase_count": showcase_count,
            "smoke_count": claim_counts.get("smoke", 0),
            "deferred_count": claim_counts.get("deferred", 0),
            "none_count": claim_counts.get("none", 0),
            "cad_proof_count": cad_proof_count,
            "cad_proof_coverage_rate": cad_proof_coverage_rate,
            "cad_proof_coverage_percent": round(cad_proof_coverage_rate * 100.0, 2),
            "verified_coverage_rate": (verified_count / total_count) if total_count else 0.0,
            "showcase_coverage_rate": (showcase_count / total_count) if total_count else 0.0,
            **cad_strength,
        },
        "cad_strength": cad_strength,
        "by_claim_level": {level: claim_counts.get(level, 0) for level in CLAIM_LEVELS},
        "by_ladder_level": _count_table([row for row in capabilities if isinstance(row, dict)], "ladder_level"),
        "by_domain": _count_table([row for row in capabilities if isinstance(row, dict)], "domain"),
        "by_category": by_category,
        "category_cad_proof": category_cad_proof,
        "evidence_path_audit": _evidence_path_status(
            [row for row in capabilities if isinstance(row, dict)],
            project_root=project_root,
        ),
        "trend": {
            "series_id": "cad_capability_coverage",
            "snapshot_at": snapshot_at,
            "metrics": {
                "total_count": total_count,
                "verified_count": verified_count,
                "showcase_count": showcase_count,
                "cad_proof_count": cad_proof_count,
                "cad_proof_coverage_rate": cad_proof_coverage_rate,
                "cad_proof_coverage_percent": round(cad_proof_coverage_rate * 100.0, 2),
                "cad_strength_headline_percent": cad_strength["cad_strength_headline_percent"],
                "cad_strength_index_percent": cad_strength["cad_strength_index_percent"],
                "scene_fragment_strength_percent": cad_strength["scene_fragment_strength_percent"],
                "showcase_readiness_percent": cad_strength["showcase_readiness_percent"],
            },
        },
        "notes": [
            "cad_proof_coverage_rate counts claim_level verified or showcase only.",
            "smoke and deferred rows are registered but do not increase CAD proof coverage.",
            "geometry_verified must be backed by evidence.report_path before raising claim_level.",
            "cad_strength_headline_percent = min(cad_strength_index, scene_fragment L3+, showcase_readiness); not RCAD chimney completion.",
        ],
    }


def build_capability_coverage_trend_report(
    *,
    coverage_report: dict[str, Any],
    coverage_report_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    """Wrap coverage metrics in the shared evidence trend schema."""

    generated_at = str(coverage_report.get("generated_at", ""))
    snapshot = build_evidence_trend_snapshot(
        snapshot_id="capability-coverage-latest",
        series_id="cad_capability_coverage",
        source_kind="capability_coverage",
        source_path=str(coverage_report_path.resolve().relative_to(project_root.resolve())).replace("\\", "/"),
        snapshot_at=generated_at,
        evidence_state_counts=empty_evidence_state_counts(),
        metrics={
            **coverage_report.get("summary", {}),
            "registry_path": coverage_report.get("registry_path"),
            "registry_id": coverage_report.get("registry_id"),
            "registry_updated_at": coverage_report.get("registry_updated_at"),
        },
    )
    trend = build_evidence_trend_report(
        report_id="capability-coverage-trend",
        generated_at=generated_at,
        snapshots=[snapshot],
        notes=[
            "LCAD-11.4 capability coverage trend hook.",
            "Coverage metrics are carried in snapshot.metrics; this hook does not create new geometry evidence.",
        ],
    )
    errors = validate_evidence_trend_report(trend)
    if errors:
        raise ValueError("invalid capability coverage trend report: " + "; ".join(errors))
    return trend


def _write_capability_coverage_trend(
    *,
    coverage_report: dict[str, Any],
    coverage_report_path: Path,
    project_root: Path,
) -> Path:
    trend = build_capability_coverage_trend_report(
        coverage_report=coverage_report,
        coverage_report_path=coverage_report_path,
        project_root=project_root,
    )
    trend_path = coverage_report_path.parent / "evidence_trend" / CAPABILITY_COVERAGE_TREND_FILENAME
    trend_path.parent.mkdir(parents=True, exist_ok=True)
    trend_path.write_text(json.dumps(trend, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return trend_path


def run_capability_coverage(
    project_root: Path,
    *,
    registry_path: Path | None = None,
    output_path: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    registry_file = registry_path or (root / DEFAULT_REGISTRY_PATH)
    registry = load_capability_registry(registry_file, project_root=root)
    validation_errors = validate_capability_registry(registry)
    if validation_errors:
        return {
            "version": COVERAGE_VERSION,
            "report_id": "cad-capability-coverage",
            "status": "invalid",
            "generated_at": generated_at or _utc_now_iso(),
            "registry_path": str(registry_file),
            "errors": validation_errors,
        }

    report = build_capability_coverage_report(
        registry,
        registry_path=registry_file,
        project_root=root,
        generated_at=generated_at,
    )

    if output_path is not None:
        target = resolve_under_project_output(root, output_path, label="output_path")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["output_path"] = str(target.resolve().relative_to(root)).replace("\\", "/")
        trend_path = _write_capability_coverage_trend(
            coverage_report=report,
            coverage_report_path=target,
            project_root=root,
        )
        report["trend_output_path"] = str(trend_path.resolve().relative_to(root)).replace("\\", "/")

    return report
