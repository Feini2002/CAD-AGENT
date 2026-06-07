"""Readonly audit for model trace and live-provider claims."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _finding(code: str, path: str, message: str, *, severity: str = "blocked", **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "path": path, "message": message, **extra}


def _candidate_claim_files(root: Path, run_roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for run_root in run_roots:
        resolved = run_root if run_root.is_absolute() else root / run_root
        if resolved.is_file() and resolved.suffix.lower() == ".json":
            paths.append(resolved)
        elif resolved.is_dir():
            paths.extend(sorted(resolved.rglob("*.json")))
    return sorted(set(paths))


def _is_model_claim(payload: dict[str, Any]) -> bool:
    return any(
        key in payload
        for key in (
            "modelInvoked",
            "liveProviderPass",
            "modelUnavailable",
            "traceRef",
            "modelProviderStatus",
            "requiresDownstreamConsumption",
        )
    )


def _live_claimed(payload: dict[str, Any]) -> bool:
    provider_status = payload.get("modelProviderStatus", {})
    provider_pass = isinstance(provider_status, dict) and str(provider_status.get("status", "")) in {
        "pass",
        "live_provider_pass",
    }
    return bool(payload.get("liveProviderPass")) or provider_pass


def _trace_summary_path(claim_path: Path, trace_ref: str) -> Path:
    trace_path = Path(trace_ref)
    if trace_path.is_absolute():
        return trace_path
    return claim_path.parent / trace_path


def _trace_sibling(summary_path: Path, name: str) -> Path:
    return summary_path.parent / name


def audit_model_trace_claims(root: Path, run_roots: list[Path]) -> dict[str, Any]:
    """Find model trace reports that overclaim live model participation."""

    findings: list[dict[str, Any]] = []
    scanned = 0
    for path in _candidate_claim_files(root, run_roots):
        payload = _read_json(path)
        if not payload or not _is_model_claim(payload):
            continue
        scanned += 1
        rel = _display_path(path, root)
        live_claim = _live_claimed(payload)
        trace_ref = str(payload.get("traceRef") or "")

        if live_claim and bool(payload.get("modelUnavailable")):
            findings.append(
                _finding(
                    "model_unavailable_claimed_live",
                    rel,
                    "modelUnavailable=true cannot support a live provider pass claim.",
                )
            )
        if live_claim and not trace_ref:
            findings.append(
                _finding(
                    "model_trace_ref_missing",
                    rel,
                    "live model claims require a traceRef.",
                )
            )
            continue
        if not trace_ref:
            continue

        summary_path = _trace_summary_path(path, trace_ref)
        if live_claim and not summary_path.is_file():
            findings.append(
                _finding(
                    "model_trace_summary_missing",
                    rel,
                    "traceRef does not point to an existing trace summary.",
                    traceRef=trace_ref,
                )
            )
            continue

        required_siblings = {
            "command": _trace_sibling(summary_path, "command.json"),
            "normalized": _trace_sibling(summary_path, "normalized_output.json"),
            "manifest": _trace_sibling(summary_path, "trace_manifest.json"),
            "review": _trace_sibling(summary_path, "trace_review.json"),
        }
        missing_required = [
            label
            for label in ("command", "normalized")
            if not required_siblings[label].is_file()
        ]
        if live_claim and missing_required and summary_path.is_file():
            findings.append(
                _finding(
                    "trace_only_live_claim",
                    rel,
                    "trace summary alone cannot support live provider pass.",
                    traceRef=trace_ref,
                    missingRequired=missing_required,
                )
            )
        if live_claim and not required_siblings["command"].is_file():
            findings.append(
                _finding(
                    "model_trace_missing_command",
                    rel,
                    "live provider proof requires command.json alongside trace summary.",
                    traceRef=trace_ref,
                )
            )
        if live_claim and not required_siblings["normalized"].is_file():
            findings.append(
                _finding(
                    "model_trace_missing_normalized_output",
                    rel,
                    "live provider proof requires normalized_output.json alongside trace summary.",
                    traceRef=trace_ref,
                )
            )

        command_payload = _read_json(required_siblings["command"])
        if live_claim and command_payload:
            command_text = json.dumps(command_payload, ensure_ascii=False)
            if "codex.cmd" not in command_text and "codex" not in command_text:
                findings.append(
                    _finding(
                        "model_trace_command_not_codex",
                        rel,
                        "live provider proof command must identify the Codex CLI route.",
                        traceRef=trace_ref,
                    )
                )

        normalized_payload = _read_json(required_siblings["normalized"])
        if live_claim and normalized_payload:
            provider_status = normalized_payload.get("modelProviderStatus", {})
            route = str(provider_status.get("route", "")) if isinstance(provider_status, dict) else ""
            if route and route != "codex_cli_local":
                findings.append(
                    _finding(
                        "model_trace_bad_provider_route",
                        rel,
                        "live provider proof must use route=codex_cli_local.",
                        traceRef=trace_ref,
                        route=route,
                    )
                )
            schema_valid = normalized_payload.get("schemaValid")
            if schema_valid is False:
                findings.append(
                    _finding(
                        "model_trace_schema_invalid",
                        rel,
                        "live provider proof cannot pass with schemaValid=false.",
                        traceRef=trace_ref,
                    )
                )

        if bool(payload.get("requiresDownstreamConsumption")):
            downstream_refs = payload.get("downstreamRefs", [])
            if not isinstance(downstream_refs, list) or not downstream_refs:
                findings.append(
                    _finding(
                        "model_trace_missing_downstream_refs",
                        rel,
                        "model live participation claims must show downstream consumption refs.",
                        traceRef=trace_ref,
                    )
                )

    blocked = [finding for finding in findings if finding.get("severity") == "blocked"]
    return {
        "schemaVersion": "model-trace-claim-audit/v1",
        "status": "blocked" if blocked else "pass",
        "summary": {
            "runRoots": [_display_path(path if path.is_absolute() else root / path, root) for path in run_roots],
            "claimsScanned": scanned,
            "blockedCount": len(blocked),
        },
        "findings": findings,
        "operatorAction": "fix blocked model trace claims before claiming live model participation."
        if blocked
        else "no model trace claim blockers found.",
    }

