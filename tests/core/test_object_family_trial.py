from __future__ import annotations

import json
import unittest

from tests.helpers import temporary_artifact_dir


def _write_sofa_context(root) -> None:
    registry_path = root / "libraries" / "system_library" / "registry.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "assetId": "sofa_asset_package_seed",
                        "name": "沙发对象族资产包",
                        "category": "furniture.seating.sofas",
                        "aliases": ["沙发", "sofa"],
                        "tags": ["靠背", "坐垫", "扶手"],
                        "assetKind": "object_block",
                        "verificationStatus": "systemized",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    memory_path = root / "agents" / "cad_designer" / "training_memory.json"
    memory_path.parent.mkdir(parents=True)
    memory_path.write_text(
        json.dumps(
            {
                "agentId": "cad_designer",
                "lessons": [
                    {
                        "capabilityId": "sofa-symbol",
                        "summary": "沙发必须拆出靠背、坐垫和扶手，避免只画一个外框。",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    failure_path = root / "projects" / "case_sofa" / "runs" / "round1_failure_notes.json"
    failure_path.parent.mkdir(parents=True)
    failure_path.write_text(
        json.dumps({"case_id": "case_sofa", "root_cause": "沙发靠背与坐垫重叠，缺少 readback 检查。"}, ensure_ascii=False),
        encoding="utf-8",
    )


class ObjectFamilyTrialTests(unittest.TestCase):
    def test_sofa_trial_builds_rag_candidates_valid_cad_plan_and_readback_contract(self) -> None:
        from core.assets.object_family_trial import build_object_family_trial
        from core.plan_engine.validate_plan import validate_plan

        with temporary_artifact_dir("object_family_trial") as root:
            _write_sofa_context(root)

            trial = build_object_family_trial("复用沙发时检查靠背、坐垫和扶手", object_family="sofa", project_root=root)

        self.assertEqual(trial["kind"], "object_family_trial")
        self.assertEqual(trial["objectFamily"], "sofa")
        self.assertEqual(trial["status"], "cad_plan_draft_ready")
        self.assertEqual(trial["retrievalPack"]["sourceSummary"]["reference_asset"], 0)
        self.assertGreaterEqual(len(trial["designCandidates"]), 2)
        self.assertLessEqual(len(trial["designCandidates"]), 3)
        self.assertEqual(trial["selectedCandidate"]["candidateId"], trial["designCandidates"][0]["candidateId"])
        self.assertIn("back", trial["selectedCandidate"]["requiredParts"])
        self.assertIn("seat", trial["selectedCandidate"]["requiredParts"])
        self.assertIn("arm_left", trial["selectedCandidate"]["requiredParts"])

        cad_plan = trial["cadPlanDraft"]
        self.assertEqual(validate_plan(cad_plan), [])
        self.assertTrue(cad_plan["needs_confirmation"])
        self.assertEqual(cad_plan["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(cad_plan["intent"], "draw_symbol_glyph")
        self.assertEqual(trial["dryRunReport"]["status"], "valid")
        self.assertEqual(trial["executionPlan"]["cadWritePolicy"], "not_executed_no_cad")
        self.assertIn("created_handles", trial["readbackEvidenceRequirements"]["requiredFields"])
        self.assertIn("real_cad_geometry", trial["evidenceBoundary"]["notChecked"])

    def test_non_sofa_trial_blocks_before_cad_plan_claims(self) -> None:
        from core.assets.object_family_trial import build_object_family_trial

        with temporary_artifact_dir("object_family_trial_blocked") as root:
            trial = build_object_family_trial("先试一下床对象族", object_family="bed", project_root=root)

        self.assertEqual(trial["status"], "unsupported_object_family")
        self.assertNotIn("cadPlanDraft", trial)
        self.assertIn("sofa_only_mvp", trial["blockingReasons"])
        self.assertIn("no_cad_written", trial["evidenceBoundary"]["checked"])


if __name__ == "__main__":
    unittest.main()
