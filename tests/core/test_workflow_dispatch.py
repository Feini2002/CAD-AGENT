from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.orchestrator.request_context import build_request_context
from core.orchestrator.workflow_dispatch import (
    DISPATCH_BLOCKED,
    DISPATCH_READY,
    execute_workflow_dispatch,
    load_workflow_routes,
    orchestrate_request,
    resolve_workflow_route,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class WorkflowDispatchTests(unittest.TestCase):
    def test_draw_object_spec_resolves_symbol_glyph_route(self) -> None:
        context = build_request_context(
            context_id="req-dispatch-draw",
            request_kind="draw",
            user_request="绘制办公桌符号",
            available_inputs=["object_spec"],
            input_paths={"object_spec": "examples/object_specs/desk_1400x700.json"},
            allow_cad=True,
        )
        dispatch = resolve_workflow_route(context)
        self.assertEqual(dispatch["status"], DISPATCH_READY)
        self.assertEqual(dispatch["workflow_id"], "object_symbol_glyph")
        self.assertFalse(dispatch["requires_cad"])

    def test_proposal_resolves_non_cad_loop(self) -> None:
        context = build_request_context(
            context_id="req-dispatch-proposal",
            request_kind="proposal",
            user_request="生成柜体方案",
            available_inputs=["design_brief", "drawing_model", "object_spec"],
            input_paths={
                "design_brief": "examples/design_briefs/minimal_cabinet_brief.json",
                "drawing_model": "examples/drawing_models/minimal_empty_room.json",
                "object_spec": "examples/object_specs/minimal_cabinet_object.json",
            },
        )
        dispatch = resolve_workflow_route(context)
        self.assertEqual(dispatch["workflow_id"], "proposal_non_cad_loop")
        self.assertEqual(dispatch["entrypoint"], "core.workflows.non_cad_pipeline:run_non_cad_pipeline")

    def test_orchestrate_executes_symbol_glyph_non_cad(self) -> None:
        context = build_request_context(
            context_id="req-orch-symbol",
            request_kind="draw",
            user_request="绘制物件符号",
            scene_hint="no_scene",
            available_inputs=["object_spec"],
            input_paths={"object_spec": "examples/object_specs/desk_1400x700.json"},
            allow_cad=True,
        )
        report = orchestrate_request(
            context,
            output_dir=artifact_path("workflow_dispatch", "symbol_glyph"),
            execute=True,
        )
        self.assertTrue(report["may_execute"])
        execution = report["execution"]
        self.assertIsNotNone(execution)
        assert execution is not None
        self.assertEqual(execution["status"], "ok")
        self.assertEqual(execution["workflow_id"], "object_symbol_glyph")

    def test_orchestrate_runs_non_cad_pipeline_via_entrypoint(self) -> None:
        context = build_request_context(
            context_id="req-orch-noncad",
            request_kind="proposal",
            user_request="非CAD全链路",
            available_inputs=["design_brief"],
            input_paths={
                "workflow": "examples/workflows/full_non_cad_core_loop.json",
                "design_brief": "examples/design_briefs/minimal_cabinet_brief.json",
            },
        )
        dispatch = resolve_workflow_route(context)
        self.assertEqual(dispatch["workflow_id"], "proposal_non_cad_loop")
        result = execute_workflow_dispatch(
            dispatch,
            context,
            output_dir=artifact_path("workflow_dispatch", "non_cad_loop"),
        )
        self.assertEqual(result["status"], "ok")
        self.assertIn("cad_plan", result["artifacts"])

    def test_blocked_gate_skips_execution(self) -> None:
        context = build_request_context(
            context_id="req-orch-blocked",
            request_kind="draw",
            user_request="",
        )
        report = orchestrate_request(
            context,
            output_dir=artifact_path("workflow_dispatch", "blocked"),
            execute=True,
        )
        self.assertFalse(report["may_execute"])
        self.assertEqual(report["workflow_dispatch"]["status"], DISPATCH_BLOCKED)
        self.assertEqual(report["execution"]["status"], "skipped")

    def test_cad_route_deferred_without_include_cad(self) -> None:
        context = build_request_context(
            context_id="req-cad-deferred",
            request_kind="draw",
            user_request="执行计划",
            available_inputs=["cad_plan"],
            input_paths={"cad_plan": "examples/plans/insert_block_alpha_test.json"},
            allow_cad=True,
        )
        dispatch = resolve_workflow_route(context)
        self.assertEqual(dispatch["workflow_id"], "object_cad_plan_execute")
        result = execute_workflow_dispatch(
            dispatch,
            context,
            output_dir=artifact_path("workflow_dispatch", "cad_deferred"),
            include_cad=False,
        )
        self.assertEqual(result["status"], "deferred")

    def test_workflow_routes_fixture_loads(self) -> None:
        table = load_workflow_routes()
        self.assertGreaterEqual(len(table["routes"]), 5)


if __name__ == "__main__":
    unittest.main()
