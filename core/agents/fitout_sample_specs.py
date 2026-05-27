"""Registered commercial fitout de-identified project samples (CFIT-09+)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FitoutSampleSpec:
    sample_id: str
    subscene_id: str
    project_rel: Path
    workflow_rel: Path
    confirmation_id: str
    default_notes: tuple[str, ...]

    @property
    def bundle_filename(self) -> str:
        return f"{self.sample_id}_confirmation_bundle.json"


DEFAULT_FITOUT_SAMPLE_ID = "commercial_fitout_sample"

FITOUT_SAMPLE_SPECS: dict[str, FitoutSampleSpec] = {
    "commercial_fitout_sample": FitoutSampleSpec(
        sample_id="commercial_fitout_sample",
        subscene_id="open_office",
        project_rel=Path("projects/commercial_fitout_sample"),
        workflow_rel=Path("examples/workflows/commercial_fitout_sample_confirmation_loop.json"),
        confirmation_id="confirm-commercial-fitout-sample-open-office",
        default_notes=(
            "Risk: shell obstacles are hand-authored and not CAD-verified.",
            "Risk: FITOUT_* blocks are placeholders until company block library is bound.",
            "Assumption: open-office zone sizing is indicative for layout preview only.",
        ),
    ),
    "commercial_fitout_meeting_sample": FitoutSampleSpec(
        sample_id="commercial_fitout_meeting_sample",
        subscene_id="meeting_room",
        project_rel=Path("projects/commercial_fitout_meeting_sample"),
        workflow_rel=Path("examples/workflows/commercial_fitout_meeting_sample_confirmation_loop.json"),
        confirmation_id="confirm-commercial-fitout-meeting-room",
        default_notes=(
            "Risk: meeting-room shell is hand-authored and not CAD-verified.",
            "Risk: FITOUT_* blocks are placeholders until company block library is bound.",
            "Assumption: meeting seating count is indicative for layout preview only.",
        ),
    ),
    "commercial_fitout_reception_sample": FitoutSampleSpec(
        sample_id="commercial_fitout_reception_sample",
        subscene_id="reception",
        project_rel=Path("projects/commercial_fitout_reception_sample"),
        workflow_rel=Path("examples/workflows/commercial_fitout_reception_sample_confirmation_loop.json"),
        confirmation_id="confirm-commercial-fitout-reception",
        default_notes=(
            "Risk: reception shell is hand-authored and not CAD-verified.",
            "Risk: FITOUT_* blocks are placeholders until company block library is bound.",
            "Assumption: entry approach and waiting zone sizing is indicative for layout preview only.",
        ),
    ),
}

# Backward-compatible alias used across C-CFIT-05/06 entry points.
FITOUT_SAMPLE_ID = DEFAULT_FITOUT_SAMPLE_ID


def resolve_fitout_sample_spec(sample_id: str | None = None) -> FitoutSampleSpec:
    resolved = sample_id or DEFAULT_FITOUT_SAMPLE_ID
    spec = FITOUT_SAMPLE_SPECS.get(resolved)
    if spec is None:
        raise ValueError(f"unknown commercial fitout sample_id: {resolved!r}")
    return spec


def fitout_subscene_to_sample_id() -> dict[str, str]:
    return {spec.subscene_id: spec.sample_id for spec in FITOUT_SAMPLE_SPECS.values()}


def resolve_fitout_sample_spec_for_workflow(workflow_path: Path, *, project_root: Path) -> FitoutSampleSpec:
    workflow_path = workflow_path.resolve()
    root = project_root.resolve()
    try:
        relative = workflow_path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"workflow_path must be under project root: {workflow_path}") from exc
    for spec in FITOUT_SAMPLE_SPECS.values():
        if spec.workflow_rel == relative:
            return spec
    raise ValueError(f"no registered fitout sample for workflow: {relative}")
