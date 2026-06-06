from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = PROJECT_ROOT / "agents" / "pipeline"
SOFA_CASE = PROJECT_ROOT / "projects" / "residential_sofa_2seat_20260528"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PipelineVisualContractTests(unittest.TestCase):
    def test_manifest_registers_visual_contract_agents_and_flow(self) -> None:
        manifest = load_json(PIPELINE_ROOT / "pipeline_manifest.json")

        agent_ids = {agent["agent_id"] for agent in manifest["agents"]}
        self.assertTrue(
            {
                "pipeline_context_curator",
                "pipeline_asset_retriever",
                "pipeline_asset_governor",
                "pipeline_orchestrator",
                "pipeline_design_director",
                "pipeline_style_generator",
                "pipeline_visual_intent",
                "pipeline_intent",
                "pipeline_execute",
                "pipeline_audit",
                "pipeline_visual_acceptance_reviewer",
                "pipeline_design_reviewer",
                "pipeline_repair",
                "pipeline_delivery",
                "pipeline_learning_promoter",
            }.issubset(agent_ids)
        )

        self.assertEqual(
            manifest["orchestration"]["default_flow"],
            [
                "pipeline_context_curator",
                "pipeline_asset_retriever",
                "pipeline_asset_governor",
                "pipeline_orchestrator",
                "pipeline_design_director",
                "pipeline_style_generator",
                "pipeline_visual_intent",
                "pipeline_intent",
                "pipeline_execute",
                "pipeline_audit",
                "pipeline_visual_acceptance_reviewer",
                "pipeline_design_reviewer",
                "pipeline_repair",
                "pipeline_delivery",
                "pipeline_learning_promoter",
            ],
        )

    def test_manifest_blocks_reference_match_without_visual_contract(self) -> None:
        manifest = load_json(PIPELINE_ROOT / "pipeline_manifest.json")

        gates = manifest["orchestration"]["hard_gates"]
        reference_gate = gates["reference_match"]
        self.assertEqual(reference_gate["blocks"], ["pipeline_execute"])
        self.assertIn("style_target", reference_gate["requires"])
        self.assertIn("visual_parts", reference_gate["requires"])
        self.assertIn("visual_style_brief", reference_gate["requires"])

        delivery_gate = gates["delivery"]
        self.assertIn("agent_review_all_pass", delivery_gate["requires"])
        self.assertIn("audit_pass_or_approximate_ok", delivery_gate["requires"])

    def test_manifest_tracks_required_round_artifacts(self) -> None:
        manifest = load_json(PIPELINE_ROOT / "pipeline_manifest.json")
        artifacts = manifest["artifacts"]

        for key in [
            "context_pack",
            "route",
            "visual_parts",
            "visual_style_brief",
            "cad_plan",
            "style_compare",
            "agent_review",
            "repair_plan",
            "learning_patch",
        ]:
            with self.subTest(key=key):
                self.assertIn(key, artifacts)

    def test_new_agent_contract_files_exist(self) -> None:
        expected = {
            "context_curator/agent.json": ("pipeline_context_curator", "roundN_context_pack.json"),
            "visual_intent/agent.json": ("pipeline_visual_intent", "roundN_visual_parts.json"),
            "learning_promoter/agent.json": ("pipeline_learning_promoter", "roundN_learning_patch.json"),
        }

        for relative, (agent_id, required_output) in expected.items():
            with self.subTest(agent=relative):
                data = load_json(PIPELINE_ROOT / relative)
                self.assertEqual(data["id"], agent_id)
                self.assertIn(required_output, data["outputs"])
                self.assertIn("must_not", data)

    def test_execute_agent_consumes_visual_parts_before_freeform_intent(self) -> None:
        execute = load_json(PIPELINE_ROOT / "execute" / "agent.json")

        self.assertEqual(execute["inputs"][0], "runs/roundN_visual_parts.json")
        self.assertIn("draw_structures_not_declared_in_visual_parts", execute["must_not"])

    def test_audit_repair_delivery_keep_visual_gate_artifacts(self) -> None:
        audit = load_json(PIPELINE_ROOT / "audit" / "agent.json")
        repair = load_json(PIPELINE_ROOT / "repair" / "agent.json")
        delivery = load_json(PIPELINE_ROOT / "delivery" / "agent.json")

        self.assertIn("runs/roundN_visual_parts.json", audit["inputs"])
        self.assertIn("runs/roundN_style_compare.md", audit["outputs"])
        self.assertIn("machine_green_delivery", audit["must_not"])

        self.assertIn("runs/roundN_style_compare.md", repair["inputs"])
        self.assertIn("runs/roundN_visual_parts.json", repair["inputs"])
        self.assertIn("runs/roundN_repair_plan.json", repair["outputs"])

        self.assertIn("runs/roundN_style_compare.md", delivery["inputs"])
        self.assertIn("runs/roundN_visual_parts.json", delivery["inputs"])
        self.assertIn("delivery_without_style_compare", delivery["must_not"])

    def test_sofa_round12_visual_parts_declares_required_components(self) -> None:
        visual_parts = load_json(SOFA_CASE / "runs" / "round12_visual_parts.json")

        self.assertEqual(visual_parts["object"], "sofa_plan")
        self.assertEqual(visual_parts["seat_count"], 2)
        part_ids = {part["id"] for part in visual_parts["parts"]}
        self.assertEqual(
            part_ids,
            {
                "arm_left",
                "arm_right",
                "seat_left",
                "seat_right",
                "back_left",
                "back_right",
                "base_rail",
            },
        )
        self.assertTrue(all(part.get("closed") is True for part in visual_parts["parts"]))
        self.assertIn("closed_outer_shell", visual_parts["forbidden"])
        self.assertIn("split_line_as_main_structure", visual_parts["forbidden"])

    def test_residential_rules_include_visual_first_sofa_contract(self) -> None:
        rules = (PROJECT_ROOT / "agents" / "residential" / "rules.md").read_text(encoding="utf-8")

        self.assertIn("参照款沙发 plan", rules)
        self.assertIn("visual_parts.json", rules)
        self.assertIn("closed_outer_shell", rules)
        self.assertIn("split_line_as_main_structure", rules)


if __name__ == "__main__":
    unittest.main()
