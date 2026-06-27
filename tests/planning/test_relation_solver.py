from __future__ import annotations

import pytest

from cad_agent.domain.drawing import DrawingEntitySnapshot
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.anchors import anchor_point
from cad_agent.planning.candidate_scoring import SCORE_WEIGHTS, score_candidate
from cad_agent.planning.relation_graph import build_relation_graph
from cad_agent.planning.relation_solver import solve_scene_relations


def scene(objects: list[SceneObjectSpec], *, scene_id: str = "scene") -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id="run-rel",
        scene_id=scene_id,
        units="mm",
        view="plan_2d",
        objects=objects,
    )


def obj(
    object_id: str,
    kind: str,
    *,
    dimensions: Dimensions2D | None = None,
    placement: PlacementIntent | None = None,
) -> SceneObjectSpec:
    return SceneObjectSpec(
        id=object_id,
        kind=kind,
        dimensions=dimensions,
        placement=placement or PlacementIntent(mode="absolute", base_point=(0, 0)),
    )


def standard_scene(*, mouse_side: str = "right") -> SceneSpec:
    mouse_relation = {"right_of": "keyboard"} if mouse_side == "right" else {"left_of": "keyboard"}
    return scene(
        [
            obj("desk", "desk", placement=PlacementIntent(mode="absolute", base_point=(0, 0))),
            obj("monitor", "monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_center")),
            obj(
                "keyboard",
                "keyboard",
                placement=PlacementIntent(mode="relative", on="desk", in_front_of="monitor", align_x="monitor", gap=40),
            ),
            obj(
                "mouse",
                "mouse",
                placement=PlacementIntent(mode="relative", on="desk", align_y="keyboard", gap=40, **mouse_relation),
            ),
            obj("vase", "vase", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_right")),
        ]
    )


def assert_inside(inner: tuple[float, float, float, float], outer: tuple[float, float, float, float]) -> None:
    assert inner[0] >= outer[0]
    assert inner[1] >= outer[1]
    assert inner[2] <= outer[2]
    assert inner[3] <= outer[3]


def test_anchor_points_are_computed_from_bbox_and_margin():
    bbox = (0.0, 0.0, 1000.0, 500.0)

    assert anchor_point(bbox, "front_left", margin=50) == (50.0, 50.0)
    assert anchor_point(bbox, "front_center", margin=50) == (500.0, 50.0)
    assert anchor_point(bbox, "front_right", margin=50) == (950.0, 50.0)
    assert anchor_point(bbox, "center_left", margin=50) == (50.0, 250.0)
    assert anchor_point(bbox, "center", margin=50) == (500.0, 250.0)
    assert anchor_point(bbox, "center_right", margin=50) == (950.0, 250.0)
    assert anchor_point(bbox, "rear_left", margin=50) == (50.0, 450.0)
    assert anchor_point(bbox, "rear_center", margin=50) == (500.0, 450.0)
    assert anchor_point(bbox, "rear_right", margin=50) == (950.0, 450.0)


def test_candidate_scoring_weights_are_fixed_by_policy():
    assert SCORE_WEIGHTS == {
        "outside_surface": 10000,
        "severe_overlap": 5000,
        "relation_violation": 2000,
        "clearance_shortfall": 10,
        "movement_from_preferred_anchor": 1,
    }

    score = score_candidate(
        outside_surface=True,
        overlap_ratio=0.5,
        relation_violations=2,
        clearance_shortfall=30,
        movement_from_preferred_anchor=12,
    )

    assert score.total == 16812
    assert score.penalties["outside_surface"] == 10000
    assert score.penalties["severe_overlap"] == 2500
    assert score.penalties["relation_violation"] == 4000
    assert score.penalties["clearance_shortfall"] == 300
    assert score.penalties["movement_from_preferred_anchor"] == 12


def test_standard_scene_solves_relations_inside_surface():
    result = solve_scene_relations(standard_scene())

    assert result.status == "succeeded"
    assert result.unsatisfied_constraints == []
    assert list(result.poses) == ["desk", "monitor", "keyboard", "mouse", "vase"]
    desk_box = result.local_bboxes["desk"]
    for object_id in ["monitor", "keyboard", "mouse", "vase"]:
        assert_inside(result.local_bboxes[object_id], desk_box)
    assert result.local_centers["keyboard"][1] < result.local_centers["monitor"][1]
    assert result.local_centers["mouse"][0] > result.local_centers["keyboard"][0]
    assert result.local_centers["vase"][0] > result.local_centers["monitor"][0]


def test_missing_reference_blocks_without_guessing_success():
    invalid = SceneSpec.model_construct(
        schema_version="scene-spec/v1",
        run_id="run-rel",
        scene_id="missing-ref",
        units="mm",
        view="plan_2d",
        objects=[
            obj("desk", "desk", placement=PlacementIntent(mode="absolute", base_point=(0, 0))),
            obj("keyboard", "keyboard", placement=PlacementIntent(mode="relative", on="desk", in_front_of="ghost")),
        ],
        constraints=[],
        target_layer="CODEX_PREVIEW",
        assumptions=[],
    )

    result = solve_scene_relations(invalid)

    assert result.status == "blocked"
    assert result.poses == {}
    assert "unknown_object_reference:keyboard:ghost" in result.unsatisfied_constraints


def test_relation_graph_detects_cycles():
    cyclic = scene(
        [
            obj("a", "keyboard", placement=PlacementIntent(mode="relative", right_of="b")),
            obj("b", "mouse", placement=PlacementIntent(mode="relative", right_of="a")),
        ],
        scene_id="cycle",
    )

    graph = build_relation_graph(cyclic.objects)
    result = solve_scene_relations(cyclic)

    assert graph.status == "blocked"
    assert graph.order == []
    assert graph.errors == ["relation_cycle:a,b"]
    assert result.status == "blocked"
    assert result.unsatisfied_constraints == ["relation_cycle:a,b"]


def test_nearby_collision_blocks_when_snapshot_entity_overlaps_candidate():
    nearby = [
        DrawingEntitySnapshot(
            handle="N1",
            entity_type="LWPOLYLINE",
            layer="CODEX_PREVIEW",
            bbox=(450, 420, 950, 700),
        )
    ]

    result = solve_scene_relations(standard_scene(), nearby_entities=nearby)

    assert result.status == "blocked"
    assert "nearby_collision:monitor:N1" in result.unsatisfied_constraints
