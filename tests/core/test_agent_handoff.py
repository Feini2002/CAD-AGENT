from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _agent_output(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "pass",
        "decision": "pass",
        "statePatch": {"phase": "reviewed"},
        "evidenceRefs": ["cad_reports/readback_summary.json"],
        "evidenceUsed": ["cad_reports/readback_summary.json"],
        "evidenceMissing": [],
        "openQuestions": [],
        "nextRequiredEvidence": [],
        "finalResponseAllowedClaims": ["no-CAD handoff only"],
        "blockingReasons": [],
    }
    payload.update(overrides)
    return payload


class AgentHandoffTests(unittest.TestCase):
    def test_handoff_packet_schema_registered_and_inferable(self) -> None:
        from core.schemas.registry import get_schema_path, infer_model_type

        path = get_schema_path("agent_handoff_packet")
        self.assertTrue(path.is_file())
        self.assertEqual(
            infer_model_type(
                {
                    "schemaVersion": "handoff_packet/v1",
                    "fromAgentId": "pipeline_design_director",
                    "toAgentIds": ["pipeline_style_generator"],
                    "status": "ready",
                    "decisionSummary": "pass",
                    "statePatch": {},
                    "evidenceRefs": [],
                    "evidenceMissing": [],
                    "openQuestions": [],
                    "downstreamInstructions": [],
                    "allowedClaims": [],
                    "forbiddenClaims": [],
                    "sha256OfSourceOutput": "abc",
                }
            ),
            "agent_handoff_packet",
        )

    def test_build_handoff_packet_hashes_source_and_preserves_evidence_only(self) -> None:
        from core.orchestrator.agent_handoff import build_handoff_packet

        with temporary_artifact_dir("agent_handoff_packet") as root:
            source = root / "agent_outputs" / "pipeline_design_director.json"
            output = _agent_output()
            _write_json(source, output)

            packet = build_handoff_packet(
                output,
                from_agent_id="pipeline_design_director",
                to_agent_ids=["pipeline_style_generator"],
                source_path=source,
            )

            self.assertEqual(packet["schemaVersion"], "handoff_packet/v1")
            self.assertEqual(packet["status"], "ready")
            self.assertEqual(packet["evidenceRefs"], ["cad_reports/readback_summary.json"])
            self.assertEqual(packet["allowedClaims"], ["no-CAD handoff only"])
            self.assertTrue(packet["sha256OfSourceOutput"])
            self.assertIn("must not invent evidence", packet["forbiddenClaims"])

    def test_blocked_model_output_builds_blocked_handoff(self) -> None:
        from core.orchestrator.agent_handoff import build_handoff_packet

        with temporary_artifact_dir("agent_handoff_blocked") as root:
            source = root / "agent_outputs" / "pipeline_style_generator.json"
            output = _agent_output(status="unavailable", decision="unavailable", blockingReasons=["provider_unavailable"])
            _write_json(source, output)

            packet = build_handoff_packet(
                output,
                from_agent_id="pipeline_style_generator",
                to_agent_ids=["pipeline_design_reviewer"],
                source_path=source,
            )

            self.assertEqual(packet["status"], "blocked")
            self.assertIn("provider_unavailable", packet["downstreamInstructions"])


if __name__ == "__main__":
    unittest.main()
