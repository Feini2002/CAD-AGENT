from __future__ import annotations

import json
import unittest

from core.orchestrator.request_context import (
    GATE_STATUS_BLOCKED,
    GATE_STATUS_NEEDS_CLARIFICATION,
    GATE_STATUS_READY,
    build_request_context,
    evaluate_request_gate,
    gate_blocks_cad_execution,
    validate_request_context,
)
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class RequestContextTests(unittest.TestCase):
    def test_example_request_context_validates_against_schema(self) -> None:
        path = PROJECT_ROOT / "examples/orchestrator/draw_desk_request_context.json"
        errors = validate_json(PROJECT_ROOT / "core/schemas/request_context.schema.json", path)
        self.assertEqual(errors, [])

    def test_draw_context_with_object_spec_is_ready_for_cad(self) -> None:
        context = json.loads(
            (PROJECT_ROOT / "examples/orchestrator/draw_desk_request_context.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_request_context(context), [])
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_READY)
        self.assertTrue(gate["may_dispatch_workflow"])
        self.assertTrue(gate["may_execute_cad"])
        self.assertFalse(gate_blocks_cad_execution(gate))

    def test_missing_inputs_blocks_without_cad_dispatch(self) -> None:
        context = json.loads(
            (PROJECT_ROOT / "examples/orchestrator/blocked_missing_input_request_context.json").read_text(
                encoding="utf-8"
            )
        )
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_BLOCKED)
        self.assertFalse(gate["may_dispatch_workflow"])
        self.assertFalse(gate["may_execute_cad"])
        self.assertTrue(gate_blocks_cad_execution(gate))
        self.assertIn("missing user_request and structured inputs", gate["blocked_reasons"][0])

    def test_needs_clarification_blocks_even_with_inputs(self) -> None:
        context = build_request_context(
            context_id="req-clarify",
            request_kind="draw",
            user_request="画一张图",
            available_inputs=["object_spec"],
            allow_cad=True,
            needs_clarification=True,
            clarification_questions=["请确认桌面尺寸"],
        )
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_NEEDS_CLARIFICATION)
        self.assertFalse(gate["may_execute_cad"])
        self.assertFalse(gate["may_dispatch_workflow"])

    def test_allow_cad_false_blocks_draw_kind(self) -> None:
        context = build_request_context(
            context_id="req-no-cad",
            request_kind="draw",
            user_request="绘制办公桌",
            available_inputs=["object_spec"],
            allow_cad=False,
        )
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_BLOCKED)
        self.assertTrue(any("allow_cad" in reason for reason in gate["blocked_reasons"]))

    def test_project_sample_requires_manifest(self) -> None:
        context = build_request_context(
            context_id="req-sample",
            request_kind="project_sample",
            user_request="跑项目样本 CAD 检查",
            allow_cad=True,
        )
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_BLOCKED)
        self.assertTrue(any("project_sample_manifest" in reason for reason in gate["blocked_reasons"]))


if __name__ == "__main__":
    unittest.main()
