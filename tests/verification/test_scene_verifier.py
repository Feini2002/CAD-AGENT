from __future__ import annotations

from cad_agent.adapters.fake_backend import FakeCadBackend
from cad_agent.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.primitives import Primitive
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.scene_compiler import CompileSceneResult, compile_scene
from cad_agent.verification.repair_planner import plan_scene_repair
from cad_agent.verification.scene_verifier import verify_scene_execution


def snapshot(*, nearby=None) -> DrawingSnapshot:
    return DrawingSnapshot(
        schema_version="drawing-snapshot/v1",
        run_id="run-verify",
        document_id="fake-doc",
        units="mm",
        current_space="model",
        active_layer="CODEX_PREVIEW",
        saved=False,
        target_region=(0, 0, 2000, 1200),
        nearby_entities=nearby or [],
        snapshot_hash="snapshot:verify",
    )


def obj(object_id: str, kind: str, *, dimensions: Dimensions2D | None = None, placement: PlacementIntent) -> SceneObjectSpec:
    return SceneObjectSpec(id=object_id, kind=kind, dimensions=dimensions, placement=placement)


def standard_scene() -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id="run-verify",
        scene_id="verify-standard",
        units="mm",
        view="plan_2d",
        objects=[
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
                placement=PlacementIntent(mode="relative", on="desk", right_of="keyboard", align_y="keyboard", gap=40),
            ),
            obj("vase", "vase", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_right")),
        ],
    )


def compile_standard() -> tuple[SceneSpec, DrawingSnapshot, CompileSceneResult]:
    scene = standard_scene()
    snap = snapshot()
    compiled = compile_scene(scene, snap)
    assert compiled.status == "succeeded"
    assert compiled.patch is not None
    return scene, snap, compiled


def execute_standard():
    scene, snap, compiled = compile_standard()
    backend = FakeCadBackend()
    receipt = backend.apply_patch(compiled.patch)
    readback = backend.readback(transaction_id=compiled.patch.transaction_id)
    return scene, snap, compiled, backend, receipt, readback


def operation_for(compiled: CompileSceneResult, semantic_id: str) -> PatchOperation:
    assert compiled.patch is not None
    return next(operation for operation in compiled.patch.operations if operation.semantic_object_id == semantic_id)


def update_patch(
    *,
    run_id: str,
    transaction_id: str,
    semantic_id: str,
    target_handles: list[str],
    primitives: list[Primitive],
) -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id=run_id,
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=[
            PatchOperation(
                op_id=f"update:{semantic_id}",
                action="update",
                semantic_object_id=semantic_id,
                target_handles=target_handles,
                primitives=primitives,
            )
        ],
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def delete_patch(*, run_id: str, transaction_id: str, semantic_id: str, target_handles: list[str]) -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id=run_id,
        transaction_id=transaction_id,
        target_layer="CODEX_PREVIEW",
        operations=[
            PatchOperation(
                op_id=f"delete:{semantic_id}",
                action="delete",
                semantic_object_id=semantic_id,
                target_handles=target_handles,
            )
        ],
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def circle_primitive(semantic_id: str, *, center: tuple[float, float], radius: float) -> Primitive:
    return Primitive(
        primitive_id=f"{semantic_id}:bad-body",
        semantic_object_id=semantic_id,
        primitive_type="circle",
        geometry={"center": [center[0], center[1], 0.0], "radius": radius},
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type="CIRCLE",
    )


def check_ids(report) -> set[str]:
    return {check.check_id for check in report.checks if check.status != "passed"}


def test_fake_backend_execution_verifies_passed_scene():
    scene, snap, compiled, _backend, receipt, readback = execute_standard()

    report = verify_scene_execution(scene=scene, compile_result=compiled, receipt=receipt, readback=readback, snapshot=snap)

    assert report.schema_version == "verification-report/v1"
    assert report.overall_status == "passed"
    assert report.blocking_reasons == []
    assert "preview_geometry_verified" in report.allowed_claims


def test_receipt_integrity_blocks_wrong_layer_and_saved_current_dwg():
    scene, snap, compiled = compile_standard()
    backend = FakeCadBackend(failure_mode="wrong_layer")
    wrong_layer_receipt = backend.apply_patch(compiled.patch)

    wrong_layer_report = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=wrong_layer_receipt,
        readback=wrong_layer_receipt,
        snapshot=snap,
    )

    assert wrong_layer_report.overall_status == "blocked"
    assert any(reason.startswith("wrong_layer:") for reason in wrong_layer_report.blocking_reasons)

    saved_receipt = wrong_layer_receipt.model_copy(update={"saved_current_dwg": True})
    saved_report = verify_scene_execution(scene=scene, compile_result=compiled, receipt=saved_receipt, readback=saved_receipt, snapshot=snap)

    assert saved_report.overall_status == "blocked"
    assert "saved_current_dwg_true" in saved_report.blocking_reasons


def test_verifier_locates_missing_monitor_and_mouse_keyboard_overlap():
    scene, snap, compiled, backend, receipt, _readback = execute_standard()
    monitor_handles = receipt.semantic_to_handles["monitor"]
    backend.apply_patch(
        delete_patch(
            run_id=scene.run_id,
            transaction_id="damage-delete-monitor",
            semantic_id="monitor",
            target_handles=monitor_handles,
        )
    )
    missing_report = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=receipt,
        readback=backend.readback(transaction_id=compiled.patch.transaction_id),
        snapshot=snap,
    )

    assert "missing_object:monitor" in missing_report.blocking_reasons
    assert "missing_object" in check_ids(missing_report)

    keyboard_body = operation_for(compiled, "keyboard").primitives[:1]
    backend.apply_patch(
        update_patch(
            run_id=scene.run_id,
            transaction_id="damage-mouse-overlap",
            semantic_id="mouse",
            target_handles=receipt.semantic_to_handles["mouse"],
            primitives=keyboard_body,
        )
    )
    overlap_report = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=receipt,
        readback=backend.readback(transaction_id=compiled.patch.transaction_id),
        snapshot=snap,
    )

    assert "severe_overlap:keyboard:mouse" in overlap_report.blocking_reasons


def test_repair_planner_updates_only_failed_mouse_and_passes_after_fake_backend_apply():
    scene, snap, compiled, backend, receipt, _readback = execute_standard()
    keyboard_body = operation_for(compiled, "keyboard").primitives[:1]
    backend.apply_patch(
        update_patch(
            run_id=scene.run_id,
            transaction_id="damage-mouse",
            semantic_id="mouse",
            target_handles=receipt.semantic_to_handles["mouse"],
            primitives=keyboard_body,
        )
    )
    failed = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=receipt,
        readback=backend.readback(transaction_id=compiled.patch.transaction_id),
        snapshot=snap,
    )

    repair = plan_scene_repair(scene=scene, compile_result=compiled, verification_report=failed, prior_receipt=receipt)

    assert repair.status == "succeeded"
    assert repair.patch is not None
    assert [operation.semantic_object_id for operation in repair.patch.operations] == ["mouse"]
    assert repair.patch.operations[0].action == "update"
    assert repair.patch.operations[0].target_handles == receipt.semantic_to_handles["mouse"]

    repair_receipt = backend.apply_patch(repair.patch)
    repaired = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=repair_receipt,
        readback=backend.readback(transaction_id=repair.patch.transaction_id),
        snapshot=snap,
    )

    assert repaired.overall_status == "passed"


def test_repair_planner_adds_missing_monitor_without_redrawing_whole_scene():
    scene, snap, compiled, backend, receipt, _readback = execute_standard()
    backend.apply_patch(
        delete_patch(
            run_id=scene.run_id,
            transaction_id="damage-delete-monitor",
            semantic_id="monitor",
            target_handles=receipt.semantic_to_handles["monitor"],
        )
    )
    failed = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=receipt,
        readback=backend.readback(transaction_id=compiled.patch.transaction_id),
        snapshot=snap,
    )

    repair = plan_scene_repair(scene=scene, compile_result=compiled, verification_report=failed, prior_receipt=receipt)

    assert repair.status == "succeeded"
    assert repair.patch is not None
    assert [operation.semantic_object_id for operation in repair.patch.operations] == ["monitor"]
    assert repair.patch.operations[0].action == "create"
    assert repair.patch.operations[0].target_handles == []

    repair_receipt = backend.apply_patch(repair.patch)
    repaired = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=repair_receipt,
        readback=backend.readback(transaction_id=repair.patch.transaction_id),
        snapshot=snap,
    )

    assert repaired.overall_status == "passed"


def test_vase_outside_surface_repairs_only_vase():
    scene, snap, compiled, backend, receipt, _readback = execute_standard()
    backend.apply_patch(
        update_patch(
            run_id=scene.run_id,
            transaction_id="damage-vase-outside",
            semantic_id="vase",
            target_handles=receipt.semantic_to_handles["vase"],
            primitives=[circle_primitive("vase", center=(5000, 5000), radius=50)],
        )
    )
    failed = verify_scene_execution(
        scene=scene,
        compile_result=compiled,
        receipt=receipt,
        readback=backend.readback(transaction_id=compiled.patch.transaction_id),
        snapshot=snap,
    )

    assert "outside_surface:vase:desk" in failed.blocking_reasons

    repair = plan_scene_repair(scene=scene, compile_result=compiled, verification_report=failed, prior_receipt=receipt)

    assert repair.status == "succeeded"
    assert repair.patch is not None
    assert [operation.semantic_object_id for operation in repair.patch.operations] == ["vase"]
    assert repair.patch.operations[0].action == "update"


def test_safety_failure_is_not_repaired_and_nearby_handle_change_blocks():
    nearby = [DrawingEntitySnapshot(handle="N1", entity_type="LWPOLYLINE", layer="A-WALL", bbox=(10, 10, 20, 20))]
    scene = standard_scene()
    snap = snapshot(nearby=nearby)
    compiled = compile_scene(scene, snap)
    assert compiled.status == "succeeded"
    backend = FakeCadBackend()
    receipt = backend.apply_patch(compiled.patch)
    bad_receipt = receipt.model_copy(update={"updated_handles": ["N1"]})

    failed = verify_scene_execution(scene=scene, compile_result=compiled, receipt=bad_receipt, readback=bad_receipt, snapshot=snap)
    repair = plan_scene_repair(scene=scene, compile_result=compiled, verification_report=failed, prior_receipt=bad_receipt)

    assert failed.overall_status == "blocked"
    assert "nearby_handle_modified:N1" in failed.blocking_reasons
    assert repair.status == "blocked"
    assert repair.patch is None
    assert "safety_failure_not_repairable" in repair.blocking_reasons
