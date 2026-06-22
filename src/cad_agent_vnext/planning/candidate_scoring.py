from __future__ import annotations

from pydantic import Field

from cad_agent_vnext.domain.common import StrictModel


SCORE_WEIGHTS = {
    "outside_surface": 10000,
    "severe_overlap": 5000,
    "relation_violation": 2000,
    "clearance_shortfall": 10,
    "movement_from_preferred_anchor": 1,
}


class CandidateScore(StrictModel):
    total: float
    penalties: dict[str, float] = Field(default_factory=dict)


def score_candidate(
    *,
    outside_surface: bool = False,
    overlap_ratio: float = 0,
    relation_violations: int = 0,
    clearance_shortfall: float = 0,
    movement_from_preferred_anchor: float = 0,
) -> CandidateScore:
    penalties = {
        "outside_surface": SCORE_WEIGHTS["outside_surface"] if outside_surface else 0,
        "severe_overlap": SCORE_WEIGHTS["severe_overlap"] * max(0.0, float(overlap_ratio)),
        "relation_violation": SCORE_WEIGHTS["relation_violation"] * max(0, int(relation_violations)),
        "clearance_shortfall": SCORE_WEIGHTS["clearance_shortfall"] * max(0.0, float(clearance_shortfall)),
        "movement_from_preferred_anchor": SCORE_WEIGHTS["movement_from_preferred_anchor"]
        * max(0.0, float(movement_from_preferred_anchor)),
    }
    return CandidateScore(total=sum(penalties.values()), penalties=penalties)

