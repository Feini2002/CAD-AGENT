from __future__ import annotations

import json
import unittest

from core.orchestrator.request_context import build_request_context
from core.orchestrator.route_audit_report import build_route_audit_report
from core.orchestrator.scene_registry import load_scene_registry
from core.orchestrator.workflow_dispatch import orchestrate_request
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class RouteAuditReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_scene_registry()

    def test_orchestrate_writes_route_audit_fixture(self) -> None:
        context = build_request_context(
            context_id="req-audit-symbol",
            request_kind="draw",
            user_request="绘制物件符号",
            scene_hint="no_scene",
            available_inputs=["object_spec"],
            input_paths={"object_spec": "examples/object_specs/desk_1400x700.json"},
            allow_cad=True,
        )
        output_dir = artifact_path("route_audit", "symbol_glyph")
        report = orchestrate_request(
            context,
            output_dir=output_dir,
            execute=True,
        )
        audit = report["route_audit_report"]
        self.assertTrue((output_dir / "route_audit_report.json").is_file())
        self.assertEqual(audit["routing_summary"]["selected_workflow_id"], "object_symbol_glyph")
        self.assertFalse(audit["routing_summary"]["scene_module_enabled"])
        self.assertIn("dry_run_valid_plan_only", audit["evidence"]["available"])
        self.assertIn("readback_geometry_verified", audit["evidence"]["deferred"])

    def test_manifest_scene_audit_records_module_enabled(self) -> None:
        context = build_request_context(
            context_id="req-audit-fitout",
            request_kind="layout",
            user_request="工装布局",
            project_manifest={"scene_id": "commercial_fitout"},
            available_inputs=["shell_model"],
        )
        orchestration = orchestrate_request(context, execute=False)
        audit = build_route_audit_report(context, orchestration, registry=self.registry)
        self.assertEqual(audit["routing_summary"]["activated_scene_id"], "commercial_fitout")
        self.assertTrue(audit["routing_summary"]["scene_module_enabled"])
        self.assertEqual(audit["scene"]["maturity"], "scaffold")
        self.assertIn("scene_product_delivery", audit["evidence"]["not_claimable"])

    def test_blocked_request_lists_deferred_execution(self) -> None:
        context = build_request_context(
            context_id="req-audit-blocked",
            request_kind="draw",
            user_request="",
        )
        orchestration = orchestrate_request(context, execute=False)
        audit = build_route_audit_report(context, orchestration, registry=self.registry)
        self.assertNotEqual(audit["routing_summary"]["orchestrator_status"], "ready")
        self.assertTrue(audit["deferred_items"])
        self.assertIn("workflow_execution", {item["item"] for item in audit["deferred_items"]})

    def test_example_audit_validates_against_schema(self) -> None:
        context = build_request_context(
            context_id="req-audit-schema",
            request_kind="proposal",
            user_request="柜体方案",
            available_inputs=["design_brief"],
            input_paths={"design_brief": "examples/design_briefs/minimal_cabinet_brief.json"},
        )
        orchestration = orchestrate_request(context, execute=False)
        audit = build_route_audit_report(context, orchestration, registry=self.registry)
        example_path = PROJECT_ROOT / "examples" / "orchestrator" / "sample_route_audit_report.json"
        self.assertEqual(validate_json(PROJECT_ROOT / "core/schemas/route_audit_report.schema.json", example_path), [])

        generated_path = artifact_path("route_audit", "schema_fixture") / "sample_route_audit_report.json"
        generated_path.parent.mkdir(parents=True, exist_ok=True)
        generated_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        errors = validate_json(PROJECT_ROOT / "core/schemas/route_audit_report.schema.json", generated_path)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
