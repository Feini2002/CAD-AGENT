from __future__ import annotations

from pathlib import Path

import pytest

from cad_agent_vnext.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent_vnext.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent_vnext.planning.impact_estimator import estimate_patch_impact
from cad_agent_vnext.planning.scene_compiler import compile_scene
from cad_agent_vnext.planning.semantic_mapping import build_semantic_mapping


ROOT = Path(__file__).resolve().parents[3]


def snapshot(*, target_region: tuple[float, float, float, float] | None = (0, 0, 2000, 1200), nearby=None) -> DrawingSnapshot:
    return DrawingSnapshot(
        schema_version="drawing-snapshot/v1",
        run_id="run-compile",
        document_id="fake-doc",
        units="mm",
        current_space="model",
        active_layer="CODEX_PREVIEW",
        saved=False,
        target_region=target_region,
        nearby_entities=nearby or [],
        snapshot_hash="snapshot:test",
    )


def obj(object_id: str, kind: str, *, dimensions: Dimensions2D | None = None, placement: PlacementIntent) -> SceneObjectSpec:
    return SceneObjectSpec(id=object_id, kind=kind, dimensions=dimensions, placement=placement)


def scene(objects: list[SceneObjectSpec], *, scene_id: str = "scene") -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id="run-compile",
        scene_id=scene_id,
        units="mm",
        view="plan_2d",
        objects=objects,
    )


def standard_scene(*, mouse_side: str = "right", desk_mode: str = "absolute", rotation_deg: float = 0) -> SceneSpec:
    mouse_relation = {"right_of": "keyboard"} if mouse_side == "right" else {"left_of": "keyboard"}
    desk_placement = (
        PlacementIntent(mode="absolute", base_point=(0, 0), rotation_deg=rotation_deg)
        if desk_mode == "absolute"
        else PlacementIntent(mode="free_region_center", rotation_deg=rotation_deg)
    )
    return scene(
        [
            obj("desk", "desk", placement=desk_placement),
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
        scene_id=f"standard-{mouse_side}-{desk_mode}-{rotation_deg}",
    )


def test_standard_scene_compiles_to_preview_create_patch_with_semantic_mapping():
    result = compile_scene(standard_scene(), snapshot())

    assert result.status == "succeeded"
    assert result.patch is not None
    assert result.patch.schema_version == "cad-patch/v1"
    assert result.patch.run_id == "run-compile"
    assert result.patch.transaction_id == result.stable_hash
    assert result.patch.target_layer == "CODEX_PREVIEW"
    assert result.patch.save_current_dwg is False
    assert result.patch.forbidden_effects == ["dwg_save", "formal_layer_write"]
    assert [operation.semantic_object_id for operation in result.patch.operations] == [
        "desk",
        "monitor",
        "keyboard",
        "mouse",
        "vase",
    ]
    assert all(operation.action == "create" for operation in result.patch.operations)
    assert set(result.semantic_map.object_to_operation) == {"desk", "monitor", "keyboard", "mouse", "vase"}
    assert result.semantic_map == build_semantic_mapping(result.patch)
    assert result.impact.entity_count == sum(len(operation.primitives) for operation in result.patch.operations)
    assert result.impact.impact_bbox is not None


def test_left_mouse_and_double_monitor_compile_without_prompt_routes():
    left = compile_scene(standard_scene(mouse_side="left"), snapshot())
    dual = compile_scene(
        scene(
            [
                obj("desk", "desk", dimensions=Dimensions2D(width=1800, depth=800), placement=PlacementIntent(mode="absolute", base_point=(0, 0))),
                obj("monitor-a", "monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_left")),
                obj(
                    "monitor-b",
                    "monitor",
                    placement=PlacementIntent(mode="relative", on="desk", right_of="monitor-a", align_y="monitor-a", gap=40),
                ),
            ],
            scene_id="dual-monitor",
        ),
        snapshot(),
    )

    assert left.status == "succeeded"
    assert dual.status == "succeeded"
    assert [operation.semantic_object_id for operation in dual.patch.operations] == ["desk", "monitor-a", "monitor-b"]


def test_rotation_is_preserved_in_generated_primitives():
    result = compile_scene(standard_scene(rotation_deg=90), snapshot())

    assert result.status == "succeeded"
    assert result.relation_result.poses["monitor"].rotation_deg == 90
    monitor = next(operation for operation in result.patch.operations if operation.semantic_object_id == "monitor")
    monitor_pose = result.relation_result.poses["monitor"]
    assert monitor.primitives[0].geometry["points"][0][0] == monitor_pose.center[0] + 90.0


@pytest.mark.parametrize(
    ("bad_scene", "expected_reason"),
    [
        (
            scene(
                [
                    obj("desk", "desk", placement=PlacementIntent(mode="absolute", base_point=(0, 0))),
                    obj("printer", "printer", placement=PlacementIntent(mode="relative", on="desk", anchor="center")),
                ],
                scene_id="unknown",
            ),
            "unsupported_object_kind:printer",
        ),
        (
            scene(
                [
                    obj("desk", "desk", dimensions=Dimensions2D(width=900, depth=500), placement=PlacementIntent(mode="absolute", base_point=(0, 0))),
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
                scene_id="infeasible",
            ),
            "outside_surface:mouse",
        ),
    ],
)
def test_compile_blocks_unknown_object_and_infeasible_constraints(bad_scene: SceneSpec, expected_reason: str):
    result = compile_scene(bad_scene, snapshot())

    assert result.status == "blocked"
    assert result.patch is None
    assert expected_reason in result.blocking_reasons


def test_compile_blocks_nearby_collision():
    nearby = [DrawingEntitySnapshot(handle="N1", entity_type="LWPOLYLINE", layer="CODEX_PREVIEW", bbox=(450, 420, 950, 700))]

    result = compile_scene(standard_scene(), snapshot(nearby=nearby))

    assert result.status == "blocked"
    assert result.patch is None
    assert "nearby_collision:monitor:N1" in result.blocking_reasons


def test_compile_uses_snapshot_target_region_for_free_region_center_without_unbounded_growth():
    result = compile_scene(standard_scene(desk_mode="free_region_center"), snapshot(target_region=(1000, 2000, 3000, 3200)))

    assert result.status == "succeeded"
    assert result.target_region == (1000, 2000, 3000, 3200)
    assert result.relation_result.poses["desk"].center == (2000.0, 2600.0)

    blocked = compile_scene(standard_scene(desk_mode="free_region_center"), snapshot(target_region=None), allow_preview_parking_region=False)

    assert blocked.status == "blocked"
    assert blocked.patch is None
    assert blocked.blocking_reasons == ["target_region_unavailable"]


def test_compile_output_hash_is_stable_for_semantically_same_scene():
    first = compile_scene(standard_scene(), snapshot())
    second = compile_scene(standard_scene(), snapshot())

    assert first.status == "succeeded"
    assert first.stable_hash == second.stable_hash
    assert first.patch == second.patch


def test_compile_blocks_when_entity_budget_exceeded():
    result = compile_scene(standard_scene(), snapshot(), max_entity_budget=2)

    assert result.status == "blocked"
    assert result.patch is None
    assert result.blocking_reasons == ["max_entity_budget_exceeded"]


def test_impact_estimator_matches_patch_contents():
    result = compile_scene(standard_scene(), snapshot())

    impact = estimate_patch_impact(result.patch)

    assert impact == result.impact
    assert impact.entity_count > 0
    assert impact.impact_bbox == result.impact.impact_bbox


def test_scene_compiler_source_has_no_prompt_route_or_backend_access():
    source = (ROOT / "src" / "cad_agent_vnext" / "planning" / "scene_compiler.py").read_text(encoding="utf-8")

    forbidden = [
        "帮我画",
        "电脑桌",
        "computer_desk_scene",
        "desk_with_monitor_keyboard_mouse_vase",
        "backend.",
        "apply_patch",
        "KEYWORD",
    ]
    for token in forbidden:
        assert token not in source
