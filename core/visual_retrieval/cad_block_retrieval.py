"""Visual-first retrieval of CAD block references from an active drawing.

V0 intentionally ranks block references from lightweight visual/semantic
signals first. Detailed block construction summaries are optional confirmation
signals, not the primary retrieval path.
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from core.safety.policy import DIAGNOSTIC_LAYER, PREVIEW_LAYER
from core.verification.inspect_dwg import normalize_com_entity


SOFA_TOKENS = ("sofa", "couch", "沙发")
THREE_SEAT_TOKENS = ("三人", "三座", "三位", "3seat", "3-seat", "three-seat", "three seat")
TWO_SEAT_TOKENS = ("双人", "两人", "二人", "二座", "2seat", "2-seat", "two-seat", "two seat")
PLAN_VIEW_TOKENS = ("俯视", "平面", "plan", "top view", "top-view")
SCREENSHOT_TOKENS = ("截图", "图片", "image", "screenshot")
CONTROLLED_TEST_PREFIXES = ("CODEX_TEST_BLOCK",)


@dataclass(frozen=True)
class VisualQueryProfile:
    raw_query: str
    object_category: str
    visual_input_mode: str
    plan_view: bool
    seat_count: int | None
    aspect_ratio_min: float
    aspect_ratio_max: float
    min_width: float
    min_depth: float
    expected_parts: list[str] = field(default_factory=list)
    evidence_boundary: str = (
        "visual and semantic signals rank candidates only; CAD readback is required for geometry claims"
    )


@dataclass(frozen=True)
class BlockCandidate:
    handle: str
    block_name: str
    layer: str
    bbox: dict[str, list[float]] | None
    size: list[float] | None
    aspect_ratio: float | None
    source_entity: dict[str, Any]


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: BlockCandidate
    score: float
    reasons: list[str]
    block_definition_summary: dict[str, Any] | None = None


@dataclass(frozen=True)
class RetrievalReport:
    status: str
    query_profile: VisualQueryProfile
    candidate_count: int
    candidates: list[ScoredCandidate]
    best_match: ScoredCandidate | None
    timings: dict[str, float]
    active_document: dict[str, str] = field(default_factory=dict)
    safety: dict[str, bool] = field(
        default_factory=lambda: {
            "read_only": True,
            "wrote_cad": False,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["query_profile"] = asdict(self.query_profile)
        payload["candidates"] = [_scored_to_dict(item) for item in self.candidates]
        payload["best_match"] = _scored_to_dict(self.best_match) if self.best_match else None
        payload["evidence_boundary"] = {
            "visual": "visual/profile similarity is used for recall and ranking",
            "semantic": "object words constrain what kind of asset is being searched",
            "cad": "handle, block_name, layer and bbox are active-DWG readback evidence",
            "not_claimed": "screenshot pixels do not prove true CAD dimensions",
        }
        return payload


def parse_visual_query_profile(query: str, *, visual_hint: str | None = None) -> VisualQueryProfile:
    normalized = _normalize_text(" ".join(part for part in [query, visual_hint or ""] if part))
    object_category = "sofa" if _contains_any(normalized, SOFA_TOKENS) else "unknown"
    seat_count = None
    if _contains_any(normalized, THREE_SEAT_TOKENS):
        seat_count = 3
    elif _contains_any(normalized, TWO_SEAT_TOKENS):
        seat_count = 2

    plan_view = _contains_any(normalized, PLAN_VIEW_TOKENS) or object_category == "sofa"
    visual_input_mode = "screenshot_profile" if _contains_any(normalized, SCREENSHOT_TOKENS) else "semantic_profile"

    if object_category == "sofa" and seat_count == 3:
        ratio_min, ratio_max = 2.25, 3.8
        expected_parts = ["left_arm", "right_arm", "three_seat_divisions", "rounded_cushions", "back_or_base_band"]
    elif object_category == "sofa":
        ratio_min, ratio_max = 1.7, 3.8
        expected_parts = ["arms", "seat_cushions", "back_or_base_band"]
    else:
        ratio_min, ratio_max = 0.25, 6.0
        expected_parts = []

    return VisualQueryProfile(
        raw_query=query,
        object_category=object_category,
        visual_input_mode=visual_input_mode,
        plan_view=plan_view,
        seat_count=seat_count,
        aspect_ratio_min=ratio_min,
        aspect_ratio_max=ratio_max,
        min_width=1200.0 if object_category == "sofa" else 0.0,
        min_depth=400.0 if object_category == "sofa" else 0.0,
        expected_parts=expected_parts,
    )


def retrieve_visual_blocks(
    *,
    query: str,
    entities: list[dict[str, Any]],
    visual_hint: str | None = None,
    block_definition_summaries: dict[str, dict[str, Any]] | None = None,
    top_k: int = 5,
    clock: Callable[[], float] = time.perf_counter,
) -> RetrievalReport:
    started = clock()
    profile = parse_visual_query_profile(query, visual_hint=visual_hint)
    parsed_at = clock()
    candidates = [candidate for entity in entities if (candidate := block_candidate_from_entity(entity)) is not None]
    ranked = rank_candidates(profile, candidates, block_definition_summaries=block_definition_summaries)
    ranked = ranked[: max(1, top_k)]
    finished = clock()
    return RetrievalReport(
        status="pass" if ranked else "not_found",
        query_profile=profile,
        candidate_count=len(candidates),
        candidates=ranked,
        best_match=ranked[0] if ranked else None,
        timings={
            "profile_parse_seconds": round(parsed_at - started, 6),
            "candidate_rank_seconds": round(finished - parsed_at, 6),
            "total_seconds": round(finished - started, 6),
        },
    )


def retrieve_visual_blocks_from_driver(
    driver: Any,
    *,
    query: str,
    visual_hint: str | None = None,
    top_k: int = 5,
    inspect_top: int = 0,
    clock: Callable[[], float] = time.perf_counter,
) -> RetrievalReport:
    started = clock()
    entities = driver.snapshot_modelspace()
    snapshotted_at = clock()
    initial = retrieve_visual_blocks(
        query=query,
        visual_hint=visual_hint,
        entities=entities,
        top_k=max(top_k, inspect_top or top_k),
        clock=clock,
    )
    ranked_at = clock()
    summaries: dict[str, dict[str, Any]] = {}
    if inspect_top > 0:
        for scored in initial.candidates[:inspect_top]:
            summary = summarize_block_definition(driver, scored.candidate.block_name)
            if summary:
                summaries[scored.candidate.block_name] = summary
    summarized_at = clock()
    final = retrieve_visual_blocks(
        query=query,
        visual_hint=visual_hint,
        entities=entities,
        block_definition_summaries=summaries,
        top_k=top_k,
        clock=clock,
    )
    finished = clock()
    timings = dict(final.timings)
    timings.update(
        {
            "snapshot_seconds": round(snapshotted_at - started, 6),
            "initial_rank_seconds": round(ranked_at - snapshotted_at, 6),
            "block_summary_seconds": round(summarized_at - ranked_at, 6),
            "end_to_end_seconds": round(finished - started, 6),
        }
    )
    return RetrievalReport(
        status=final.status,
        query_profile=final.query_profile,
        candidate_count=final.candidate_count,
        candidates=final.candidates,
        best_match=final.best_match,
        timings=timings,
        active_document={
            "name": str(getattr(getattr(driver, "doc", None), "Name", "")),
            "full_name": str(getattr(getattr(driver, "doc", None), "FullName", "")),
        },
    )


def block_candidate_from_entity(entity: dict[str, Any]) -> BlockCandidate | None:
    if entity.get("type") != "block_reference":
        return None
    bbox = entity.get("bbox") if isinstance(entity.get("bbox"), dict) else None
    size = _bbox_size(bbox)
    aspect_ratio = None
    if size and size[1] > 0:
        width, depth = sorted(size, reverse=True)
        aspect_ratio = width / depth
    return BlockCandidate(
        handle=str(entity.get("handle", "")),
        block_name=str(entity.get("block_name", "")),
        layer=str(entity.get("layer", "")),
        bbox=bbox,
        size=size,
        aspect_ratio=aspect_ratio,
        source_entity=dict(entity),
    )


def rank_candidates(
    profile: VisualQueryProfile,
    candidates: list[BlockCandidate],
    *,
    block_definition_summaries: dict[str, dict[str, Any]] | None = None,
) -> list[ScoredCandidate]:
    summaries = block_definition_summaries or {}
    scored = [score_candidate(profile, candidate, summaries.get(candidate.block_name)) for candidate in candidates]
    return sorted(scored, key=lambda item: (-item.score, item.candidate.handle))


def score_candidate(
    profile: VisualQueryProfile,
    candidate: BlockCandidate,
    block_definition_summary: dict[str, Any] | None = None,
) -> ScoredCandidate:
    score = 0.0
    reasons: list[str] = []
    name_text = _normalize_text(f"{candidate.block_name} {candidate.layer}")

    if profile.object_category == "sofa" and _contains_any(name_text, SOFA_TOKENS):
        score += 5.0
        reasons.append("semantic_name_sofa")

    if candidate.aspect_ratio is not None:
        if profile.aspect_ratio_min <= candidate.aspect_ratio <= profile.aspect_ratio_max:
            score += 6.0
            reasons.append(f"visual_ratio_match={candidate.aspect_ratio:.2f}")
        elif profile.object_category != "unknown":
            distance = min(
                abs(candidate.aspect_ratio - profile.aspect_ratio_min),
                abs(candidate.aspect_ratio - profile.aspect_ratio_max),
            )
            if distance <= 0.5:
                score += 2.0
                reasons.append(f"visual_ratio_near={candidate.aspect_ratio:.2f}")

    if candidate.size:
        width, depth = sorted(candidate.size, reverse=True)
        if width >= profile.min_width and depth >= profile.min_depth:
            score += 3.0
            reasons.append(f"furniture_scale={width:.0f}x{depth:.0f}")

    if candidate.layer not in {PREVIEW_LAYER, DIAGNOSTIC_LAYER}:
        score += 1.0
        reasons.append("source_layer_not_preview")

    if candidate.block_name.startswith(CONTROLLED_TEST_PREFIXES):
        score -= 4.0
        reasons.append("controlled_test_block_penalty")

    if block_definition_summary:
        score += _score_block_summary(profile, block_definition_summary, reasons)

    return ScoredCandidate(
        candidate=candidate,
        score=round(score, 3),
        reasons=reasons,
        block_definition_summary=block_definition_summary,
    )


def summarize_block_definition(driver: Any, block_name: str) -> dict[str, Any] | None:
    doc = getattr(driver, "doc", None)
    blocks = getattr(doc, "Blocks", None)
    if blocks is None:
        return None
    try:
        block = blocks.Item(block_name)
    except Exception:
        return None

    entities: list[dict[str, Any]] = []
    try:
        count = int(block.Count)
    except Exception:
        return None
    for index in range(count):
        try:
            entities.append(normalize_com_entity(block.Item(index)))
        except Exception:
            continue
    type_counts = dict(Counter(str(entity.get("type", "unknown")) for entity in entities))
    long_vertical = 0
    long_horizontal = 0
    for entity in entities:
        start = entity.get("start_point")
        end = entity.get("end_point")
        if not (isinstance(start, list) and isinstance(end, list) and len(start) >= 2 and len(end) >= 2):
            continue
        dx = abs(float(start[0]) - float(end[0]))
        dy = abs(float(start[1]) - float(end[1]))
        if dx < 1e-3 and dy > 250:
            long_vertical += 1
        if dy < 1e-3 and dx > 500:
            long_horizontal += 1
    return {
        "block_name": block_name,
        "entity_count": len(entities),
        "type_counts": type_counts,
        "long_vertical_line_count": long_vertical,
        "long_horizontal_line_count": long_horizontal,
    }


def _score_block_summary(profile: VisualQueryProfile, summary: dict[str, Any], reasons: list[str]) -> float:
    type_counts = summary.get("type_counts", {})
    score = 0.0
    line_count = int(type_counts.get("line", 0)) if isinstance(type_counts, dict) else 0
    arc_count = int(type_counts.get("arc", 0)) if isinstance(type_counts, dict) else 0
    vertical_count = int(summary.get("long_vertical_line_count", 0))
    horizontal_count = int(summary.get("long_horizontal_line_count", 0))

    if profile.object_category == "sofa" and arc_count >= 4:
        score += 2.0
        reasons.append(f"rounded_part_arcs={arc_count}")
    if profile.seat_count and vertical_count >= profile.seat_count:
        score += 2.0
        reasons.append(f"seat_division_lines={vertical_count}")
    if profile.object_category == "sofa" and horizontal_count >= 2:
        score += 1.0
        reasons.append(f"long_sofa_bands={horizontal_count}")
    if line_count >= 20:
        score += 1.0
        reasons.append(f"rich_block_linework={line_count}")
    return score


def _scored_to_dict(scored: ScoredCandidate | None) -> dict[str, Any] | None:
    if scored is None:
        return None
    return {
        "score": scored.score,
        "reasons": scored.reasons,
        "candidate": asdict(scored.candidate),
        "block_definition_summary": scored.block_definition_summary,
    }


def _bbox_size(bbox: dict[str, Any] | None) -> list[float] | None:
    if not isinstance(bbox, dict):
        return None
    minimum = bbox.get("min")
    maximum = bbox.get("max")
    if not (isinstance(minimum, list) and isinstance(maximum, list) and len(minimum) >= 2 and len(maximum) >= 2):
        return None
    return [abs(float(maximum[0]) - float(minimum[0])), abs(float(maximum[1]) - float(minimum[1]))]


def _normalize_text(text: str) -> str:
    return text.strip().lower().replace("_", "-")


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token.lower() in text for token in tokens)
