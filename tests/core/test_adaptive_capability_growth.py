from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


class AdaptiveCapabilityGrowthTests(unittest.TestCase):
    def test_profile_loader_consumes_local_lessons_and_marks_unchecked_boundaries(self) -> None:
        from core.training.capability_growth_profile import build_capability_growth_profile

        programs = [
            {
                "capabilityId": "cad-layer-lineweight-standard",
                "name": "线宽 / 线型标准",
                "focus": "线宽、线型、打印样式",
            }
        ]
        with temporary_artifact_dir("adaptive_growth_profile") as root:
            profile_source = root / "profile.json"
            profile_source.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "profiles": {
                            "cad-layer-lineweight-standard": {
                                "profileVersion": "lesson-v2",
                                "minimumExpressionLevel": "growth",
                                "transferableLessons": [
                                    {
                                        "lessonId": "lineweight-distinct-samples",
                                        "summary": "线宽训练必须画出可回读的不同 Lineweight。",
                                        "positiveExample": "70 / 35 / 13 三档样线",
                                        "negativeExample": "只写文字说明但线宽没有变化",
                                    }
                                ],
                            }
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            profile = build_capability_growth_profile(
                programs=programs,
                capability_ids=["cad-layer-lineweight-standard"],
                replay_mode="growth_replay",
                profile_source=profile_source,
                project_root=root,
                generated_at="2026-06-07T00:00:00Z",
            )

        self.assertEqual(profile["status"], "pass", profile)
        self.assertEqual(profile["profileSource"]["status"], "pass")
        self.assertEqual(profile["profileSource"]["role"], "local_file")
        item = profile["profiles"][0]
        self.assertEqual(item["capabilityId"], "cad-layer-lineweight-standard")
        self.assertEqual(item["profileVersion"], "lesson-v2")
        self.assertEqual(item["minimumExpressionLevel"], "growth")
        self.assertEqual(item["evidenceState"], "profile_loaded")
        self.assertEqual(item["transferableLessons"][0]["lessonId"], "lineweight-distinct-samples")
        self.assertEqual(item["deterministicProofBoundaries"]["cadGeometryProof"], "not_checked")
        self.assertEqual(item["deterministicProofBoundaries"]["projectDeliveryReadiness"], "not_checked")

    def test_profile_source_outside_workspace_is_blocked_before_reading(self) -> None:
        from core.training.capability_growth_profile import validate_profile_source

        with temporary_artifact_dir("adaptive_growth_profile_outside") as root:
            outside = root.parent / "outside-profile.json"
            result = validate_profile_source(outside, project_root=root)

        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(result["reason"], "profile_source_outside_workspace")
        self.assertFalse(result["readAttempted"])

    def test_adaptive_planner_and_regression_guard_block_expression_downgrade(self) -> None:
        from core.training.adaptive_replay_planner import build_adaptive_replay_plan
        from core.training.expression_regression_gate import evaluate_expression_regression_guard

        profile = {
            "status": "pass",
            "profiles": [
                {
                    "capabilityId": "cad-layer-lineweight-standard",
                    "profileVersion": "lesson-v2",
                    "minimumExpressionLevel": "growth",
                    "transferableLessons": [
                        {"lessonId": "lineweight-distinct-samples", "summary": "线宽必须可回读。"}
                    ],
                }
            ],
        }
        plan = build_adaptive_replay_plan(
            replay_mode="growth_replay",
            scope={"mode": "focused", "requestedCapabilityIds": ["cad-layer-lineweight-standard"]},
            capability_profile=profile,
            allow_low_expression=False,
        )

        self.assertEqual(plan["status"], "pass", plan)
        self.assertEqual(plan["safetyBoundaries"]["worker"]["deployRequired"], False)
        item = plan["items"][0]
        self.assertEqual(item["targetExpressionLevel"], "growth")
        self.assertEqual(item["baselineExpressionLevel"], "growth")
        self.assertEqual(item["consumedLessonIds"], ["lineweight-distinct-samples"])
        self.assertFalse(item["acceptedLowExpression"])
        self.assertIn("growth_replay", item["whyExpressionLevelChosen"])

        guard = evaluate_expression_regression_guard(
            plan["items"],
            replay_mode="growth_replay",
            allow_low_expression=False,
        )
        self.assertEqual(guard["status"], "pass", guard)

        downgrade_guard = evaluate_expression_regression_guard(
            [
                {
                    "capabilityId": "cad-layer-lineweight-standard",
                    "targetExpressionLevel": "smoke",
                    "baselineExpressionLevel": "growth",
                    "acceptedLowExpression": False,
                }
            ],
            replay_mode="growth_replay",
            allow_low_expression=False,
        )
        self.assertEqual(downgrade_guard["status"], "blocked", downgrade_guard)
        self.assertEqual(downgrade_guard["failures"][0]["reason"], "expression_regression")

    def test_source_role_classifier_distinguishes_fact_derived_diagnostic_candidate_archived_and_missing(self) -> None:
        from core.training.capability_growth_profile import classify_profile_source_role

        with temporary_artifact_dir("adaptive_growth_source_roles") as root:
            active = root / "output" / "training_queues" / "cad-foundation-remaining-21" / "report.json"
            active.parent.mkdir(parents=True)
            active.write_text("{}", encoding="utf-8")
            derived = root / "capability-map-data.js"
            derived.write_text("window.X={}", encoding="utf-8")
            diagnostic = root / "output" / "debug" / "draft.md"
            diagnostic.parent.mkdir(parents=True)
            diagnostic.write_text("draft", encoding="utf-8")
            candidate = root / "output" / "training_queues" / "focused" / "candidate.json"
            candidate.parent.mkdir(parents=True)
            candidate.write_text("{}", encoding="utf-8")
            archived = root / "archive" / "old-report.json"
            archived.parent.mkdir(parents=True)
            archived.write_text("{}", encoding="utf-8")

            self.assertEqual(
                classify_profile_source_role(active, project_root=root, active_fact_source_paths=[active])["role"],
                "fact_source",
            )
            self.assertEqual(classify_profile_source_role(derived, project_root=root)["role"], "derived")
            self.assertEqual(classify_profile_source_role(diagnostic, project_root=root)["role"], "diagnostic")
            self.assertEqual(classify_profile_source_role(candidate, project_root=root)["role"], "candidate")
            self.assertEqual(classify_profile_source_role(archived, project_root=root)["role"], "archived_index")
            self.assertEqual(classify_profile_source_role(root / "missing.json", project_root=root)["role"], "missing_or_stale")

    def test_no_cad_inventory_emits_diagnostic_report_without_mutating_durable_state(self) -> None:
        from core.training.capability_growth_profile import build_capability_growth_inventory, write_growth_inventory_report

        with temporary_artifact_dir("adaptive_growth_inventory") as root:
            training_sources = root / "docs" / "training" / "training-sources.json"
            report_path = root / "output" / "training_queues" / "cad-foundation-remaining-21" / "report.json"
            memory_path = root / "agents" / "cad_designer" / "training_memory.json"
            prompt_path = root / "agents" / "cad_designer" / "prompt_addendum.md"
            report_path.parent.mkdir(parents=True)
            memory_path.parent.mkdir(parents=True)
            training_sources.parent.mkdir(parents=True)
            report_path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
            memory_path.write_text(json.dumps({"lessons": []}), encoding="utf-8")
            prompt_path.write_text("# Addendum\n", encoding="utf-8")
            training_sources.write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "id": "remaining-21",
                                "status": "active",
                                "kind": "training_acceptance_report",
                                "path": report_path.relative_to(root).as_posix(),
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            inventory = build_capability_growth_inventory(
                project_root=root,
                programs=[{"capabilityId": "cad-layer-lineweight-standard", "name": "线宽线型标准"}],
            )
            output = write_growth_inventory_report(inventory, root / "output" / "validation_runs" / "adaptive-growth")

            self.assertEqual(inventory["status"], "pass", inventory)
            self.assertEqual(inventory["cadExecution"]["status"], "not_run")
            self.assertEqual(inventory["mutatedTargets"], [])
            roles = {source["role"] for source in inventory["sources"]}
            self.assertIn("fact_source", roles)
            self.assertIn("candidate", roles)
            self.assertTrue(Path(output["reportPath"]).is_file())
            self.assertEqual(output["dataBloatRole"], "diagnostic")

    def test_transferable_lesson_candidate_requires_positive_negative_and_retest_boundaries(self) -> None:
        from core.training.capability_growth_profile import build_transferable_lesson_candidate

        lesson = build_transferable_lesson_candidate(
            lesson_id="lineweight-readback",
            origin_capability_id="cad-layer-lineweight-standard",
            statement="线宽训练必须有真实线宽和线型 readback。",
            positive_pattern="三档线宽与 CENTER/DASHED/CONTINUOUS 都可回读。",
            negative_pattern="只写中文说明但实体线宽没有变化。",
            preconditions=["focused growth replay"],
            does_not_apply_when=["explicit smoke"],
            audit_implication="检查 lineweight/linetype/linetypeScale。",
            retest_required=True,
            source_refs=[{"path": "output/training_queues/example/report.json", "role": "candidate"}],
        )

        self.assertEqual(lesson["status"], "valid", lesson)
        self.assertEqual(lesson["promotionLevel"], "candidate")
        self.assertTrue(lesson["retestRequired"])
        self.assertIn("notChecked", lesson["evidenceBoundary"])

        invalid = build_transferable_lesson_candidate(
            lesson_id="bad",
            origin_capability_id="cad-layer-lineweight-standard",
            statement="missing boundaries",
            positive_pattern="positive only",
        )
        self.assertEqual(invalid["status"], "invalid", invalid)
        self.assertIn("negativePattern", invalid["missingFields"])
        self.assertIn("retestRequired", invalid["missingFields"])

    def test_candidate_profile_rejects_debug_and_derived_sources_as_hard_baselines(self) -> None:
        from core.training.capability_growth_profile import build_profile_candidate_from_sources

        with temporary_artifact_dir("adaptive_growth_profile_baseline") as root:
            debug_path = root / "output" / "debug" / "adaptive.md"
            derived_path = root / "capability-map-data.js"
            debug_path.parent.mkdir(parents=True)
            debug_path.write_text("debug", encoding="utf-8")
            derived_path.write_text("window.X={}", encoding="utf-8")

            result = build_profile_candidate_from_sources(
                capability_id="cad-layer-lineweight-standard",
                sources=[debug_path, derived_path],
                project_root=root,
                require_hard_baseline=True,
            )

        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(result["reason"], "no_fact_source_hard_baseline")
        self.assertEqual({source["role"] for source in result["sourceRefs"]}, {"diagnostic", "derived"})

    def test_request_router_covers_smoke_focused_formal_standard_and_project_execution(self) -> None:
        from core.training.adaptive_replay_planner import route_adaptive_training_request

        smoke = route_adaptive_training_request(request_kind="quick_trial", capability_ids=["cad-hatch-boundary"])
        focused = route_adaptive_training_request(request_kind="focused_retraining", capability_ids=["cad-hatch-boundary"])
        formal_all = route_adaptive_training_request(request_kind="all-31", capability_ids=["cad-hatch-boundary"])
        standard = route_adaptive_training_request(
            request_kind="focused_retraining",
            capability_ids=["cad-dim-style-baseline"],
            has_standard_source=True,
        )
        project = route_adaptive_training_request(request_kind="project_execution", capability_ids=["cad-dim-style-baseline"])

        self.assertEqual(smoke["replayMode"], "smoke_replay")
        self.assertEqual(smoke["promotionLevel"], "observation")
        self.assertTrue(smoke["acceptedLowExpression"])
        self.assertEqual(focused["route"], "focused_retraining")
        self.assertEqual(focused["replayMode"], "growth_replay")
        self.assertFalse(focused["scope"]["fullBatchAllowed"])
        self.assertEqual(formal_all["replayMode"], "growth_replay")
        self.assertEqual(formal_all["formalAcceptanceRequired"], False)
        self.assertEqual(standard["replayMode"], "standard_replay")
        self.assertEqual(project["route"], "project_execution")
        self.assertEqual(project["cadExecution"]["deterministicProofRequired"], True)

    def test_regression_guard_blocks_missing_required_features_but_exempts_smoke_with_reason(self) -> None:
        from core.training.expression_regression_gate import evaluate_expression_regression_guard

        blocked = evaluate_expression_regression_guard(
            [
                {
                    "capabilityId": "cad-layer-lineweight-standard",
                    "targetExpressionLevel": "growth",
                    "baselineExpressionLevel": "growth",
                    "requiredFeatures": ["lineweight_readback", "linetype_scale_readback"],
                    "observedFeatures": ["lineweight_readback"],
                }
            ],
            replay_mode="growth_replay",
            allow_low_expression=False,
        )
        self.assertEqual(blocked["status"], "blocked", blocked)
        self.assertEqual(blocked["failures"][0]["reason"], "required_features_missing")
        self.assertFalse(blocked["comparisonPolicy"]["screenshotOnly"])
        self.assertFalse(blocked["comparisonPolicy"]["handleCountOnly"])

        smoke = evaluate_expression_regression_guard(
            [
                {
                    "capabilityId": "cad-layer-lineweight-standard",
                    "targetExpressionLevel": "smoke",
                    "baselineExpressionLevel": "growth",
                }
            ],
            replay_mode="smoke_replay",
            allow_low_expression=True,
        )
        self.assertEqual(smoke["status"], "not_applicable", smoke)
        self.assertEqual(smoke["acceptedExemption"], "explicit_minimal_smoke")

    def test_closeout_claim_classifier_restricts_allowed_claims_by_evidence_state(self) -> None:
        from core.training.adaptive_growth_closeout import classify_adaptive_growth_closeout

        verified = classify_adaptive_growth_closeout(
            status="pass",
            checks=[{"name": "expression_regression_guard", "status": "pass"}],
            readback_count=3,
            created_handle_count=3,
            replay_mode="growth_replay",
            visual_reviewed=False,
        )
        not_verified = classify_adaptive_growth_closeout(
            status="pass",
            checks=[{"name": "expression_regression_guard", "status": "pass"}],
            readback_count=0,
            created_handle_count=3,
            replay_mode="growth_replay",
            visual_reviewed=False,
        )
        blocked = classify_adaptive_growth_closeout(
            status="blocked",
            checks=[{"name": "expression_regression_guard", "status": "fail"}],
            readback_count=0,
            created_handle_count=0,
            replay_mode="growth_replay",
            visual_reviewed=False,
        )

        self.assertEqual(verified["claimState"], "verified")
        self.assertEqual(not_verified["claimState"], "not_verified")
        self.assertEqual(blocked["claimState"], "blocked")
        self.assertNotIn("project delivery ready", " ".join(verified["allowedClaims"]))
        self.assertIn("not_implemented", verified["disallowedClaimStates"])


if __name__ == "__main__":
    unittest.main()
