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

        for field in ("canAskUserToReview", "lookHereFirst"):
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
            "learningCandidate",
        ):
            self.assertIn(field, design_review["properties"])
            self.assertIn(field, design_review["required"])

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
