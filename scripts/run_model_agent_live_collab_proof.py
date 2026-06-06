#!/usr/bin/env python
"""Run MODEL-AGENT-LIVE-COLLAB-PROOF-01 against a run package."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.model_review.codex_cli_client import CodexCliReviewConfig
from core.orchestrator.model_agent_chain_runtime import run_model_agent_live_collab_proof
from core.orchestrator.request_context import build_request_context
from core.orchestrator.run_package_state import DEFAULT_RUN_ROOT, create_run_package
from core.runtime.encoding_guard import configure_utf8_process


DEFAULT_REQUEST = "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _create_run(*, run_id: str, request_text: str) -> Path:
    context = build_request_context(
        context_id=run_id,
        request_kind="draw",
        user_request=request_text,
        available_inputs=["cad_plan"],
        allow_cad=False,
    )
    state = create_run_package(
        run_id,
        user_request={"text": request_text, "requestKind": "draw"},
        context_pack={
            "schemaVersion": "run-package-context-pack/v1",
            "runId": run_id,
            "requestContext": context,
        },
        root_dir=DEFAULT_RUN_ROOT,
    )
    return Path(state["runDir"])


def _state_patch(phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "phaseLabelForUser": phase,
        "completedEvidence": ["local fixture model output"],
        "pendingEvidence": [],
        "pendingUserAction": "",
        "blockedReason": "",
        "nextSafeAction": "continue",
    }


def _learning_candidate() -> dict[str, Any]:
    return {
        "decision": "not_required",
        "trigger": "not_required",
        "responsibleAgentIds": [],
        "errorPattern": "",
        "correctPattern": "",
        "promptDelta": "",
        "checkerDelta": "",
        "retestOriginalTask": False,
    }


def _fixture_output_for_schema(schema_path: str) -> dict[str, Any]:
    name = Path(schema_path).name
    learning_candidate = _learning_candidate()
    common = {
        "decision": "pass",
        "learningCandidate": learning_candidate,
        "statePatch": _state_patch(name),
        "finalResponseAllowedClaims": ["local fixture agent-chain output only"],
        "evidenceUsed": ["local_fixture_model", "rule_context_pack", "upstream handoff packets"],
        "evidenceMissing": [],
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
        "toolIntent": None,
    }
    if name == "design_director_review.schema.json":
        return {
            "status": "pass",
            "designStrategy": {"styleCandidatePolicy": "multiple"},
            "drawingTypeDecision": "presentation_preview",
            "expressionPurpose": "compare readable CAD expression options",
            "designIntent": "show a compact tea table symbol with Chinese labels",
            "audienceAndUse": "user review before CAD execution",
            "constraints": ["no direct CAD write from model", "CODEX_PREVIEW only after controlled execution"],
            "requiredChildAgents": ["pipeline_style_generator", "pipeline_design_reviewer"],
            "openQuestions": [],
            "evidenceBoundary": {"notProofOf": ["real model quality", "CAD geometry"]},
            **common,
        }
    if name == "style_generation_review.schema.json":
        return {
            "status": "pass",
            "styleDecision": "multiple",
            "styleCandidates": [{"id": "A"}, {"id": "B"}],
            "selectedStyleCandidate": "A",
            "styleParameterGrammar": {"scale": "model_units"},
            "candidateTradeoffs": [{"id": "A", "tradeoff": "more readable"}],
            "needsUserChoice": False,
            "styleWaiverReason": "",
            "candidateCountPolicy": "explicit_multi_candidate",
            "requestedCandidateCount": 2,
            "candidateLabelPolicy": "abc",
            "creativityPolicy": "contextual_not_forced",
            "semanticRoutingConfidence": "high",
            **common,
        }
    if name == "design_review.schema.json":
        return {
            "status": "pass",
            "designReview": "fixture style candidates are readable enough for intent drafting",
            "professionalDrawingLike": True,
            "readability": True,
            "industryHabitFit": True,
            "scaleAndProportionFit": True,
            "styleCandidateFit": True,
            "contentMatchesDesignPurpose": True,
            "needsUserChoice": False,
            "repairOrRegenerateRecommendation": {},
            **common,
        }
    raise ValueError(f"fixture model output is not defined for schema: {schema_path}")


def _fixture_model_runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
    schema_path = command[command.index("--output-schema") + 1]
    output_path = Path(command[command.index("--output-last-message") + 1])
    output_path.write_text(
        json.dumps(_fixture_output_for_schema(schema_path), ensure_ascii=False),
        encoding="utf-8",
    )
    return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


def _local_agent_chain_proof(result: dict[str, Any]) -> dict[str, Any]:
    model_agents = {
        str(item.get("agentId")): item
        for item in result.get("agentOutputChain", [])
        if str(item.get("agentId")) in {"pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"}
    }
    required_agents_ready = all(
        model_agents.get(agent_id, {}).get("status") == "pass"
        and model_agents.get(agent_id, {}).get("modelInvoked") is True
        and model_agents.get(agent_id, {}).get("schemaValid") is True
        and bool(model_agents.get(agent_id, {}).get("handoffPath"))
        and bool(model_agents.get(agent_id, {}).get("handoffSha256"))
        for agent_id in ("pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer")
    )
    agent_chain_ready = (
        result.get("modelChainStatus") == "ready"
        and result.get("conflictHandling", {}).get("status") == "pass"
        and required_agents_ready
    )
    fake_cad_boundary_preserved = (
        result.get("cadProof", {}).get("driverMode") == "fake_driver_preflight"
        and result.get("cadProof", {}).get("cadGeometryVerified") is False
    )
    return {
        "schemaVersion": "local-agent-chain-proof/v1",
        "status": "pass" if agent_chain_ready and fake_cad_boundary_preserved else "fail",
        "agentChainReady": bool(agent_chain_ready),
        "requiredModelAgentsReady": bool(required_agents_ready),
        "fakeCadBoundaryPreserved": bool(fake_cad_boundary_preserved),
        "notProven": ["real OpenAI provider availability", "real gpt-5.5 judgement quality", "real AutoCAD geometry"],
    }


def main(argv: list[str] | None = None) -> int:
    configure_utf8_process()
    parser = argparse.ArgumentParser(description="Run the model-agent live collaboration proof.")
    parser.add_argument("--run-dir", type=Path, default=None, help="Existing run package directory.")
    parser.add_argument("--run-id", default=f"model-agent-live-collab-proof-{_timestamp()}")
    parser.add_argument("--request", default=DEFAULT_REQUEST)
    parser.add_argument(
        "--driver-mode",
        choices=["autocad_existing", "fake_driver_preflight"],
        default="autocad_existing",
        help="CAD driver mode. autocad_existing connects to an already-open AutoCAD session.",
    )
    parser.add_argument("--base-x", type=float, default=68000.0)
    parser.add_argument("--base-y", type=float, default=36000.0)
    parser.add_argument("--base-z", type=float, default=0.0)
    parser.add_argument("--invoke-model", action="store_true", help="Invoke ready Prompt Packs through Codex CLI.")
    parser.add_argument(
        "--fixture-model",
        action="store_true",
        help="Use local schema-shaped model fixtures; never invoke Codex CLI or the model provider.",
    )
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument(
        "--ignore-user-config",
        action="store_true",
        help="Run Codex CLI model bridge with --ignore-user-config to avoid incompatible local config.",
    )
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        help="Run Codex CLI model bridge with --skip-git-repo-check, useful when --model-cwd is outside the repo.",
    )
    parser.add_argument(
        "--model-cwd",
        type=Path,
        default=None,
        help="Working directory for Codex CLI model bridge. Use a temp dir to avoid loading repo AGENTS.md.",
    )
    parser.add_argument(
        "--continue-cad-on-model-blocked",
        action="store_true",
        help="Still run controlled preview CAD validation when model outputs are blocked. The result remains model-chain blocked.",
    )
    args = parser.parse_args(argv)
    if args.fixture_model and args.invoke_model:
        parser.error("--fixture-model and --invoke-model are mutually exclusive")

    run_dir = args.run_dir or _create_run(run_id=args.run_id, request_text=args.request)
    config = CodexCliReviewConfig(
        enabled=bool(args.invoke_model or args.fixture_model),
        model=args.model,
        timeout_seconds=int(args.timeout_seconds),
        ignore_user_config=bool(args.ignore_user_config),
        skip_git_repo_check=bool(args.skip_git_repo_check),
    )
    result = run_model_agent_live_collab_proof(
        run_dir,
        config=config,
        cwd=args.model_cwd,
        driver_mode=args.driver_mode,
        base_point=[args.base_x, args.base_y, args.base_z],
        runner=_fixture_model_runner if args.fixture_model else None,
        continue_cad_on_model_blocked=bool(args.continue_cad_on_model_blocked),
    )
    if args.fixture_model:
        result["localFixtureModel"] = {
            "status": "used",
            "networkUsed": False,
            "codexCliInvoked": False,
            "modelProviderInvoked": False,
            "purpose": "agent-chain-only local fixture proof",
        }
        result["localAgentChainProof"] = _local_agent_chain_proof(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    real_cad_verified = result.get("cadProof", {}).get("cadGeometryVerified") is True
    local_fixture_pass = (
        args.fixture_model
        and args.driver_mode == "fake_driver_preflight"
        and result.get("localAgentChainProof", {}).get("status") == "pass"
    )
    return 0 if real_cad_verified or local_fixture_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
