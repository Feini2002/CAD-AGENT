from __future__ import annotations

import json
import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tests.helpers import temporary_artifact_dir


EXPECTED_PROMPT_PACKS = {
    "pipeline_visual_acceptance_reviewer",
    "pipeline_repair",
    "pipeline_asset_governor",
    "pipeline_visual_layout_reviewer",
    "pipeline_orchestrator",
    "pipeline_delivery",
    "pipeline_design_director",
    "pipeline_style_generator",
    "pipeline_design_reviewer",
    "pipeline_learning_promoter",
}

DESIGN_PROMPT_PACKS = {
    "pipeline_design_director",
    "pipeline_style_generator",
    "pipeline_design_reviewer",
}

VISIBLE_AUDIT_FIELDS = {
    "decision",
    "evidenceUsed",
    "evidenceMissing",
    "assumptions",
    "alternativesConsidered",
    "blockingReasons",
    "nextRequiredEvidence",
    "finalResponseAllowedClaims",
    "learningCandidate",
    "toolIntent",
}


def _prompt_payload() -> dict[str, object]:
    return {
        "userRequest": "请复审这次 CODEX_PREVIEW 输出能否请用户验收。",
        "taskContext": {
            "taskKind": "visual_acceptance_review",
            "route": "formal_acceptance",
            "targetLayer": "CODEX_PREVIEW",
        },
        "evidenceRefs": [
            "cad_reports/readback_summary.json",
            "screenshots/preview.png",
        ],
        "statePatchRequest": {
            "phase": "visual_reviewed",
            "phaseLabelForUser": "视觉验收",
        },
        "agentSpecific": {},
    }


def _common_model_fields() -> dict[str, object]:
    return {
        "decision": "pass",
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
        "learningCandidate": {
            "decision": "not_required",
            "trigger": "",
            "responsibleAgentIds": [],
            "errorPattern": "",
            "correctPattern": "",
            "promptDelta": "",
            "checkerDelta": "",
            "retestOriginalTask": False,
        },
        "statePatch": {
            "phase": "visual_reviewed",
            "phaseLabelForUser": "视觉验收已完成",
            "completedEvidence": ["model visual review"],
            "pendingEvidence": [],
            "pendingUserAction": "请重点看文字、位置和遮挡",
            "blockedReason": "",
            "nextSafeAction": "ask_user_review",
        },
        "finalResponseAllowedClaims": [
            "模型只读视觉复审通过，可进入用户可见验收请求"
        ],
        "evidenceUsed": ["screenshot visual aid", "readback summary ref"],
        "evidenceMissing": [],
        "toolIntent": None,
    }


def _soft_judgment() -> dict[str, object]:
    return {
        "confidence": 0.78,
        "acceptableForCurrentScope": True,
        "betterAlternativeAvailable": False,
        "needsUserTasteChoice": False,
        "riskLevel": "low",
        "suggestedRepairScope": "none",
        "selfUncertainty": ["synthetic fixture may miss real CAD visual issues"],
        "riskNote": "unit-test soft judgment only; hard gates still rely on evidence",
        "whatWouldChangeMyMind": ["missing CAD readback", "user reports visual mismatch"],
    }


def _valid_visual_acceptance_model_output() -> dict[str, object]:
    return {
        "status": "pass",
        "canAskUserToReview": True,
        "aestheticAcceptable": True,
        "textReadable": True,
        "noMojibake": True,
        "noSevereOverlap": True,
        "noSevereClipping": True,
        "alignmentAcceptable": True,
        "contentMatchesIntent": True,
        "reusableOutputLikely": True,
        "evidenceBoundaryRespected": True,
        "nonScreenshotEvidenceChecked": True,
        "blockingReasons": [],
        "visualProblems": [],
        "lookHereFirst": ["文字是否可读", "主要对象是否贴边"],
        "repairRecommendation": {
            "mode": "none",
            "reason": "synthetic prompt-pack smoke test",
            "targetZone": "none",
            "targetHandles": [],
            "nextChecks": [],
        },
        "softJudgment": _soft_judgment(),
        **_common_model_fields(),
    }


def _valid_learning_promotion_model_output() -> dict[str, object]:
    return {
        "status": "pass",
        "learningPromotionDecision": "proposal_ready",
        "promotionMode": "proposal_only",
        "targetAgentIds": ["pipeline_design_reviewer"],
        "memoryPatchProposals": [
            {
                "targetAgentId": "pipeline_design_reviewer",
                "memoryLayer": "decision_exemplars",
                "action": "add",
                "errorPattern": "delivery tried to claim user acceptance before visual evidence",
                "correctPattern": "delivery must block until visual acceptance and readback evidence are present",
                "promptDelta": "Check visual acceptance evidence before final allowed claims.",
                "checkerDelta": "",
                "evidenceRefs": ["model_traces/pipeline_delivery/trace.json"],
                "supersedes": [],
                "retireCandidate": False,
                "changedDecision": True,
            }
        ],
        "promptPatchProposals": [
            {
                "targetAgentId": "pipeline_design_reviewer",
                "patchType": "prompt_addendum",
                "proposal": "Block user-review claims when visual evidence is absent.",
                "evidenceRefs": ["model_traces/pipeline_delivery/trace.json"],
                "writeAllowed": False,
            }
        ],
        "checkerCandidateProposals": [
            {
                "checkerScope": "delivery_claims",
                "candidate": "Detect user acceptance claims without visual acceptance evidence.",
                "evidenceRefs": ["model_traces/pipeline_delivery/trace.json"],
                "retestRequired": True,
            }
        ],
        "behaviorChangeEvidence": {
            "beforeDecision": "ready_to_ask_user_review",
            "afterDecision": "blocked_until_visual_acceptance",
            "changedRoute": False,
            "changedRequiredAgents": False,
            "changedToolChoice": False,
            "changedBlockingReason": True,
            "retestedOriginalTask": True,
            "memoryAppliedInFutureRun": False,
            "predictionReconciliation": {
                "statement": "User will reject unsupported acceptance claims.",
                "reconciled": False,
                "outcome": "pending",
            },
        },
        "retestPlan": {
            "retestOriginalTask": True,
            "targetTaskRef": "output/runs/mock/model_trace.json",
            "why": "The proposed patch must prove it blocks the original unsupported claim.",
        },
        "evidenceBoundary": {
            "writePolicy": "proposal_only",
            "notProofOf": [
                "training passed",
                "memory written",
                "CAD geometry verified",
                "Project Delivery Readiness",
            ],
        },
        **_common_model_fields(),
    }


class ModelPromptLibraryTests(unittest.TestCase):
    def test_prompt_pack_manifest_loads_registered_agents_and_reuses_schemas(self) -> None:
        from core.model_review.prompt_library import list_prompt_packs, load_prompt_pack

        packs = list_prompt_packs()
        self.assertTrue(EXPECTED_PROMPT_PACKS.issubset(set(packs)))

        manifest = json.loads(Path("core/model_review/prompt_packs/manifest.json").read_text(encoding="utf-8"))
        planned = {str(item.get("agentId")) for item in manifest.get("plannedPacks", []) if isinstance(item, dict)}
        self.assertFalse(DESIGN_PROMPT_PACKS.intersection(planned))

        for agent_id in EXPECTED_PROMPT_PACKS:
            pack = load_prompt_pack(agent_id)
            self.assertEqual(pack.agent_id, agent_id)
            self.assertTrue(pack.prompt_path.is_file())
            self.assertTrue(pack.boundary_rules_path.is_file())
            self.assertTrue(pack.negative_examples_path.is_file())
            self.assertTrue(pack.input_schema_path.is_file())
            self.assertTrue(pack.output_schema_path.is_file())
            self.assertEqual(pack.output_schema_path.parent.name, "schemas")

    def test_prompt_rendering_includes_real_boundaries_state_and_allowed_claims(self) -> None:
        from core.model_review.prompt_library import load_prompt_pack

        for agent_id in EXPECTED_PROMPT_PACKS:
            prompt = load_prompt_pack(agent_id).render_prompt(_prompt_payload())
            self.assertIn("strict JSON", prompt)
            self.assertIn("modelProviderStatus", prompt)
            self.assertIn("只读", prompt)
            self.assertIn("不得写 CAD", prompt)
            self.assertIn("不能替代 CAD readback", prompt)
            self.assertIn("statePatch", prompt)
            self.assertIn("finalResponseAllowedClaims", prompt)
            self.assertIn("visible audit fields", prompt)
            self.assertIn("Do not expose raw chain-of-thought", prompt)
            self.assertIn("export manifest", prompt)
            self.assertIn("explicit payload", prompt)
            self.assertIn("Input Payload", prompt)

    def test_model_review_schemas_require_visible_audit_fields(self) -> None:
        for schema_path in sorted(Path("core/model_review/schemas").glob("*.schema.json")):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            required = set(schema.get("required", []))
            missing = sorted(VISIBLE_AUDIT_FIELDS - required)
            self.assertEqual(missing, [], schema_path.name)
            for field in VISIBLE_AUDIT_FIELDS:
                self.assertIn(field, schema["properties"], schema_path.name)

    def test_repair_plan_schema_matches_validator_operation_shape(self) -> None:
        schema = json.loads(
            Path("core/model_review/schemas/repair_plan_review.schema.json").read_text(encoding="utf-8")
        )
        operation = schema["properties"]["operations"]["items"]
        required = set(operation["required"])
        properties = set(operation["properties"])

        self.assertIn("action", required)
        self.assertIn("targetHandles", required)
        self.assertIn("targetBbox", required)
        self.assertNotIn("operationType", properties)
        self.assertNotIn("targetHandle", properties)

    def test_agent_specific_prompt_contract_fields_are_schema_backed(self) -> None:
        visual = json.loads(
            Path("core/model_review/schemas/visual_acceptance_review.schema.json").read_text(encoding="utf-8")
        )
        repair = json.loads(
            Path("core/model_review/schemas/repair_plan_review.schema.json").read_text(encoding="utf-8")
        )
        asset = json.loads(
            Path("core/model_review/schemas/asset_governor_review.schema.json").read_text(encoding="utf-8")
        )
        design_director = json.loads(
            Path("core/model_review/schemas/design_director_review.schema.json").read_text(encoding="utf-8")
        )
        style_generation = json.loads(
            Path("core/model_review/schemas/style_generation_review.schema.json").read_text(encoding="utf-8")
        )
        design_review = json.loads(
            Path("core/model_review/schemas/design_review.schema.json").read_text(encoding="utf-8")
        )
        learning_promotion = json.loads(
            Path("core/model_review/schemas/learning_promotion_review.schema.json").read_text(encoding="utf-8")
        )

        for field in ("canAskUserToReview", "lookHereFirst", "softJudgment"):
            self.assertIn(field, visual["properties"])
            self.assertIn(field, visual["required"])

        for field in (
            "rootCause",
            "repairMode",
            "whyLocalRepairIsEnough",
            "whyFullRedrawIsNotAllowedOrNeeded",
            "requiresUserPermission",
            "protectedNeighbors",
        ):
            self.assertIn(field, repair["properties"])
            self.assertIn(field, repair["required"])

        for field in (
            "assetLifecycleDecision",
            "sourceBoundaryDecision",
            "cleanSourceAllowed",
            "quarantineReason",
            "requiredChildAgents",
            "nativeVisibleEvidenceRequired",
            "reuseProofRequired",
        ):
            self.assertIn(field, asset["properties"])
            self.assertIn(field, asset["required"])

        for field in (
            "designStrategy",
            "drawingTypeDecision",
            "expressionPurpose",
            "designIntent",
            "requiredChildAgents",
            "openQuestions",
            "evidenceBoundary",
            "learningCandidate",
        ):
            self.assertIn(field, design_director["properties"])
            self.assertIn(field, design_director["required"])

        for field in (
            "styleDecision",
            "styleCandidates",
            "selectedStyleCandidate",
            "styleParameterGrammar",
            "candidateTradeoffs",
            "needsUserChoice",
            "styleWaiverReason",
            "candidateCountPolicy",
            "requestedCandidateCount",
            "candidateLabelPolicy",
            "creativityPolicy",
            "semanticRoutingConfidence",
            "learningCandidate",
        ):
            self.assertIn(field, style_generation["properties"])
            self.assertIn(field, style_generation["required"])
        self.assertEqual(style_generation["properties"]["styleCandidates"]["minItems"], 0)

        for field in (
            "designReview",
            "professionalDrawingLike",
            "readability",
            "industryHabitFit",
            "styleCandidateFit",
            "contentMatchesDesignPurpose",
            "needsUserChoice",
            "repairOrRegenerateRecommendation",
            "softJudgment",
            "learningCandidate",
        ):
            self.assertIn(field, design_review["properties"])
            self.assertIn(field, design_review["required"])
        self.assertEqual(design_review["$defs"]["softJudgment"]["properties"]["confidence"]["minimum"], 0)
        self.assertEqual(design_review["$defs"]["softJudgment"]["properties"]["confidence"]["maximum"], 1)
        for schema in (
            design_review,
            json.loads(Path("core/model_review/schemas/visual_acceptance_review.schema.json").read_text(encoding="utf-8")),
            json.loads(Path("core/model_review/schemas/visual_layout_review.schema.json").read_text(encoding="utf-8")),
            json.loads(Path("core/model_review/schemas/delivery_claims_review.schema.json").read_text(encoding="utf-8")),
        ):
            self.assertIn("selfUncertainty", schema["$defs"]["softJudgment"]["required"])
            self.assertIn("selfUncertainty", schema["$defs"]["softJudgment"]["properties"])

        for field in (
            "learningPromotionDecision",
            "promotionMode",
            "memoryPatchProposals",
            "promptPatchProposals",
            "checkerCandidateProposals",
            "behaviorChangeEvidence",
            "retestPlan",
        ):
            self.assertIn(field, learning_promotion["properties"])
            self.assertIn(field, learning_promotion["required"])
        self.assertEqual(learning_promotion["properties"]["promotionMode"]["enum"], ["proposal_only"])
        behavior = learning_promotion["$defs"]["behaviorChangeEvidence"]
        self.assertIn("retestedOriginalTask", behavior["required"])
        self.assertIn("predictionReconciliation", behavior["required"])

    def test_prompt_pack_review_writes_trace_and_converted_agent_output(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.model_review.prompt_library import run_prompt_pack_review

        with temporary_artifact_dir("prompt_pack_visual_acceptance") as root:
            run_dir = root / "run"
            output_path = run_dir / "agent_outputs" / "pipeline_visual_acceptance_reviewer.json"

            def fake_runner(
                command: list[str],
                **_kwargs: object,
            ) -> subprocess.CompletedProcess[str]:
                output_index = command.index("--output-last-message") + 1
                Path(command[output_index]).write_text(
                    json.dumps(_valid_visual_acceptance_model_output(), ensure_ascii=False),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            report = run_prompt_pack_review(
                agent_id="pipeline_visual_acceptance_reviewer",
                payload=_prompt_payload(),
                run_dir=run_dir,
                output_path=output_path,
                config=CodexCliReviewConfig(enabled=True),
                runner=fake_runner,
                cwd=root,
                trace_id="visual-pass",
            )

            self.assertEqual(report["status"], "pass")
            self.assertTrue(output_path.is_file())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["status"], "pass")
            self.assertEqual(written["statePatch"]["phase"], "visual_reviewed")
            self.assertTrue(written["finalResponseAllowedClaims"])

            trace_dir = run_dir / "model_traces" / "pipeline_visual_acceptance_reviewer" / "visual-pass"
            self.assertTrue((trace_dir / "trace_manifest.json").is_file())
            context = json.loads((trace_dir / "prompt_pack_context.json").read_text(encoding="utf-8"))
            self.assertEqual(context["promptPackId"], "pipeline_visual_acceptance_reviewer")
            self.assertEqual(context["schemaPath"], "core/model_review/schemas/visual_acceptance_review.schema.json")

    def test_prompt_pack_review_export_manifest_allowlists_payload_evidence_refs(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.model_review.prompt_library import run_prompt_pack_review

        with temporary_artifact_dir("prompt_pack_export_refs") as root:
            run_dir = root / "run"
            evidence_path = run_dir / "cad_reports" / "readback_summary.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(
                json.dumps({"status": "pass", "createdHandleCount": 2}, ensure_ascii=False),
                encoding="utf-8",
            )
            payload = _prompt_payload()
            payload["evidenceRefs"] = [str(evidence_path)]
            output_path = run_dir / "agent_outputs" / "pipeline_visual_acceptance_reviewer.json"
            runner_called = False

            def fake_runner(
                command: list[str],
                **_kwargs: object,
            ) -> subprocess.CompletedProcess[str]:
                nonlocal runner_called
                runner_called = True
                output_index = command.index("--output-last-message") + 1
                Path(command[output_index]).write_text(
                    json.dumps(_valid_visual_acceptance_model_output(), ensure_ascii=False),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            report = run_prompt_pack_review(
                agent_id="pipeline_visual_acceptance_reviewer",
                payload=payload,
                run_dir=run_dir,
                output_path=output_path,
                config=CodexCliReviewConfig(enabled=True),
                runner=fake_runner,
                cwd=root,
                trace_id="visual-export-refs",
            )

            trace_dir = run_dir / "model_traces" / "pipeline_visual_acceptance_reviewer" / "visual-export-refs"
            export_manifest = json.loads((trace_dir / "export_manifest.json").read_text(encoding="utf-8"))
            trace_manifest = json.loads((trace_dir / "trace_manifest.json").read_text(encoding="utf-8"))
            expected_ref = str(evidence_path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")

            self.assertTrue(runner_called)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(export_manifest["status"], "pass")
            self.assertIn(expected_ref, trace_manifest["inputs"]["summaryRefs"])
            self.assertTrue(
                any(
                    item.get("kind") == "payload_ref"
                    and item.get("path") == expected_ref
                    and item.get("status") == "present"
                    for item in export_manifest["sentArtifacts"]
                )
            )

    def test_learning_promoter_prompt_pack_outputs_proposal_only_patch(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig
        from core.model_review.prompt_library import run_prompt_pack_review

        with temporary_artifact_dir("prompt_pack_learning_promoter") as root:
            run_dir = root / "run"
            evidence_path = run_dir / "model_traces" / "pipeline_delivery" / "trace.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(
                json.dumps({"status": "blocked", "blockingReasons": ["unsupported acceptance claim"]}, ensure_ascii=False),
                encoding="utf-8",
            )
            payload = {
                "userRequest": "复审这次失败是否应该沉淀学习补丁。",
                "taskContext": {
                    "taskKind": "model_trace_learning",
                    "route": "training_data_bloat_governance",
                },
                "evidenceRefs": [str(evidence_path)],
                "statePatchRequest": {
                    "phase": "learning_reviewed",
                    "phaseLabelForUser": "学习补丁提案已复审",
                },
                "agentSpecific": {
                    "writePolicy": "proposal_only",
                },
            }
            output_path = run_dir / "agent_outputs" / "pipeline_learning_promoter.json"

            def fake_runner(
                command: list[str],
                **_kwargs: object,
            ) -> subprocess.CompletedProcess[str]:
                output_index = command.index("--output-last-message") + 1
                Path(command[output_index]).write_text(
                    json.dumps(_valid_learning_promotion_model_output(), ensure_ascii=False),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            report = run_prompt_pack_review(
                agent_id="pipeline_learning_promoter",
                payload=payload,
                run_dir=run_dir,
                output_path=output_path,
                config=CodexCliReviewConfig(enabled=True),
                runner=fake_runner,
                cwd=root,
                trace_id="learning-proposal",
            )

            trace_dir = run_dir / "model_traces" / "pipeline_learning_promoter" / "learning-proposal"
            export_manifest = json.loads((trace_dir / "export_manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["promotionMode"], "proposal_only")
            self.assertTrue(output_path.is_file())
            self.assertFalse((root / "agents" / "pipeline" / "design_reviewer" / "training_memory.json").exists())
            self.assertEqual(export_manifest["status"], "pass")

    def test_probe_dry_run_can_target_prompt_pack_without_model_invocation(self) -> None:
        from scripts.probe_codex_cli_model_review import main

        stdout = StringIO()
        with redirect_stdout(stdout):
            rc = main(["--prompt-pack", "pipeline_repair"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["promptPackId"], "pipeline_repair")
        self.assertFalse(payload["modelInvoked"])
        self.assertIn("repair_plan_review.schema.json", payload["schema"])

    def test_probe_dry_run_can_request_skip_git_repo_check_for_repo_external_bridge_cwd(self) -> None:
        from scripts.probe_codex_cli_model_review import main

        stdout = StringIO()
        with redirect_stdout(stdout):
            rc = main(
                [
                    "--prompt-pack",
                    "pipeline_design_director",
                    "--skip-git-repo-check",
                    "--ignore-user-config",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["skipGitRepoCheck"])
        self.assertTrue(payload["ignoreUserConfig"])
        self.assertIn("--ignore-user-config", payload["executeCommand"])
        self.assertIn("--skip-git-repo-check", payload["executeCommand"])


if __name__ == "__main__":
    unittest.main()
