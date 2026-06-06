#!/usr/bin/env python3
"""Probe the Python -> Codex CLI model-review bridge.

By default this script is a dry run. Use --execute only after the user has
authorized a real model call, because Codex CLI contacts the configured model
provider.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Sequence

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.probe_codex_cli_model_review.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.model_review.codex_cli_client import (
    DEFAULT_CODEX_CLI_MODEL,
    DEFAULT_CODEX_CLI_REASONING_EFFORT,
    CodexCliReviewConfig,
    run_codex_cli_review,
)


DEFAULT_PROBE_OUTPUT = "output/model_reviews/codex_cli_link_probe_visual_acceptance.json"

CONNECTIVITY_PROMPT = """
You are running a connectivity probe for a CAD Agent model-review bridge.
Do not inspect files, do not call tools, do not execute CAD, and do not make
any claim about a real drawing.

Return exactly one JSON object matching the provided schema.
For this synthetic probe only, set status to pass, all boolean fields to true,
blockingReasons and visualProblems to empty arrays, and repairRecommendation to
{"mode":"none","reason":"synthetic connectivity probe only","targetZone":"none","targetHandles":[],"nextChecks":[]}.
Set lookHereFirst to ["synthetic probe only"].
Also include decision, assumptions, alternativesConsidered, blockingReasons,
nextRequiredEvidence, learningCandidate, statePatch, finalResponseAllowedClaims,
evidenceUsed, and evidenceMissing. statePatch must contain phase,
phaseLabelForUser, completedEvidence, pendingEvidence, pendingUserAction,
blockedReason, and nextSafeAction. Include toolIntent and set it to null.
""".strip()


def _resolve_workspace_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _dump(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually invoke Codex CLI and the configured model provider.",
    )
    parser.add_argument("--model", default=DEFAULT_CODEX_CLI_MODEL, help="Model name passed to Codex CLI.")
    parser.add_argument(
        "--reasoning-effort",
        default=DEFAULT_CODEX_CLI_REASONING_EFFORT,
        help="Codex CLI model_reasoning_effort config value.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument(
        "--schema",
        default="core/model_review/schemas/visual_acceptance_review.schema.json",
        help="Schema used for the synthetic model response.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_PROBE_OUTPUT,
        help="Where Codex CLI writes its last JSON message.",
    )
    parser.add_argument(
        "--workdir",
        default=str(Path(tempfile.gettempdir()) / "cad-agent-model-bridge" / "probe-dry-run"),
        help="Local working directory for Codex CLI when repo context is not allowed.",
    )
    parser.add_argument(
        "--allow-repo-context",
        action="store_true",
        help="Allow Codex CLI to run from the repo root and load project rules.",
    )
    parser.add_argument(
        "--ignore-user-config",
        action="store_true",
        help="Pass --ignore-user-config to Codex CLI; auth still uses CODEX_HOME.",
    )
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        help="Pass --skip-git-repo-check when the model bridge cwd is repo-external.",
    )
    parser.add_argument(
        "--prompt-pack",
        "--agent-id",
        dest="prompt_pack",
        default="",
        help="Use a registered core/model_review prompt pack instead of the synthetic connectivity prompt.",
    )
    return parser


def _synthetic_prompt_pack_payload(agent_id: str) -> dict[str, object]:
    return {
        "userRequest": f"Synthetic prompt-pack probe for {agent_id}.",
        "taskContext": {
            "taskKind": "synthetic_prompt_pack_probe",
            "route": "probe_only",
            "targetLayer": "CODEX_PREVIEW",
        },
        "evidenceRefs": [],
        "statePatchRequest": {
            "phase": "model_review_probe",
            "phaseLabelForUser": "模型 Prompt Pack 探针",
        },
        "agentSpecific": {},
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prompt_pack = None
    prompt_payload: dict[str, object] | None = None
    if args.prompt_pack:
        from core.model_review.prompt_library import load_prompt_pack

        prompt_pack = load_prompt_pack(str(args.prompt_pack))
        prompt_payload = _synthetic_prompt_pack_payload(prompt_pack.agent_id)
        schema_path = prompt_pack.output_schema_path
        output_arg = (
            f"output/model_reviews/{prompt_pack.agent_id}_probe.json"
            if args.output == DEFAULT_PROBE_OUTPUT
            else args.output
        )
    else:
        schema_path = _resolve_workspace_path(args.schema)
        output_arg = args.output
    output_path = _resolve_workspace_path(output_arg)
    if args.allow_repo_context:
        codex_cwd = PROJECT_ROOT
    else:
        codex_cwd = _resolve_workspace_path(args.workdir)
        codex_cwd.mkdir(parents=True, exist_ok=True)

    config = CodexCliReviewConfig(
        enabled=bool(args.execute),
        model=str(args.model),
        reasoning_effort=str(args.reasoning_effort),
        timeout_seconds=int(args.timeout_seconds),
        sandbox="read-only",
        executable="codex.cmd",
        ignore_rules=not bool(args.allow_repo_context),
        ignore_user_config=bool(args.ignore_user_config),
        skip_git_repo_check=bool(args.skip_git_repo_check),
    )

    if not args.execute:
        payload: dict[str, object] = {
            "status": "dry_run",
            "modelInvoked": False,
            "wouldInvoke": True,
            "provider": "codex_cli",
            "model": config.model,
            "reasoningEffort": config.reasoning_effort,
            "modelPolicy": f"{config.model}:{config.reasoning_effort}",
            "route": "codex_cli_local",
            "schema": str(schema_path),
            "output": str(output_path),
            "codexCwd": str(codex_cwd),
            "repoExternalCwd": not Path(codex_cwd).resolve().is_relative_to(PROJECT_ROOT.resolve()),
            "exportManifestStatus": "would_check",
            "unexpectedProjectContextLoaded": False,
            "ignoreRules": config.ignore_rules,
            "ignoreUserConfig": config.ignore_user_config,
            "skipGitRepoCheck": config.skip_git_repo_check,
            "dataBoundary": [
                "synthetic prompt only",
                "schema path",
                "no CAD files",
                "no DWG writes",
                "no project rules unless --allow-repo-context is set",
            ],
            "executeCommand": (
                "scripts/probe_codex_cli_model_review.py --execute "
                f"--model {config.model} --reasoning-effort {config.reasoning_effort}"
                f"{' --ignore-user-config' if config.ignore_user_config else ''}"
                f"{' --skip-git-repo-check' if config.skip_git_repo_check else ''}"
            ),
        }
        if prompt_pack is not None and prompt_payload is not None:
            rendered_prompt = prompt_pack.render_prompt(prompt_payload)
            payload.update(
                {
                    "promptPackId": prompt_pack.agent_id,
                    "promptPackVersion": prompt_pack.version,
                    "taskType": prompt_pack.task_type,
                    "renderedPromptChars": len(rendered_prompt),
                }
            )
        _dump(payload)
        return 0

    if prompt_pack is not None and prompt_payload is not None:
        from core.model_review.prompt_library import run_prompt_pack_review

        report = run_prompt_pack_review(
            agent_id=prompt_pack.agent_id,
            payload=prompt_payload,
            run_dir=PROJECT_ROOT / "output" / "model_reviews" / "codex_cli_prompt_pack_probe_run",
            output_path=output_path,
            config=config,
            cwd=codex_cwd,
            trace_id=f"{prompt_pack.agent_id}-probe",
        )
        _dump(report)
        provider_status = report.get("modelProviderStatus", {})
        linked = (
            isinstance(provider_status, dict)
            and provider_status.get("modelInvoked") is True
            and provider_status.get("modelUnavailable") is False
            and provider_status.get("schemaValid") is True
        )
        return 0 if linked else 1

    report = run_codex_cli_review(
        prompt=CONNECTIVITY_PROMPT,
        schema_path=schema_path,
        output_path=output_path,
        config=config,
        cwd=codex_cwd,
        agent_id="probe_codex_cli_model_review",
        task_type="synthetic_connectivity_probe",
        trace_id="codex-cli-link-probe",
    )
    _dump(report)
    provider_status = report.get("modelProviderStatus", {})
    linked = (
        isinstance(provider_status, dict)
        and provider_status.get("modelInvoked") is True
        and provider_status.get("modelUnavailable") is False
        and provider_status.get("schemaValid") is True
    )
    return 0 if linked else 1


if __name__ == "__main__":
    raise SystemExit(main())
