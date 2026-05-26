from __future__ import annotations

import unittest

from core.orchestrator.activation_policy import (
    ACTIVATION_MANIFEST_SPECIFIED,
    ACTIVATION_NEEDS_CLARIFICATION,
    ACTIVATION_NO_SCENE,
    ACTIVATION_SCENE_ACTIVE,
    evaluate_scene_activation,
    merge_activation_into_request_gate,
)
from core.orchestrator.request_context import (
    GATE_STATUS_NEEDS_CLARIFICATION,
    GATE_STATUS_READY,
    build_request_context,
    evaluate_request_gate,
)
from core.orchestrator.scene_registry import DEFAULT_SCENE_ID, load_scene_registry


class ActivationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_scene_registry()

    def test_generic_request_defaults_to_no_scene(self) -> None:
        context = build_request_context(
            context_id="req-generic",
            request_kind="general",
            user_request="帮我生成一个方案",
            scene_hint="no_scene",
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activation_status"], ACTIVATION_NO_SCENE)
        self.assertEqual(report["activated_scene_id"], DEFAULT_SCENE_ID)
        self.assertFalse(report["may_use_scene_module"])
        self.assertTrue(report["must_use_core_workflow"])

    def test_manifest_specified_scene(self) -> None:
        context = build_request_context(
            context_id="req-manifest",
            request_kind="layout",
            user_request="工装门店布局",
            project_manifest={"scene_id": "commercial_fitout", "project_id": "demo"},
            available_inputs=["shell_model"],
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activation_status"], ACTIVATION_MANIFEST_SPECIFIED)
        self.assertEqual(report["activated_scene_id"], "commercial_fitout")
        self.assertTrue(report["may_use_scene_module"])

    def test_single_trigger_activates_office(self) -> None:
        context = build_request_context(
            context_id="req-office",
            request_kind="layout",
            user_request="开放办公室工位布局",
            scene_hint="no_scene",
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activation_status"], ACTIVATION_SCENE_ACTIVE)
        self.assertEqual(report["activated_scene_id"], "office")

    def test_multiple_triggers_need_clarification(self) -> None:
        context = build_request_context(
            context_id="req-ambiguous",
            request_kind="layout",
            user_request="办公室和住宅餐厅混合布局",
            scene_hint="no_scene",
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activation_status"], ACTIVATION_NEEDS_CLARIFICATION)
        self.assertEqual(report["activated_scene_id"], DEFAULT_SCENE_ID)
        self.assertTrue(report["clarification_required"])
        self.assertGreaterEqual(len(report["candidate_scene_ids"]), 2)

    def test_scene_hint_overrides_when_no_manifest(self) -> None:
        context = build_request_context(
            context_id="req-hint",
            request_kind="general",
            user_request="",
            scene_hint="residential",
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activated_scene_id"], "residential")
        self.assertTrue(report["may_use_scene_module"])

    def test_merge_activation_blocks_dispatch_on_clarification(self) -> None:
        context = build_request_context(
            context_id="req-merge",
            request_kind="general",
            user_request="办公和家装",
        )
        gate = evaluate_request_gate(context)
        self.assertEqual(gate["status"], GATE_STATUS_READY)
        activation = evaluate_scene_activation(context, self.registry)
        merged = merge_activation_into_request_gate(context, gate, activation)
        self.assertEqual(merged["status"], GATE_STATUS_NEEDS_CLARIFICATION)
        self.assertFalse(merged["may_dispatch_workflow"])

    def test_unknown_manifest_scene_is_blocked(self) -> None:
        context = build_request_context(
            context_id="req-bad-manifest",
            request_kind="general",
            user_request="test",
            project_manifest={"scene_id": "unknown_scene"},
        )
        report = evaluate_scene_activation(context, self.registry)
        self.assertEqual(report["activation_status"], "blocked")
        self.assertEqual(report["activated_scene_id"], DEFAULT_SCENE_ID)
        self.assertFalse(report["may_use_scene_module"])


if __name__ == "__main__":
    unittest.main()
