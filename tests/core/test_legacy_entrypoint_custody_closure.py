from __future__ import annotations

import json
import unittest

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


class LegacyEntrypointCustodyClosureTests(unittest.TestCase):
    def test_repo_entrypoints_are_fully_classified_without_warning_backlog(self) -> None:
        from core.entrypoint_custody.audit import build_entrypoint_custody_audit

        audit = build_entrypoint_custody_audit(PROJECT_ROOT)
        unclassified = [
            finding
            for finding in audit["findings"]
            if finding.get("code") == "unregistered_repo_entrypoint"
        ]

        self.assertEqual(unclassified, [])
        self.assertEqual(audit["summary"]["warningCount"], 0, audit["summary"])

    def test_training_claim_audit_blocks_growth_without_renderer_memory_or_live_reasoning(self) -> None:
        from core.training.report_claim_audit import audit_training_report_claims

        with temporary_artifact_dir("legacy-training-claim-closure") as tmp:
            report_path = tmp / "growth_report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "replayMode": "growth_replay",
                        "passType": "growth_replay",
                        "capabilityProfile": {
                            "profileSource": {
                                "status": "pass",
                                "role": "active_fact_source",
                                "path": "docs/training/training-sources.json",
                            },
                            "profiles": [],
                        },
                        "requiredFeaturesConsumed": False,
                        "rendererDecision": {},
                        "liveReasoning": {"required": True, "status": "not_run"},
                        "memoryWriteMode": "overwrite",
                        "templateLock": {"status": "not_checked"},
                        "modelSuggestion": {"text": "use a richer renderer"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            audit = audit_training_report_claims(PROJECT_ROOT, [report_path])
            codes = {finding["code"] for finding in audit["findings"]}

        self.assertIn("renderer_decision_missing", codes)
        self.assertIn("required_features_not_consumed", codes)
        self.assertIn("live_reasoning_missing_or_not_pass", codes)
        self.assertIn("memory_no_downgrade_missing", codes)
        self.assertIn("template_lock_not_checked", codes)
        self.assertIn("model_suggestion_missing_disposition", codes)

    def test_model_trace_claim_audit_blocks_trace_summary_only_live_claim(self) -> None:
        from core.model_review.trace_claim_audit import audit_model_trace_claims

        with temporary_artifact_dir("legacy-model-trace-claim-closure") as tmp:
            trace_dir = tmp / "model_traces" / "pipeline_design_director" / "trace-1"
            trace_dir.mkdir(parents=True)
            trace_summary = trace_dir / "trace_summary.md"
            trace_summary.write_text("trace summary only\n", encoding="utf-8")
            (tmp / "claim.json").write_text(
                json.dumps(
                    {
                        "modelInvoked": True,
                        "liveProviderPass": True,
                        "modelUnavailable": False,
                        "traceRef": "model_traces/pipeline_design_director/trace-1/trace_summary.md",
                        "requiresDownstreamConsumption": True,
                        "downstreamRefs": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            audit = audit_model_trace_claims(PROJECT_ROOT, [tmp])
            codes = {finding["code"] for finding in audit["findings"]}

        self.assertIn("trace_only_live_claim", codes)
        self.assertIn("model_trace_missing_command", codes)
        self.assertIn("model_trace_missing_normalized_output", codes)
        self.assertIn("model_trace_missing_downstream_refs", codes)

