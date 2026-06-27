from __future__ import annotations

from pathlib import Path

import pytest

from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.footprints import boxes_overlap
from cad_agent.planning.relation_solver import solve_scene_relations


ROOT = Path(__file__).resolve().parents[2]


def obj(object_id: str, kind: str, *, dimensions: Dimensions2D | None = None, placement: PlacementIntent) -> SceneObjectSpec:
    return SceneObjectSpec(id=object_id, kind=kind, dimensions=dimensions, placement=placement)


def scene(objects: list[SceneObjectSpec], *, scene_id: str) -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id="run-rel-var",
        scene_id=scene_id,
        units="mm",
        view="plan_2d",
        objects=objects,
    )


def desk_scene(*, width: float = 1400, depth: float = 700, rotation_deg: float = 0, mouse_side: str = "right") -> SceneSpec:
    mouse_relation = {"right_of": "keyboard"} if mouse_side == "right" else {"left_of": "keyboard"}
    return scene(
        [
            obj(
                "desk",
                "desk",
                dimensions=Dimensions2D(width=width, depth=depth),
                placement=PlacementIntent(mode="absolute", base_point=(0, 0), rotation_deg=rotation_deg),
            ),
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
        ],
        scene_id=f"desk-{width}-{mouse_side}-{rotation_deg}",
    )


@pytest.mark.parametrize(("side", "direction"), [("right", 1), ("left", -1)])
def test_mouse_left_and_right_use_same_algorithm(side: str, direction: int):
    result = solve_scene_relations(desk_scene(mouse_side=side))

    assert result.status == "succeeded"
    assert (result.local_centers["mouse"][0] - result.local_centers["keyboard"][0]) * direction > 0


def test_double_monitor_places_second_monitor_relative_to_first():
    result = solve_scene_relations(
        scene(
            [
                obj(
                    "desk",
                    "desk",
                    dimensions=Dimensions2D(width=1800, depth=800),
                    placement=PlacementIntent(mode="absolute", base_point=(0, 0)),
                ),
                obj("monitor-a", "monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_left")),
                obj(
                    "monitor-b",
                    "monitor",
                    placement=PlacementIntent(mode="relative", on="desk", right_of="monitor-a", align_y="monitor-a", gap=40),
                ),
            ],
            scene_id="double-monitor",
        )
    )

    assert result.status == "succeeded"
    assert result.local_centers["monitor-b"][0] > result.local_centers["monitor-a"][0]
    assert result.local_centers["monitor-b"][1] == result.local_centers["monitor-a"][1]


@pytest.mark.parametrize("width", [900, 1200, 1600])
def test_supported_desk_widths_keep_surface_objects_inside_and_non_overlapping(width: float):
    result = solve_scene_relations(desk_scene(width=width, mouse_side="left" if width == 900 else "right"))

    assert result.status == "succeeded"
    desk_box = result.local_bboxes["desk"]
    children = ["monitor", "keyboard", "mouse", "vase"]
    for child in children:
        box = result.local_bboxes[child]
        assert box[0] >= desk_box[0]
        assert box[1] >= desk_box[1]
        assert box[2] <= desk_box[2]
        assert box[3] <= desk_box[3]
    for index, first in enumerate(children):
        for second in children[index + 1 :]:
            assert not boxes_overlap(result.local_bboxes[first], result.local_bboxes[second])


def test_narrow_desk_infeasible_fails_explicitly():
    result = solve_scene_relations(
        scene(
            [
                obj(
                    "desk",
                    "desk",
                    dimensions=Dimensions2D(width=900, depth=500),
                    placement=PlacementIntent(mode="absolute", base_point=(0, 0)),
                ),
                obj(
                    "keyboard",
                    "keyboard",
                    dimensions=Dimensions2D(width=820, depth=180),
                    placement=PlacementIntent(mode="relative", on="desk", anchor="center"),
                ),
                obj(
                    "mouse",
                    "mouse",
                    dimensions=Dimensions2D(width=160, depth=160),
                    placement=PlacementIntent(mode="relative", on="desk", right_of="keyboard", align_y="keyboard", gap=60),
                ),
            ],
            scene_id="narrow-infeasible",
        )
    )

    assert result.status == "blocked"
    assert "outside_surface:mouse" in result.unsatisfied_constraints


def test_rotated_desk_uses_world_local_coordinate_transform():
    result = solve_scene_relations(desk_scene(width=1000, depth=500, rotation_deg=90, mouse_side="right"))

    assert result.status == "succeeded"
    assert result.poses["desk"].center == (-250.0, 500.0)
    assert result.poses["monitor"].rotation_deg == 90
    assert result.local_centers["monitor"] == (500.0, 370.0)
    assert result.poses["monitor"].center == (-370.0, 500.0)


def test_relation_solver_source_has_no_exact_prompt_route_or_scene_template():
    source = (ROOT / "src" / "cad_agent" / "planning" / "relation_solver.py").read_text(encoding="utf-8")

    forbidden = [
        "帮我画",
        "电脑桌",
        "computer_desk_scene",
        "desk_with_monitor_keyboard_mouse_vase",
        "KEYWORD",
        "exact",
    ]
    for token in forbidden:
        assert token not in source
