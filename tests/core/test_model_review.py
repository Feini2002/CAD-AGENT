from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import temporary_artifact_dir


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _valid_visual_rack_plan() -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "layoutMode": "classified_expandable_visual_warehouse_v2",
        "warehouseArchitecture": {
            "kind": "category_visual_warehouse",
            "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
            "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
            "expansionPolicy": "typed racks grow by slot families",
        },
        "acceptanceCriteria": {
            "slotContainment": "slots stay inside owning rack",
            "assetOwnership": "occupied slots record assets",
            "expansionCapacity": "future slots are visible",
            "copyPolicy": "only clean source slots are copyable",
            "screenshotBoundary": "screenshots are visual aids only",
        },
        "rackFamilies": [
            {
                "rackId": "A_BASE_SCAFFOLD",
                "zoneId": "01_CLEAN_ASSETS",
                "familyRole": "reusable_style_source",
                "copyPolicy": "clean_source_slots_only",
                "minExpansionSlots": 1,
                "slots": [
                    {
                        "slotId": "A05_DIMENSION_STYLE",
                        "status": "occupied",
                        "assetIds": ["interior_dimension_style_visual_standard"],
                        "copySourceAllowed": True,
                    },
                    {
                        "slotId": "A06_LEADER_SYMBOL_STYLE",
                        "status": "empty_reserved",
                        "assetIds": [],
                        "copySourceAllowed": False,
                    },
                ],
            },
            {
                "rackId": "B_OBJECT_ASSET_INDEX",
                "zoneId": "B_OBJECT_ASSET_INDEX",
                "familyRole": "cross_category_object_index",
                "copyPolicy": "index_only_never_copy",
                "minExpansionSlots": 1,
                "slots": [
                    {
                        "slotId": "B01_BEDS",
                        "status": "index_only",
                        "category": "furniture.sleeping.beds",
                        "nativeDwg": "libraries/system_library/furniture/sleeping/beds/bed_assets.dwg",
                        "copySourceAllowed": False,
                        "copyPolicy": "never_copy",
                    }
                ],
            },
        ],
    }


def _valid_zones() -> dict[str, dict[str, list[float]]]:
    return {
        "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
        "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
        "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
        "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
        "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
    }


def _pass_readability() -> dict[str, object]:
    return {
        "status": "pass",
        "issueCount": 0,
        "issues": [],
        "checked": ["A1/A2 visual aisle", "content density"],
    }


def _valid_visual_acceptance_review(**overrides: object) -> dict[str, object]:
    report: dict[str, object] = {
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
        "lookHereFirst": ["整体可读性"],
        "repairRecommendation": {},
        **_common_model_review_fields(),
    }
    report.update(overrides)
    return report


def _common_model_review_fields() -> dict[str, object]:
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
            "phase": "model_reviewed",
            "phaseLabelForUser": "模型只读复审",
            "completedEvidence": ["model review"],
            "pendingEvidence": [],
            "pendingUserAction": "",
            "blockedReason": "",
            "nextSafeAction": "continue_gate_checks",
        },
        "finalResponseAllowedClaims": ["模型只读复审字段完整"],
        "evidenceUsed": ["synthetic unit-test evidence"],
        "evidenceMissing": [],
        "toolIntent": None,
    }


def _valid_design_director_review() -> dict[str, object]:
    return {
        "status": "pass",
        "designStrategy": {"styleCandidatePolicy": "single_candidate"},
        "drawingTypeDecision": "diagram",
        "expressionPurpose": "local hardening test",
        "designIntent": "prove model bridge boundaries",
        "audienceAndUse": "unit test",
        "constraints": [],
        "requiredChildAgents": [],
        "openQuestions": [],
        "evidenceBoundary": {"notProofOf": ["CAD geometry", "user acceptance"]},
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
        **_common_model_review_fields(),
    }


class ModelReviewTests(unittest.TestCase):
    def test_model_review_schemas_are_codex_cli_strict(self) -> None:
        schema_dir = Path("core/model_review/schemas")

        def walk(schema: dict[str, object], path: str) -> list[str]:
            issues: list[str] = []
            if schema.get("type") == "object":
                if schema.get("additionalProperties") is not False:
                    issues.append(f"{path}: additionalProperties must be false")
                properties = schema.get("properties", {})
                if isinstance(properties, dict):
                    required = set(schema.get("required", [])) if isinstance(schema.get("required"), list) else set()
                    missing_required = sorted(set(properties) - required)
                    if missing_required:
                        issues.append(f"{path}: properties missing from required: {missing_required}")
                    for key, value in properties.items():
                        if isinstance(value, dict):
                            issues.extend(walk(value, f"{path}.{key}"))
            if schema.get("type") == "array" and isinstance(schema.get("items"), dict):
                issues.extend(walk(schema["items"], f"{path}[]"))
            return issues

        issues: list[str] = []
        for schema_path in sorted(schema_dir.glob("*.schema.json")):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            issues.extend(walk(schema, schema_path.name))

        self.assertEqual(issues, [])

    def test_codex_cli_default_model_policy_is_gpt55_medium(self) -> None:
        from core.model_review.codex_cli_client import (
            DEFAULT_CODEX_CLI_MODEL,
            DEFAULT_CODEX_CLI_REASONING_EFFORT,
            CodexCliReviewConfig,
            run_codex_cli_review,
        )

        self.assertEqual(DEFAULT_CODEX_CLI_MODEL, "gpt-5.5")
        self.assertEqual(DEFAULT_CODEX_CLI_REASONING_EFFORT, "medium")
        self.assertEqual(CodexCliReviewConfig().model, "gpt-5.5")
        self.assertEqual(CodexCliReviewConfig().reasoning_effort, "medium")

        with temporary_artifact_dir("codex_cli_medium_policy") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            schema.write_text(
                json.dumps({"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}}),
                encoding="utf-8",
            )
            observed: dict[str, object] = {}

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                observed["command"] = command
                output.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            run_codex_cli_review(
                prompt="return strict JSON",
                schema_path=schema,
                output_path=output,
                config=CodexCliReviewConfig(enabled=True),
                runner=fake_runner,
                cwd=root,
            )

            command = observed["command"]
            self.assertIsInstance(command, list)
            self.assertIn("gpt-5.5", command)
            self.assertIn("-c", command)
            self.assertIn('model_reasoning_effort="medium"', command)

    def test_schema_valid_semantic_unavailable_is_not_provider_unavailable(self) -> None:
        from core.model_review.provider_status import with_model_provider_status

        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": True,
                "reason": "insufficient evidence for this agent decision",
            },
            validation={"status": "pass", "issues": [], "missingFields": []},
        )

        self.assertTrue(report["modelInvoked"])
        self.assertFalse(report["modelProviderStatus"]["modelUnavailable"])
        self.assertTrue(report["modelProviderStatus"]["schemaValid"])

    def test_codex_cli_review_config_can_be_enabled_from_environment(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig

        env = {
            "CAD_AGENT_MODEL_REVIEW_ENABLED": "1",
            "CAD_AGENT_MODEL_REVIEW_MODEL": "gpt-5.5",
            "CAD_AGENT_MODEL_REVIEW_REASONING_EFFORT": "medium",
            "CAD_AGENT_MODEL_REVIEW_TIMEOUT_SECONDS": "42",
            "CAD_AGENT_MODEL_REVIEW_IGNORE_USER_CONFIG": "1",
            "CAD_AGENT_MODEL_REVIEW_SKIP_GIT_REPO_CHECK": "1",
        }
        with patch.dict(os.environ, env, clear=False):
            config = CodexCliReviewConfig.from_environment()

        self.assertTrue(config.enabled)
        self.assertEqual(config.model, "gpt-5.5")
        self.assertEqual(config.reasoning_effort, "medium")
        self.assertEqual(config.timeout_seconds, 42)
        self.assertEqual(config.executable, "codex.cmd")
        self.assertEqual(config.sandbox, "read-only")
        self.assertTrue(config.ignore_user_config)
        self.assertTrue(config.skip_git_repo_check)

    def test_codex_cli_review_uses_environment_config_when_config_not_passed(self) -> None:
        from core.model_review.codex_cli_client import run_codex_cli_review

        with temporary_artifact_dir("codex_cli_env_default") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            schema.write_text(
                json.dumps({"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}}),
                encoding="utf-8",
            )
            observed: dict[str, object] = {}

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                observed["command"] = command
                output.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            env = {
                "CAD_AGENT_MODEL_REVIEW_ENABLED": "1",
                "CAD_AGENT_MODEL_REVIEW_MODEL": "gpt-5.5",
                "CAD_AGENT_MODEL_REVIEW_REASONING_EFFORT": "medium",
            }
            with patch.dict(os.environ, env, clear=False):
                report = run_codex_cli_review(
                    prompt="return strict JSON",
                    schema_path=schema,
                    output_path=output,
                    runner=fake_runner,
                    cwd=root,
                )

            self.assertEqual(report["status"], "pass")
            self.assertIn("command", observed)
            command = observed["command"]
            self.assertIsInstance(command, list)
            self.assertIn("gpt-5.5", command)
            self.assertIn('model_reasoning_effort="medium"', command)

    def test_codex_cli_review_uses_repo_external_cwd(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        with temporary_artifact_dir("codex_cli_external_cwd") as root:
            schema = PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json"
            output = root / "review.json"
            captured: dict[str, object] = {}

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                captured["cwd"] = Path(cwd).resolve()
                output.write_text(json.dumps(_valid_design_director_review()), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            run_codex_cli_review(
                prompt="safe prompt",
                schema_path=schema,
                output_path=output,
                image_paths=[],
                input_summary_refs=[],
                config=CodexCliReviewConfig(enabled=True, ignore_user_config=True, skip_git_repo_check=True),
                runner=fake_runner,
                cwd=PROJECT_ROOT,
                agent_id="pipeline_design_director",
                task_type="design_director_review",
                trace_id="trace-external-cwd",
                trace_dir=root / "trace",
            )

            model_cwd = captured["cwd"]
            self.assertIsInstance(model_cwd, Path)
            self.assertFalse(model_cwd.is_relative_to(PROJECT_ROOT.resolve()))
            self.assertTrue(model_cwd.is_dir())
            command_json = json.loads((root / "trace" / "command.json").read_text(encoding="utf-8"))
            self.assertEqual(command_json["cwd"], str(model_cwd))

    def test_codex_cli_review_disabled_returns_unavailable_without_shelling(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        def forbidden_runner(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
            raise AssertionError("disabled model review must not invoke codex cli")

        with temporary_artifact_dir("codex_cli_disabled_trace") as root:
            schema = root / "schema.json"
            output = root / "disabled.json"
            trace_dir = root / "trace"
            schema.write_text(
                json.dumps({"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}}),
                encoding="utf-8",
            )

            report = run_codex_cli_review(
                prompt="review this warehouse screenshot",
                schema_path=schema,
                output_path=output,
                config=CodexCliReviewConfig(enabled=False, model="gpt-5.5"),
                runner=forbidden_runner,
                trace_id="disabled-case",
                trace_dir=trace_dir,
            )

            self.assertEqual(report["status"], "unavailable")
            self.assertFalse(report["modelInvoked"])
            self.assertTrue(report["modelProviderStatus"]["modelUnavailable"])
            self.assertFalse(report["modelProviderStatus"]["schemaValid"])
            self.assertEqual(report["modelProviderStatus"]["route"], "codex_cli_local")
            self.assertIn("disabled", report["reason"])
            self.assertEqual(report["modelTrace"]["traceId"], "disabled-case")
            trace_review = json.loads((trace_dir / "trace_review.json").read_text(encoding="utf-8"))
            self.assertEqual(trace_review["status"], "blocked")
            self.assertFalse(trace_review["modelInvocationUsable"])
            self.assertTrue((trace_dir / "trace_summary.md").is_file())

    def test_codex_cli_review_invokes_codex_cmd_and_loads_last_message_json(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        with temporary_artifact_dir("codex_cli_review") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            image = root / "warehouse.png"
            image.write_bytes(b"fake image")
            schema.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "required": ["status", "layoutReadabilityAcceptable"],
                        "properties": {
                            "status": {"type": "string"},
                            "layoutReadabilityAcceptable": {"type": "boolean"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            observed: dict[str, object] = {}

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                observed["command"] = command
                observed["input"] = input
                observed["cwd"] = cwd
                observed["encoding"] = encoding
                observed["errors"] = errors
                observed["timeout"] = timeout
                output.write_text(
                    json.dumps({"status": "pass", "layoutReadabilityAcceptable": True}),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            report = run_codex_cli_review(
                prompt="return strict JSON",
                schema_path=schema,
                output_path=output,
                image_paths=[image],
                input_summary_refs=["reports/readback_summary.json"],
                config=CodexCliReviewConfig(
                    enabled=True,
                    model="gpt-5.5",
                    timeout_seconds=77,
                    ignore_user_config=True,
                    skip_git_repo_check=True,
                ),
                runner=fake_runner,
                cwd=root,
                agent_id="pipeline_visual_layout_reviewer",
                task_type="visual_layout_review",
                trace_id="visual-layout-smoke",
                trace_dir=root / "trace",
            )

            command = observed["command"]
            self.assertIsInstance(command, list)
            self.assertEqual(command[:2], ["codex.cmd", "exec"])
            self.assertEqual(observed["encoding"], "utf-8")
            self.assertEqual(observed["errors"], "replace")
            self.assertIn("--model", command)
            self.assertIn("gpt-5.5", command)
            self.assertIn("--sandbox", command)
            self.assertIn("read-only", command)
            self.assertIn("--ephemeral", command)
            self.assertIn("--ignore-rules", command)
            self.assertIn("--ignore-user-config", command)
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--image", command)
            self.assertIn(str(schema.resolve()), command)
            self.assertIn(str(output.resolve()), command)
            self.assertIn(str(image.resolve()), command)
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["modelInvoked"])
            self.assertTrue(report["modelProviderStatus"]["schemaValid"])
            self.assertFalse(report["modelProviderStatus"]["modelUnavailable"])
            self.assertEqual(report["layoutReadabilityAcceptable"], True)
            self.assertEqual(report["modelTrace"]["traceId"], "visual-layout-smoke")

            trace_dir = root / "trace"
            self.assertEqual((trace_dir / "prompt.md").read_text(encoding="utf-8"), "return strict JSON")
            command_json = json.loads((trace_dir / "command.json").read_text(encoding="utf-8"))
            self.assertEqual(command_json["status"], "built")
            self.assertTrue(command_json["sanitized"])
            model_cwd = Path(command_json["cwd"]).resolve()
            self.assertFalse(model_cwd.is_relative_to(PROJECT_ROOT.resolve()))
            self.assertEqual(Path(observed["cwd"]).resolve(), model_cwd)
            self.assertEqual(command_json["timeoutSeconds"], 77)
            manifest = json.loads((trace_dir / "trace_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["agentId"], "pipeline_visual_layout_reviewer")
            self.assertEqual(manifest["taskType"], "visual_layout_review")
            self.assertEqual(manifest["traceId"], "visual-layout-smoke")
            self.assertEqual(manifest["inputs"]["summaryRefs"], ["reports/readback_summary.json"])
            self.assertEqual(manifest["files"]["exportManifest"], "export_manifest.json")
            gate_decision = json.loads((trace_dir / "gate_decision.json").read_text(encoding="utf-8"))
            self.assertEqual(gate_decision["status"], "pass")
            trace_review = json.loads((trace_dir / "trace_review.json").read_text(encoding="utf-8"))
            self.assertEqual(trace_review["status"], "pass")
            self.assertEqual(trace_review["taskType"], "visual_layout_review")
            self.assertTrue(trace_review["traceUsable"])
            self.assertEqual(trace_review["modelOutputTrust"], "schema_valid")
            trace_summary = (trace_dir / "trace_summary.md").read_text(encoding="utf-8")
            self.assertIn("模型调用可用性：可用", trace_summary)
            self.assertIn("export_manifest.json", trace_summary)

    def test_codex_cli_review_blocks_unexpected_project_context_warning(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        with temporary_artifact_dir("codex_cli_context_leak") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            schema.write_text(
                json.dumps({"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}}),
                encoding="utf-8",
            )

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                output.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout="",
                    stderr="Project doc C:\\Users\\User\\Desktop\\CAD-AGENT\\AGENTS.md exceeds remaining budget - truncating",
                )

            report = run_codex_cli_review(
                prompt="return strict JSON",
                schema_path=schema,
                output_path=output,
                config=CodexCliReviewConfig(enabled=True),
                runner=fake_runner,
                cwd=PROJECT_ROOT,
                trace_id="context-leak",
                trace_dir=root / "trace",
            )

            self.assertEqual(report["status"], "unavailable")
            self.assertEqual(report["reason"], "context_leak_blocked")
            audit = json.loads((root / "trace" / "context_leak_audit.json").read_text(encoding="utf-8"))
            self.assertTrue(audit["unexpectedProjectContextLoaded"])
            self.assertTrue(audit["blocking"])
            self.assertIn("Project doc", audit["warnings"][0])
            trace_summary = (root / "trace" / "trace_summary.md").read_text(encoding="utf-8")
            self.assertIn("context_leak_audit.json", trace_summary)

    def test_codex_cli_trace_blocks_when_model_declares_failure(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        with temporary_artifact_dir("codex_cli_declared_fail_trace") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            schema.write_text(
                json.dumps(
                    {
                        "type": "object",
                        "required": ["status", "blockingReasons"],
                        "properties": {
                            "status": {"type": "string"},
                            "blockingReasons": {"type": "array", "items": {"type": "string"}},
                        },
                    }
                ),
                encoding="utf-8",
            )

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                output.write_text(
                    json.dumps({"status": "fail", "blockingReasons": ["文字贴边，不能验收"]}),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            report = run_codex_cli_review(
                prompt="return strict JSON",
                schema_path=schema,
                output_path=output,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
                trace_id="declared-fail",
                trace_dir=root / "trace",
            )

            self.assertEqual(report["status"], "fail")
            self.assertTrue(report["modelProviderStatus"]["schemaValid"])
            gate_decision = json.loads((root / "trace" / "gate_decision.json").read_text(encoding="utf-8"))
            self.assertEqual(gate_decision["status"], "blocked")
            self.assertIn("model report status is fail", gate_decision["blockingReasons"])
            self.assertIn("文字贴边，不能验收", gate_decision["blockingReasons"])
            trace_review = json.loads((root / "trace" / "trace_review.json").read_text(encoding="utf-8"))
            self.assertEqual(trace_review["status"], "blocked")
            self.assertEqual(trace_review["gateDecisionStatus"], "blocked")

    def test_codex_cli_review_preserves_utf8_stderr_on_nonzero_exit(self) -> None:
        from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review

        with temporary_artifact_dir("codex_cli_review_stderr") as root:
            schema = root / "schema.json"
            output = root / "review.json"
            schema.write_text(
                json.dumps({"type": "object", "required": ["status"], "properties": {"status": {"type": "string"}}}),
                encoding="utf-8",
            )
            observed: dict[str, object] = {}

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                observed["encoding"] = encoding
                observed["errors"] = errors
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="访问权限不允许访问套接字")

            report = run_codex_cli_review(
                prompt="return strict JSON",
                schema_path=schema,
                output_path=output,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
                trace_id="stderr-case",
                trace_dir=root / "trace",
            )

            self.assertEqual(observed["encoding"], "utf-8")
            self.assertEqual(observed["errors"], "replace")
            self.assertEqual(report["status"], "unavailable")
            self.assertTrue(report["modelInvoked"])
            self.assertTrue(report["modelProviderStatus"]["modelUnavailable"])
            self.assertIn("访问权限", report["stderr"])
            self.assertIn("访问权限", (root / "trace" / "stderr.txt").read_text(encoding="utf-8"))
            gate_decision = json.loads((root / "trace" / "gate_decision.json").read_text(encoding="utf-8"))
            self.assertEqual(gate_decision["status"], "blocked")
            trace_review = json.loads((root / "trace" / "trace_review.json").read_text(encoding="utf-8"))
            self.assertEqual(trace_review["status"], "blocked")

    def test_model_review_route_policy_marks_remote_routes_as_authorization_required(self) -> None:
        from core.model_review.provider_status import route_policy

        self.assertFalse(route_policy("local_model")["requiresUserAuthorization"])
        self.assertTrue(route_policy("remote_summary_only")["requiresUserAuthorization"])
        self.assertTrue(route_policy("remote_full_visual")["requiresUserAuthorization"])
        self.assertFalse(route_policy("remote_summary_only")["allowsImages"])
        self.assertTrue(route_policy("remote_full_visual")["allowsImages"])

    def test_visual_layout_review_schema_rejects_missing_required_fields(self) -> None:
        from core.model_review.visual_layout_review import validate_visual_layout_model_review

        report = validate_visual_layout_model_review({"status": "pass", "layoutReadabilityAcceptable": True})

        self.assertEqual(report["status"], "fail")
        self.assertIn("missing required model review fields", "; ".join(report["issues"]))
        self.assertIn("sourceProofRolesSeparated", report["missingFields"])

    def test_visual_layout_review_fails_when_any_required_dimension_is_false(self) -> None:
        from core.model_review.visual_layout_review import model_review_to_visual_agent_output

        output = model_review_to_visual_agent_output(
            {
                "status": "pass",
                "layoutMatchesMetaphor": True,
                "primaryShelvesClear": True,
                "layoutReadabilityAcceptable": False,
                "aisleClearanceAcceptable": True,
                "contentDensityAcceptable": True,
                "sourceProofRolesSeparated": True,
                "layerSemanticsAcceptable": True,
                "futureExpansionClear": True,
                "retrievalPathReadable": True,
                "visualNoiseAcceptable": True,
                "nonScreenshotEvidenceChecked": True,
                "blockingReasons": [],
                "visualProblems": [],
                "repairRecommendation": {},
                **_common_model_review_fields(),
            }
        )

        self.assertEqual(output["status"], "fail")
        self.assertEqual(output["layoutReadabilityAcceptable"], "fail")
        self.assertTrue(output["modelProviderStatus"]["schemaValid"])
        self.assertIn("layoutReadabilityAcceptable=false", output["blockingReasons"])

    def test_failed_model_visual_review_blocks_a_to_a_visual_layout_gate(self) -> None:
        from core.model_review.visual_layout_review import model_review_to_visual_agent_output
        from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
        from core.orchestrator.request_context import build_request_context

        context = build_request_context(
            context_id="req-model-backed-visual-review",
            request_kind="draw",
            user_request="system asset DWG warehouse shelf layout",
            allow_cad=True,
        )
        context["agent_outputs"] = {
            "pipeline_asset_governor": {"status": "pass"},
            "pipeline_asset_librarian": {"status": "pass"},
            "pipeline_asset_dwg_curator": {"status": "pass"},
            "pipeline_asset_reuse_auditor": {"status": "pass"},
            "pipeline_visual_layout_reviewer": model_review_to_visual_agent_output(
                {
                    "status": "fail",
                    "layoutMatchesMetaphor": True,
                    "primaryShelvesClear": True,
                    "layoutReadabilityAcceptable": False,
                    "aisleClearanceAcceptable": True,
                    "contentDensityAcceptable": False,
                    "sourceProofRolesSeparated": False,
                    "layerSemanticsAcceptable": False,
                    "futureExpansionClear": True,
                    "retrievalPathReadable": True,
                    "visualNoiseAcceptable": False,
                    "nonScreenshotEvidenceChecked": True,
                    "blockingReasons": ["A2 text is unreadable at warehouse overview scale"],
                    "visualProblems": ["A2 looks like compressed proof panel"],
                    "repairRecommendation": {"mode": "focused_relayout", "targetZone": "A2_ANNOTATION_STYLES"},
                    **_common_model_review_fields(),
                }
            ),
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["status"], "blocked")
        self.assertIn("visual_layout_review", contract["failedHardGates"])
        failures = contract["agentOutputSummary"]["pipeline_visual_layout_reviewer"]["visualFailures"]
        self.assertIn("modelBackedReview", failures)
        self.assertIn("layoutReadabilityAcceptable", failures)

    def test_visual_rack_audit_rejects_failed_model_review_report(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        report = audit_visual_rack_plan(
            visual_rack_plan=_valid_visual_rack_plan(),
            zones=_valid_zones(),
            readability_report=_pass_readability(),
            model_review_report={
                "status": "fail",
                "layoutReadabilityAcceptable": False,
                "blockingReasons": ["A2 text is unreadable at overview scale"],
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("model-backed visual layout review failed", report["issues"])

    def test_visual_acceptance_review_schema_rejects_missing_required_fields(self) -> None:
        from core.model_review.visual_acceptance_review import validate_visual_acceptance_model_review

        report = validate_visual_acceptance_model_review({"status": "pass", "textReadable": True})

        self.assertEqual(report["status"], "fail")
        self.assertIn("missing required model visual acceptance fields", "; ".join(report["issues"]))
        self.assertIn("noMojibake", report["missingFields"])

    def test_model_visual_acceptance_fails_when_any_required_dimension_is_false(self) -> None:
        from core.model_review.visual_acceptance_review import model_review_to_visual_acceptance_output

        output = model_review_to_visual_acceptance_output(
            _valid_visual_acceptance_review(status="pass", textReadable=False)
        )

        self.assertEqual(output["status"], "fail")
        self.assertEqual(output["textReadable"], "fail")
        self.assertTrue(output["modelProviderStatus"]["schemaValid"])
        self.assertIn("textReadable=false", output["blockingReasons"])

    def test_failed_model_visual_acceptance_blocks_a_to_a_visual_acceptance_gate(self) -> None:
        from core.model_review.visual_acceptance_review import model_review_to_visual_acceptance_output
        from core.orchestrator.a_to_a_task_contract import build_a_to_a_task_contract
        from core.orchestrator.request_context import build_request_context

        context = build_request_context(
            context_id="req-model-backed-visual-acceptance",
            request_kind="draw",
            user_request="请做用户可见视觉验收，重点检查乱码、贴边、遮挡、裁剪和可复用边界",
            allow_cad=True,
        )
        context["agent_outputs"] = {
            "pipeline_visual_acceptance_reviewer": model_review_to_visual_acceptance_output(
                _valid_visual_acceptance_review(
                    status="fail",
                    textReadable=False,
                    noMojibake=False,
                    noSevereOverlap=False,
                    reusableOutputLikely=False,
                    blockingReasons=["框内文字像乱码且左侧贴边"],
                    visualProblems=["文字不可复用", "边框与文字冲突"],
                    repairRecommendation={"mode": "focused_text_relayout"},
                )
            )
        }

        contract = build_a_to_a_task_contract(context)

        self.assertEqual(contract["taskKind"], "visual_acceptance_review")
        self.assertEqual(contract["status"], "blocked")
        self.assertIn("visual_acceptance_review", contract["failedHardGates"])
        failures = contract["agentOutputSummary"]["pipeline_visual_acceptance_reviewer"][
            "visualAcceptanceFailures"
        ]
        self.assertIn("modelBackedVisualAcceptance", failures)
        self.assertIn("textReadable", failures)
        self.assertIn("blockingReasons", failures)

    def test_model_visual_acceptance_rejects_direct_execution_or_save(self) -> None:
        from core.model_review.visual_acceptance_review import model_review_to_visual_acceptance_output

        output = model_review_to_visual_acceptance_output(
            _valid_visual_acceptance_review(
                cadCommands=["ERASE ALL"],
                saveCurrentDwg=True,
                executionAuthorized=True,
            )
        )

        self.assertEqual(output["status"], "fail")
        self.assertFalse(output["executionAuthorized"])
        self.assertFalse(output["mayExecuteCad"])
        self.assertFalse(output["savedCurrentDwg"])
        joined = "; ".join(output["modelBackedVisualAcceptance"]["validation"]["issues"])
        self.assertIn("direct CAD commands", joined)
        self.assertIn("save current DWG", joined)
        self.assertIn("authorize execution", joined)

    def test_model_asset_governor_review_rejects_missing_required_fields(self) -> None:
        from core.model_review.asset_governor_review import validate_asset_governor_model_review

        report = validate_asset_governor_model_review(
            {
                "status": "pass",
                "classificationSuggestion": {"assetKind": "style_standard"},
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("missing required model asset governor fields", report["issues"])
        self.assertIn("sourceBoundaryRecommendation", report["missingFields"])

    def test_model_repair_plan_candidate_is_proposal_only_even_when_valid(self) -> None:
        from core.model_review.repair_plan_review import model_review_to_repair_plan_candidate

        output = model_review_to_repair_plan_candidate(
            {
                "status": "pass",
                "scopeMode": "local_repair",
                "rootCause": "wrong dimension text",
                "repairMode": "delete_replace",
                "targetHandles": ["AB12"],
                "targetBbox": {"min": [10.0, 20.0], "max": [80.0, 60.0]},
                "targetLayers": ["CODEX_PREVIEW"],
                "whyLocalRepairIsEnough": "target handle is known and isolated",
                "whyFullRedrawIsNotAllowedOrNeeded": "the rest of the preview is not implicated",
                "requiresUserPermission": False,
                "protectedNeighbors": ["nearby CODEX_PREVIEW labels"],
                "operations": [
                    {
                        "action": "delete_replace",
                        "targetHandles": ["AB12"],
                        "reason": "wrong dimension text",
                    }
                ],
                "evidenceRequired": ["created handle readback", "focused screenshot"],
                "executionPolicy": "proposal_only",
                "blockingReasons": [],
                **_common_model_review_fields(),
            }
        )

        self.assertEqual(output["status"], "pass")
        self.assertFalse(output["executionAuthorized"])
        self.assertFalse(output["mayExecuteCad"])
        self.assertFalse(output["savedCurrentDwg"])
        self.assertEqual(output["repairPlanCandidate"]["targetHandles"], ["AB12"])
        self.assertTrue(output["modelProviderStatus"]["schemaValid"])

    def test_model_repair_plan_rejects_direct_cad_delete_or_save(self) -> None:
        from core.model_review.repair_plan_review import model_review_to_repair_plan_candidate

        output = model_review_to_repair_plan_candidate(
            {
                "status": "pass",
                "scopeMode": "whole_modelspace",
                "targetHandles": [],
                "targetBbox": {},
                "targetLayers": ["0"],
                "operations": [{"action": "delete_all", "reason": "clean up"}],
                "evidenceRequired": [],
                "executionPolicy": "execute_now",
                "blockingReasons": [],
                "cadCommands": ["ERASE ALL"],
                "saveCurrentDwg": True,
            }
        )

        self.assertEqual(output["status"], "fail")
        self.assertFalse(output["executionAuthorized"])
        self.assertFalse(output["mayExecuteCad"])
        self.assertFalse(output["savedCurrentDwg"])
        joined = "; ".join(output["modelBackedRepairPlan"]["validation"]["issues"])
        self.assertIn("proposal_only", joined)
        self.assertIn("direct CAD commands", joined)
        self.assertIn("save current DWG", joined)
        self.assertFalse(output["modelProviderStatus"]["schemaValid"])


if __name__ == "__main__":
    unittest.main()
