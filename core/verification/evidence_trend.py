"""Evidence trend JSON contract shared by LCAD-11 trend rollups."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_contract import evidence_summary_rollup
from core.verification.evidence_vocabulary import (
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_INVALID_CONFIGURATION,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    EVIDENCE_STATE_VALUES,
    GEOMETRY_ACCURACY_VALUES,
    SCREENSHOT_ROLE_VALUES,
)


EVIDENCE_TREND_VERSION = "0.1"

EVIDENCE_STATE_ORDER: tuple[str, ...] = (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_BENCHMARK_PASS_NON_CAD,
    EVIDENCE_BLOCKED_EXPECTED_NON_CAD,
    EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
    EVIDENCE_INVALID_CONFIGURATION,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
)

GEOMETRY_ACCURACY_ORDER: tuple[str, ...] = tuple(sorted(GEOMETRY_ACCURACY_VALUES))
SCREENSHOT_ROLE_ORDER: tuple[str, ...] = tuple(sorted(SCREENSHOT_ROLE_VALUES))
GEOMETRY_VERIFIED_TREND_STATES: frozenset[str] = frozenset(
    {
        EVIDENCE_CAD_CAPABILITY_VERIFIED,
        EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    }
)
GUARD_ONLY_TREND_STATES: frozenset[str] = frozenset({EVIDENCE_NEGATIVE_GUARD_VERIFIED})
EVIDENCE_TREND_SOURCE_KINDS: frozenset[str] = frozenset(
    {
        "local_cad_regression",
        "cad_validation",
        "capability_coverage",
        "negative_cad_runner",
        "benchmark_suite",
        "manual",
    }
)

if set(EVIDENCE_STATE_ORDER) != EVIDENCE_STATE_VALUES:
    raise RuntimeError("EVIDENCE_STATE_ORDER must match EVIDENCE_STATE_VALUES.")


def _complete_count_map(
    values: tuple[str, ...],
    counts: dict[str, Any] | None,
    *,
    label: str,
) -> dict[str, int]:
    provided = counts or {}
    unknown = sorted(set(provided) - set(values))
    if unknown:
        raise ValueError(f"{label} contains unknown keys: {unknown}")
    completed: dict[str, int] = {}
    for key in values:
        value = provided.get(key, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{label}.{key} must be a non-negative integer")
        completed[key] = value
    return completed


def empty_evidence_state_counts() -> dict[str, int]:
    return {state: 0 for state in EVIDENCE_STATE_ORDER}


def summarize_evidence_trend_counts(evidence_state_counts: dict[str, int]) -> dict[str, Any]:
    total_count = sum(evidence_state_counts.values())
    cad_proof_state_count = sum(
        evidence_state_counts.get(state, 0) for state in GEOMETRY_VERIFIED_TREND_STATES
    )
    guard_only_count = sum(evidence_state_counts.get(state, 0) for state in GUARD_ONLY_TREND_STATES)
    blocked_or_invalid_count = (
        evidence_state_counts.get(EVIDENCE_BLOCKED_EXPECTED_NON_CAD, 0)
        + evidence_state_counts.get(EVIDENCE_INVALID_CONFIGURATION, 0)
    )
    summary = {
        "total_count": total_count,
        "geometry_verified_count": cad_proof_state_count,
        "cad_proof_state_count": cad_proof_state_count,
        "guard_only_count": guard_only_count,
        "blocked_or_invalid_count": blocked_or_invalid_count,
        "deferred_count": evidence_state_counts.get(EVIDENCE_DEFERRED_CAD_READBACK, 0),
        "non_cad_only": cad_proof_state_count == 0,
    }
    summary.update(evidence_summary_rollup(evidence_state_counts))
    return summary


def build_evidence_trend_snapshot(
    *,
    snapshot_id: str,
    series_id: str,
    source_kind: str,
    source_path: str,
    snapshot_at: str,
    evidence_state_counts: dict[str, Any],
    geometry_accuracy_counts: dict[str, Any] | None = None,
    screenshot_role_counts: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_kind not in EVIDENCE_TREND_SOURCE_KINDS:
        raise ValueError(f"unknown evidence trend source_kind: {source_kind!r}")
    completed_states = _complete_count_map(
        EVIDENCE_STATE_ORDER,
        evidence_state_counts,
        label="evidence_state_counts",
    )
    completed_accuracy = _complete_count_map(
        GEOMETRY_ACCURACY_ORDER,
        geometry_accuracy_counts,
        label="geometry_accuracy_counts",
    )
    completed_screenshot = _complete_count_map(
        SCREENSHOT_ROLE_ORDER,
        screenshot_role_counts,
        label="screenshot_role_counts",
    )
    return {
        "snapshot_id": snapshot_id,
        "series_id": series_id,
        "source_kind": source_kind,
        "source_path": source_path,
        "snapshot_at": snapshot_at,
        "evidence_state_counts": completed_states,
        "geometry_accuracy_counts": completed_accuracy,
        "screenshot_role_counts": completed_screenshot,
        "summary": summarize_evidence_trend_counts(completed_states),
        "metrics": dict(metrics or {}),
    }


def _vocabulary_block() -> dict[str, list[str]]:
    return {
        "evidence_states": list(EVIDENCE_STATE_ORDER),
        "geometry_accuracy_values": list(GEOMETRY_ACCURACY_ORDER),
        "screenshot_role_values": list(SCREENSHOT_ROLE_ORDER),
        "geometry_verified_evidence_states": sorted(GEOMETRY_VERIFIED_TREND_STATES),
        "guard_only_evidence_states": sorted(GUARD_ONLY_TREND_STATES),
    }


def build_evidence_trend_report(
    *,
    report_id: str,
    generated_at: str,
    snapshots: list[dict[str, Any]],
    status: str = "pass",
    notes: list[str] | None = None,
) -> dict[str, Any]:
    aggregate = empty_evidence_state_counts()
    for snapshot in snapshots:
        counts = snapshot.get("evidence_state_counts", {})
        if isinstance(counts, dict):
            for state in EVIDENCE_STATE_ORDER:
                value = counts.get(state, 0)
                if isinstance(value, int) and not isinstance(value, bool):
                    aggregate[state] += value
    summary = summarize_evidence_trend_counts(aggregate)
    summary["snapshot_count"] = len(snapshots)
    summary["series_count"] = len({str(snapshot.get("series_id", "")) for snapshot in snapshots})
    return {
        "version": EVIDENCE_TREND_VERSION,
        "report_id": report_id,
        "status": status,
        "generated_at": generated_at,
        "vocabulary": _vocabulary_block(),
        "snapshots": snapshots,
        "summary": summary,
        "notes": list(notes or []),
    }


def _validate_completed_counts(
    counts: Any,
    *,
    values: tuple[str, ...],
    label: str,
) -> list[str]:
    if not isinstance(counts, dict):
        return [f"{label} must be an object"]
    errors: list[str] = []
    expected = set(values)
    actual = set(counts)
    for key in sorted(actual - expected):
        errors.append(f"{label} has unknown key {key!r}")
    for key in sorted(expected - actual):
        errors.append(f"{label} missing key {key!r}")
    for key in sorted(actual & expected):
        value = counts.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{label}.{key} must be a non-negative integer")
    return errors


def validate_evidence_trend_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("version") != EVIDENCE_TREND_VERSION:
        errors.append(f"version must be {EVIDENCE_TREND_VERSION!r}")
    vocabulary = report.get("vocabulary")
    if not isinstance(vocabulary, dict):
        errors.append("vocabulary must be an object")
    else:
        expected_vocabulary = _vocabulary_block()
        for key, expected_values in expected_vocabulary.items():
            actual_values = vocabulary.get(key)
            if not isinstance(actual_values, list) or set(actual_values) != set(expected_values):
                errors.append(f"vocabulary.{key} must match shared evidence vocabulary")

    snapshots = report.get("snapshots")
    if not isinstance(snapshots, list):
        errors.append("snapshots must be an array")
        return errors
    aggregate = empty_evidence_state_counts()
    for index, snapshot in enumerate(snapshots):
        label = f"snapshots[{index}]"
        if not isinstance(snapshot, dict):
            errors.append(f"{label} must be an object")
            continue
        source_kind = snapshot.get("source_kind")
        if source_kind not in EVIDENCE_TREND_SOURCE_KINDS:
            errors.append(f"{label}.source_kind has unknown value {source_kind!r}")
        state_counts = snapshot.get("evidence_state_counts")
        errors.extend(_validate_completed_counts(state_counts, values=EVIDENCE_STATE_ORDER, label=f"{label}.evidence_state_counts"))
        errors.extend(
            _validate_completed_counts(
                snapshot.get("geometry_accuracy_counts"),
                values=GEOMETRY_ACCURACY_ORDER,
                label=f"{label}.geometry_accuracy_counts",
            )
        )
        errors.extend(
            _validate_completed_counts(
                snapshot.get("screenshot_role_counts"),
                values=SCREENSHOT_ROLE_ORDER,
                label=f"{label}.screenshot_role_counts",
            )
        )
        if isinstance(state_counts, dict) and not _validate_completed_counts(
            state_counts,
            values=EVIDENCE_STATE_ORDER,
            label=f"{label}.evidence_state_counts",
        ):
            expected_summary = summarize_evidence_trend_counts(state_counts)
            summary = snapshot.get("summary")
            if not isinstance(summary, dict):
                errors.append(f"{label}.summary must be an object")
            else:
                for key, expected_value in expected_summary.items():
                    if summary.get(key) != expected_value:
                        errors.append(f"{label}.summary.{key}={summary.get(key)!r}; expected {expected_value!r}")
            for state in EVIDENCE_STATE_ORDER:
                aggregate[state] += state_counts[state]

    summary = report.get("summary")
    if isinstance(summary, dict):
        expected_report_summary = summarize_evidence_trend_counts(aggregate)
        expected_report_summary["snapshot_count"] = len(snapshots)
        expected_report_summary["series_count"] = len({str(snapshot.get("series_id", "")) for snapshot in snapshots if isinstance(snapshot, dict)})
        for key, expected_value in expected_report_summary.items():
            if summary.get(key) != expected_value:
                errors.append(f"summary.{key}={summary.get(key)!r}; expected {expected_value!r}")
    else:
        errors.append("summary must be an object")
    return errors
