from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.model_review.codex_cli_client import CodexCliReviewConfig, run_codex_cli_review
from core.model_review.export_manifest import build_model_export_manifest
from core.model_review.prompt_library import load_prompt_pack
from core.orchestrator.agent_handoff import build_handoff_packet, validate_handoff_packet
from core.orchestrator.closeout_state_machine import evaluate_closeout_state
from core.orchestrator.error_taxonomy import (
    MODEL_BUSINESS_BLOCKED,
    NETWORK_UNAVAILABLE,
    classify_error_category,
)
from core.orchestrator.tool_contract import run_tool_intent


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
NOT_PROVEN = [
    "real OpenAI provider availability",
    "real gpt-5.5 judgement quality",
    "real AutoCAD geometry",
    "user acceptance",
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _status(pass_condition: bool) -> str:
    return "pass" if pass_condition else "fail"


def _export_manifest_gate(run_dir: Path) -> tuple[str, dict[str, Any]]:
    schema_path = PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json"
    allowed = build_model_export_manifest(
        agent_id="pipeline_design_director",
        trace_id="local-hardening-export",
        prompt_text="safe explicit payload only",
        schema_path=schema_path,
        payload_refs=["user_request.json"],
        image_paths=[],
        approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
    )
    blocked = build_model_export_manifest(
        agent_id="pipeline_design_director",
        trace_id="local-hardening-export-blocked",
        prompt_text=f"read {PROJECT_ROOT / 'AGENTS.md'}",
        schema_path=schema_path,
        payload_refs=[],
        image_paths=[],
        approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
    )
    _write_json(run_dir / "export_manifest_allowed.json", allowed)
    _write_json(run_dir / "export_manifest_blocked.json", blocked)
    ok = allowed.get("status") == "pass" and blocked.get("status") == "blocked"
    return _status(ok), {"allowed": allowed.get("status"), "blocked": blocked.get("status")}


def _fake_model_review(run_dir: Path) -> tuple[bool, bool, dict[str, Any]]:
    schema_path = PROJECT_ROOT / "core/model_review/schemas/delivery_claims_review.schema.json"
    output_path = run_dir / "fake_model_review.json"
    captured: dict[str, Any] = {}
    schema = _read_json(schema_path)
    properties = schema.get("properties", {}) if isinstance(schema.get("properties"), dict) else {}
    delivery_enum = properties.get("deliveryDecision", {}).get("enum", [])
    opening_enum = properties.get("openingLine", {}).get("enum", [])
    delivery_decision = delivery_enum[0] if delivery_enum else "ready_to_ask_user_review"
    opening_line = opening_enum[0] if opening_enum else "可验收"

    def fake_runner(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        captured["cwd"] = str(Path(kwargs["cwd"]).resolve())
        output_index = command.index("--output-last-message") + 1
        Path(command[output_index]).write_text(
            json.dumps(
                {
                    "status": "pass",
                    "decision": "pass",
                    "deliveryDecision": delivery_decision,
                    "openingLine": opening_line,
                    "whatChanged": ["local hardening fixture executed without network"],
                    "evidenceProves": [
                        "export manifest, repo-external cwd, context leak audit, and schema-visible fields are wired locally"
                    ],
                    "evidenceDoesNotProve": NOT_PROVEN,
                    "lookHereFirst": ["model_agent_local_hardening_proof.json"],
                    "usefulUserFeedback": "Review local proof boundaries before treating any model or CAD claim as accepted.",
                    "blockingReasons": [],
                    "statePatch": {
                        "phase": "local_proof",
                        "phaseLabelForUser": "本地证明",
                        "completedEvidence": [],
                        "pendingEvidence": [],
                        "pendingUserAction": "",
                        "blockedReason": "",
                        "nextSafeAction": "continue",
                    },
                    "finalResponseAllowedClaims": ["local fixture only"],
                    "evidenceUsed": ["fixture"],
                    "evidenceMissing": [],
                    "assumptions": [],
                    "alternativesConsidered": [],
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
                    "toolIntent": None,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    report = run_codex_cli_review(
        prompt="return local fixture JSON",
        schema_path=schema_path,
        output_path=output_path,
        config=CodexCliReviewConfig(enabled=True),
        runner=fake_runner,
        cwd=PROJECT_ROOT,
        trace_id="local-hardening-fake-model",
        trace_dir=run_dir / "fake_model_trace",
    )
    cwd_path = Path(str(captured.get("cwd") or "")).resolve()
    repo_external = cwd_path and not cwd_path.is_relative_to(PROJECT_ROOT.resolve())
    audit = _read_json(run_dir / "fake_model_trace" / "context_leak_audit.json")
    return bool(repo_external), bool(audit.get("unexpectedProjectContextLoaded")), report


def _decision_chain_fields() -> tuple[str, dict[str, Any]]:
    missing_by_schema: dict[str, list[str]] = {}
    for schema_path in sorted((PROJECT_ROOT / "core/model_review/schemas").glob("*.schema.json")):
        schema = _read_json(schema_path)
        required = set(schema.get("required", []))
        missing = sorted(VISIBLE_AUDIT_FIELDS - required)
        if missing:
            missing_by_schema[schema_path.name] = missing
    prompt = load_prompt_pack("pipeline_delivery").render_prompt(
        {
            "userRequest": "local proof",
            "taskContext": {"taskKind": "delivery"},
            "evidenceRefs": ["fake_model_trace/export_manifest.json"],
            "statePatchRequest": {"phase": "local_proof"},
            "agentSpecific": {},
        }
    )
    prompt_ok = "Do not expose raw chain-of-thought" in prompt and "visible audit fields" in prompt
    return _status(not missing_by_schema and prompt_ok), {"missingBySchema": missing_by_schema, "promptInstruction": prompt_ok}


def _handoff_packets(run_dir: Path) -> tuple[str, dict[str, Any]]:
    source = run_dir / "agent_outputs" / "pipeline_design_director.json"
    output = {
        "status": "pass",
        "decision": "pass",
        "statePatch": {"phase": "local_proof"},
        "evidenceRefs": ["fake_model_trace/normalized_output.json"],
        "evidenceMissing": [],
        "openQuestions": [],
        "nextRequiredEvidence": [],
        "finalResponseAllowedClaims": ["handoff fixture only"],
        "blockingReasons": [],
    }
    _write_json(source, output)
    packet = build_handoff_packet(
        output,
        from_agent_id="pipeline_design_director",
        to_agent_ids=["pipeline_style_generator"],
        source_path=source,
    )
    validation = validate_handoff_packet(packet)
    _write_json(run_dir / "agent_outputs" / "pipeline_design_director.handoff.json", packet)
    return _status(validation.get("status") == "pass" and bool(packet.get("sha256OfSourceOutput"))), validation


def _tool_intent_fixtures(run_dir: Path) -> tuple[str, dict[str, Any]]:
    read_trace = run_tool_intent(
        run_dir,
        {
            "schemaVersion": "tool-intent/v1",
            "toolIntentId": "intent-read-run-package",
            "requestedByAgentId": "pipeline_design_director",
            "toolName": "read_run_package",
            "purpose": "local proof read-only fixture",
            "inputs": {"paths": ["user_request.json"]},
            "targetScope": {"scopeType": "run_package", "scopeRef": "current_run"},
            "riskLevel": "low",
            "permissionClass": "read_only",
            "expectedEvidence": ["tool trace"],
            "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
        },
        run_id=run_dir.name,
    )
    blocked_trace = run_tool_intent(
        run_dir,
        {
            "schemaVersion": "tool-intent/v1",
            "toolIntentId": "intent-save-blocked",
            "requestedByAgentId": "pipeline_design_director",
            "toolName": "save_current_dwg",
            "purpose": "prove blocked save request",
            "inputs": {},
            "targetScope": {"scopeType": "current_dwg", "scopeRef": "active_document"},
            "riskLevel": "critical",
            "permissionClass": "save_current_dwg",
            "expectedEvidence": ["blocked trace"],
            "forbiddenEffects": ["dwg_save"],
            "requestedEffects": ["dwg_save"],
        },
        run_id=run_dir.name,
    )
    ok = (
        read_trace.get("orchestratorDecision") == "allowed"
        and read_trace.get("executionStatus") == "executed"
        and blocked_trace.get("orchestratorDecision") == "blocked"
        and blocked_trace.get("executionStatus") == "blocked_before_execution"
    )
    return _status(ok), {"readOnly": read_trace.get("orchestratorDecision"), "blockedSave": blocked_trace.get("orchestratorDecision")}


def _closeout_state_machine() -> tuple[str, dict[str, Any]]:
    blocked = evaluate_closeout_state(driver_mode="fake_driver_preflight", cadGeometryVerified=False)
    ready = evaluate_closeout_state(
        model_ok=True,
        validation_ok=True,
        dry_run_ok=True,
        readback_ok=True,
        target_layer="CODEX_PREVIEW",
        saved_current_dwg=False,
        visual_acceptance_ok=True,
        neighbor_protection_ok=True,
    )
    ok = blocked["state"] == "cad_evidence_missing" and ready["state"] == "ready_for_user_review"
    return _status(ok), {"blocked": blocked["state"], "ready": ready["state"]}


def _error_taxonomy() -> tuple[str, dict[str, Any]]:
    network = classify_error_category(stderr="websocket failed while connecting to api.openai.com")
    business = classify_error_category(
        review={"status": "unavailable", "modelInvoked": True},
        validation={"status": "pass", "issues": [], "missingFields": []},
    )
    ok = network == NETWORK_UNAVAILABLE and business == MODEL_BUSINESS_BLOCKED
    return _status(ok), {"network": network, "business": business}


def build_proof(run_dir: Path) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "user_request.json", {"userRequest": "local hardening proof"})
    export_status, export_detail = _export_manifest_gate(run_dir)
    repo_external, context_leak, fake_model = _fake_model_review(run_dir)
    decision_status, decision_detail = _decision_chain_fields()
    handoff_status, handoff_detail = _handoff_packets(run_dir)
    tool_status, tool_detail = _tool_intent_fixtures(run_dir)
    closeout_status, closeout_detail = _closeout_state_machine()
    taxonomy_status, taxonomy_detail = _error_taxonomy()

    statuses = [
        export_status,
        _status(repo_external and not context_leak),
        decision_status,
        handoff_status,
        tool_status,
        closeout_status,
        taxonomy_status,
    ]
    proof = {
        "schemaVersion": "model-agent-local-hardening-proof/v1",
        "status": "pass" if all(status == "pass" for status in statuses) else "fail",
        "exportManifestGate": export_status,
        "repoExternalCwd": bool(repo_external),
        "unexpectedProjectContextLoaded": bool(context_leak),
        "decisionChainFields": decision_status,
        "handoffPackets": handoff_status,
        "toolIntentFixtures": tool_status,
        "closeoutStateMachine": closeout_status,
        "errorTaxonomy": taxonomy_status,
        "details": {
            "exportManifestGate": export_detail,
            "modelReviewStatus": fake_model.get("status"),
            "decisionChainFields": decision_detail,
            "handoffPackets": handoff_detail,
            "toolIntentFixtures": tool_detail,
            "closeoutStateMachine": closeout_detail,
            "errorTaxonomy": taxonomy_detail,
        },
        "notProven": NOT_PROVEN,
        "reportPath": str(run_dir / "model_agent_local_hardening_proof.json"),
    }
    _write_json(run_dir / "model_agent_local_hardening_proof.json", proof)
    return proof


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run no-network model-agent local hardening proof.")
    parser.add_argument("--run-id", default="local-hardening-proof")
    parser.add_argument("--output-root", default=str(PROJECT_ROOT / "output" / "runs"))
    args = parser.parse_args(argv)

    run_dir = Path(args.output_root) / str(args.run_id)
    proof = build_proof(run_dir)
    print(json.dumps(proof, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if proof["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
