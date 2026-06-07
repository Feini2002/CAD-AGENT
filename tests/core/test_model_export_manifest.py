from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ModelExportManifestTests(unittest.TestCase):
    def test_export_manifest_allows_explicit_prompt_schema_and_payload(self) -> None:
        from core.model_review.export_manifest import build_model_export_manifest

        manifest = build_model_export_manifest(
            agent_id="pipeline_design_director",
            trace_id="trace-1",
            prompt_text="safe prompt",
            schema_path=PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json",
            payload_refs=["user_request.json", "context_pack.json"],
            image_paths=[],
            approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
        )

        self.assertEqual(manifest["schemaVersion"], "model-export-manifest/v1")
        self.assertEqual(manifest["status"], "pass")
        self.assertEqual(manifest["route"], "codex_cli_local")
        self.assertEqual(manifest["sentArtifacts"][0]["kind"], "prompt_text")
        self.assertEqual(manifest["forbiddenScan"]["secretLikeCount"], 0)
        self.assertEqual(manifest["unexpectedLocalFiles"], [])
        self.assertEqual(manifest["blockedArtifacts"], [])

    def test_export_manifest_blocks_unapproved_local_file(self) -> None:
        from core.model_review.export_manifest import build_model_export_manifest

        with temporary_artifact_dir("model_export_manifest_block") as root:
            secret = root / "not_in_evidence_bundle.txt"
            secret.write_text("LOCAL_ONLY_PROBE", encoding="utf-8")

            manifest = build_model_export_manifest(
                agent_id="pipeline_design_director",
                trace_id="trace-2",
                prompt_text=f"read {secret}",
                schema_path=PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json",
                payload_refs=[],
                image_paths=[],
                approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
            )

        self.assertEqual(manifest["status"], "blocked")
        self.assertIn("unauthorized_local_path", manifest["blockingReasons"])
        self.assertTrue(manifest["unexpectedLocalFiles"])
        self.assertEqual(manifest["blockedArtifacts"][0]["kind"], "unauthorized_local_path")

    def test_export_manifest_schema_is_registered(self) -> None:
        from core.schemas.registry import get_schema_path, infer_model_type

        path = get_schema_path("model_export_manifest")
        self.assertTrue(path.is_file())

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["title"], "Model Export Manifest")

        manifest = {
            "schemaVersion": "model-export-manifest/v1",
            "status": "pass",
            "route": "codex_cli_local",
            "agentId": "pipeline_design_director",
            "traceId": "trace-1",
            "approvalBasis": [],
            "sentArtifacts": [],
            "blockedArtifacts": [],
            "unexpectedLocalFiles": [],
            "forbiddenScan": {
                "secretLikeCount": 0,
                "wholeRepoRequested": False,
                "wholeOutputRequested": False,
                "fullScreenScreenshotRequested": False,
            },
            "blockingReasons": [],
            "evidenceBoundary": [],
        }
        self.assertEqual(infer_model_type(manifest), "model_export_manifest")

    def test_evidence_portfolio_is_minimal_and_export_manifest_allowlisted(self) -> None:
        from core.model_review.evidence_portfolio import build_evidence_portfolio
        from core.model_review.export_manifest import build_model_export_manifest

        with temporary_artifact_dir("evidence_portfolio_export_safe") as root:
            run_dir = root / "run"
            run_dir.mkdir()
            (run_dir / "cad_reports").mkdir()
            (run_dir / "cad_reports" / "readback_summary.json").write_text(
                json.dumps(
                    {
                        "readbackStatus": "ok",
                        "createdHandleCount": 3,
                        "targetLayer": "CODEX_PREVIEW",
                        "savedCurrentDwg": False,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            portfolio = build_evidence_portfolio(
                run_dir=run_dir,
                user_request="只做 no-CAD 认知闭环证明。",
                route="standard_draw",
                task_kind="ordinary_orchestration",
                hard_gates=["validate_plan", "dry_run", "cad_readback"],
                evidence_refs=["cad_reports/readback_summary.json"],
                memory_refs=["agents/pipeline/audit/training_memory.json"],
                history_refs=["docs/status/issues.md"],
            )

            portfolio_path = run_dir / portfolio["portfolioRef"]
            self.assertTrue(portfolio_path.is_file())
            saved = json.loads(portfolio_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["schemaVersion"], "evidence-portfolio/v1")
            self.assertEqual(saved["status"], "ready")
            self.assertEqual(saved["evidenceBoundary"]["cadWriteAuthorized"], False)
            self.assertIn("cad_reports/readback_summary.json", saved["exportRefs"])
            self.assertIn("截图只能作为 visual_aid_only", saved["evidenceBoundary"]["notProofOf"])

            manifest = build_model_export_manifest(
                agent_id="pipeline_design_reviewer",
                trace_id="portfolio-trace",
                prompt_text="Use the explicit evidence portfolio ref only.",
                schema_path=PROJECT_ROOT / "core/model_review/schemas/design_review.schema.json",
                payload_refs=[portfolio_path],
                image_paths=[],
                approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
            )

            self.assertEqual(manifest["status"], "pass")
            self.assertTrue(any(item["kind"] == "payload_ref" for item in manifest["sentArtifacts"]))


if __name__ == "__main__":
    unittest.main()
