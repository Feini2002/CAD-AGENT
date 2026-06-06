from __future__ import annotations

import json
import unittest

from tests.helpers import temporary_artifact_dir


def _write_sofa_seed(root) -> None:
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


class AssetPromotionCandidateTests(unittest.TestCase):
    def test_sofa_trial_proposes_reviewed_candidates_without_mutating_targets(self) -> None:
        from core.assets.object_family_trial import build_object_family_trial
        from core.assets.promotion_candidates import build_asset_intelligence_promotion_candidates

        with temporary_artifact_dir("asset_promotion_candidates") as root:
            _write_sofa_seed(root)
            trial = build_object_family_trial("复用沙发时检查靠背、坐垫和扶手", project_root=root)

            report = build_asset_intelligence_promotion_candidates(trial)

        self.assertEqual(report["kind"], "asset_intelligence_promotion_candidates")
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["review"]["requiredAgentId"], "pipeline_learning_promoter")
        self.assertEqual(report["mutatedTargets"], [])
        self.assertEqual(report["promotionGate"]["decisions"]["updateTrainingSource"]["status"], "not_required")
        self.assertEqual(report["promotionGate"]["decisions"]["updateTaskRules"]["status"], "needs_reviewed_package")
        self.assertEqual(report["promotionGate"]["decisions"]["updateChecker"]["status"], "needs_reviewed_package")

        candidate_types = {candidate["candidateType"] for candidate in report["candidates"]}
        self.assertEqual(candidate_types, {"task_rule", "checker", "asset_candidate", "training_item"})
        self.assertTrue(all(candidate["status"] in {"needs_reviewed_package", "candidate_only"} for candidate in report["candidates"]))
        asset_candidate = next(candidate for candidate in report["candidates"] if candidate["candidateType"] == "asset_candidate")
        self.assertIn("real_cad_replay", asset_candidate["blockedUntil"])
        self.assertIn("no_cad_written", report["evidenceBoundary"]["checked"])

    def test_promotion_candidates_block_when_trial_is_not_ready(self) -> None:
        from core.assets.promotion_candidates import build_asset_intelligence_promotion_candidates

        report = build_asset_intelligence_promotion_candidates(
            {
                "kind": "object_family_trial",
                "status": "unsupported_object_family",
                "objectFamily": "bed",
                "blockingReasons": ["sofa_only_mvp"],
            }
        )

        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["candidates"], [])
        self.assertEqual(report["mutatedTargets"], [])
        self.assertIn("source_trial_not_ready", report["blockingReasons"])


if __name__ == "__main__":
    unittest.main()
