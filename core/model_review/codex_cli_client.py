"""Codex CLI-backed model review bridge.

This module intentionally treats Codex CLI as a read-only reviewer. It returns
structured evidence for pipeline gates; callers still need CAD readback and
rule-based verification before accepting any layout or asset claim.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence
from uuid import uuid4

from core.model_review.export_manifest import build_model_export_manifest
from core.model_review.provider_status import PASS_STATUSES, with_model_provider_status
from core.model_review.trace_review import write_trace_review


Runner = Callable[..., subprocess.CompletedProcess[str]]
DEFAULT_CODEX_CLI_MODEL = "gpt-5.5"
DEFAULT_CODEX_CLI_REASONING_EFFORT = "medium"
ENV_MODEL_REVIEW_ENABLED = "CAD_AGENT_MODEL_REVIEW_ENABLED"
ENV_MODEL_REVIEW_MODEL = "CAD_AGENT_MODEL_REVIEW_MODEL"
ENV_MODEL_REVIEW_REASONING_EFFORT = "CAD_AGENT_MODEL_REVIEW_REASONING_EFFORT"
ENV_MODEL_REVIEW_TIMEOUT_SECONDS = "CAD_AGENT_MODEL_REVIEW_TIMEOUT_SECONDS"
ENV_MODEL_REVIEW_EXECUTABLE = "CAD_AGENT_MODEL_REVIEW_EXECUTABLE"
ENV_MODEL_REVIEW_IGNORE_RULES = "CAD_AGENT_MODEL_REVIEW_IGNORE_RULES"
ENV_MODEL_REVIEW_IGNORE_USER_CONFIG = "CAD_AGENT_MODEL_REVIEW_IGNORE_USER_CONFIG"
ENV_MODEL_REVIEW_SKIP_GIT_REPO_CHECK = "CAD_AGENT_MODEL_REVIEW_SKIP_GIT_REPO_CHECK"
TRACE_SCHEMA_VERSION = 1
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_EXPORT_BLOCKED = "context_export_blocked"
CONTEXT_LEAK_WARNING_PATTERNS = [
    "Project doc",
    "AGENTS.md exceeds remaining budget",
    "reading additional input from stdin",
    "plugin remote sync",
]


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on", "enabled"}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class CodexCliReviewConfig:
    enabled: bool = False
    model: str = DEFAULT_CODEX_CLI_MODEL
    reasoning_effort: str = DEFAULT_CODEX_CLI_REASONING_EFFORT
    timeout_seconds: int = 120
    sandbox: str = "read-only"
    executable: str = "codex.cmd"
    ignore_rules: bool = True
    ignore_user_config: bool = False
    skip_git_repo_check: bool = False

    @classmethod
    def from_environment(cls) -> "CodexCliReviewConfig":
        """Build the shared local Codex CLI model-review config."""

        return cls(
            enabled=_env_bool(ENV_MODEL_REVIEW_ENABLED, False),
            model=os.environ.get(ENV_MODEL_REVIEW_MODEL, DEFAULT_CODEX_CLI_MODEL),
            reasoning_effort=os.environ.get(
                ENV_MODEL_REVIEW_REASONING_EFFORT,
                DEFAULT_CODEX_CLI_REASONING_EFFORT,
            ),
            timeout_seconds=_env_int(ENV_MODEL_REVIEW_TIMEOUT_SECONDS, 120),
            executable=os.environ.get(ENV_MODEL_REVIEW_EXECUTABLE, "codex.cmd"),
            ignore_rules=_env_bool(ENV_MODEL_REVIEW_IGNORE_RULES, True),
            ignore_user_config=_env_bool(ENV_MODEL_REVIEW_IGNORE_USER_CONFIG, False),
            skip_git_repo_check=_env_bool(ENV_MODEL_REVIEW_SKIP_GIT_REPO_CHECK, False),
        )


def _resolve_executable(executable: str) -> str | None:
    if Path(executable).is_file():
        return executable
    resolved = shutil.which(executable)
    if resolved:
        return executable if executable.endswith(".cmd") else resolved
    if executable == "codex.cmd":
        return shutil.which("codex") or None
    return None


def _load_json_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "modelInvoked": True, "reason": f"model review output unreadable: {exc}"}
    return value if isinstance(value, dict) else {"status": "unavailable", "modelInvoked": True, "reason": "model review output was not a JSON object"}


def _schema_required_fields(schema_path: Path) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    required = schema.get("required", []) if isinstance(schema, dict) else []
    return [str(item) for item in required if str(item)]


def _check_required_fields(report: dict[str, object], schema_path: Path) -> list[str]:
    return [field for field in _schema_required_fields(schema_path) if field not in report]


def _text_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def _safe_slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value).strip())
    return text.strip("-._") or "model_review"


def _json_default(value: object) -> str:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )


def _model_bridge_cwd(trace_id: str) -> Path:
    root = Path(tempfile.gettempdir()) / "cad-agent-model-bridge" / _safe_slug(trace_id)
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _context_leak_audit(stderr: str, *, strict: bool = True) -> dict[str, Any]:
    warnings = [line.strip() for line in str(stderr or "").splitlines() if any(pattern in line for pattern in CONTEXT_LEAK_WARNING_PATTERNS)]
    unexpected_project_context = any(
        "Project doc" in line or "AGENTS.md exceeds remaining budget" in line for line in warnings
    )
    blocking = bool(strict and unexpected_project_context)
    return {
        "schemaVersion": "model-context-leak-audit/v1",
        "unexpectedProjectContextLoaded": unexpected_project_context,
        "warnings": warnings,
        "blocking": blocking,
    }


def _schema_snapshot(schema_path: Path) -> dict[str, Any]:
    try:
        value = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "reason": f"schema snapshot unreadable: {exc}"}
    return value if isinstance(value, dict) else {"status": "unavailable", "reason": "schema snapshot was not an object"}


def _last_message_snapshot(output_path: Path) -> dict[str, Any]:
    if not output_path.is_file():
        return {"status": "missing", "reason": f"last message file not found: {output_path}"}
    return _load_json_object(output_path)


def _build_gate_decision(report: dict[str, Any], validation: dict[str, Any] | None = None) -> dict[str, Any]:
    provider_status = report.get("modelProviderStatus")
    if not isinstance(provider_status, dict):
        provider_status = {}
    validation_payload = validation if isinstance(validation, dict) else {}
    blocking_reasons: list[str] = []
    report_status = str(report.get("status") or "").casefold()
    if report_status and report_status not in PASS_STATUSES:
        blocking_reasons.append(f"model report status is {report_status}")
    reason = report.get("reason")
    if reason:
        blocking_reasons.append(str(reason))
    for key in ("blockingReasons", "issues"):
        for item in _text_items(report.get(key)):
            text = str(item)
            if text and text not in blocking_reasons:
                blocking_reasons.append(text)
    for issue in _text_items(validation_payload.get("issues")):
        text = str(issue)
        if text and text not in blocking_reasons:
            blocking_reasons.append(text)
    missing = _text_items(validation_payload.get("missingFields"))
    if missing:
        blocking_reasons.append("missing schema fields: " + ", ".join(str(item) for item in missing))
    if provider_status.get("modelUnavailable") is True:
        blocking_reasons.append("model provider unavailable")
    if provider_status.get("schemaValid") is not True:
        blocking_reasons.append("schema validation not passed")
    context_leak_audit = report.get("contextLeakAudit")
    if isinstance(context_leak_audit, dict) and context_leak_audit.get("blocking") is True:
        blocking_reasons.append("context leak audit blocked")
    blocking = bool(provider_status.get("blocking") or blocking_reasons)
    return {
        "schemaVersion": TRACE_SCHEMA_VERSION,
        "status": "blocked" if blocking else "pass",
        "blocking": blocking,
        "blockingReasons": list(dict.fromkeys(blocking_reasons)),
        "modelProviderStatus": provider_status,
        "schemaValidation": validation_payload or {"status": "not_run", "issues": [], "missingFields": []},
        "contextLeakAudit": context_leak_audit if isinstance(context_leak_audit, dict) else {},
        "evidenceBoundary": [
            "model gate decision does not prove CAD geometry",
            "model gate decision does not authorize CAD writes, deletes, saves, or verified capability claims",
        ],
    }


@dataclass
class _TraceWriter:
    trace_id: str
    agent_id: str
    task_type: str
    trace_dir: Path
    created_at: str
    prompt: str
    schema_path: Path
    output_path: Path
    image_paths: list[Path]
    input_summary_refs: list[str]
    cwd: Path
    config: CodexCliReviewConfig

    @classmethod
    def start(
        cls,
        *,
        prompt: str,
        schema_path: Path,
        output_path: Path,
        image_paths: Sequence[Path] | None,
        input_summary_refs: Sequence[str | Path] | None,
        config: CodexCliReviewConfig,
        cwd: Path,
        agent_id: str,
        task_type: str,
        trace_id: str | None,
        trace_dir: Path | None,
    ) -> "_TraceWriter":
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        stable_trace_id = _safe_slug(trace_id or uuid4().hex[:12])
        stable_agent_id = _safe_slug(agent_id)
        stable_task_type = _safe_slug(task_type)
        if trace_dir is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            root = output_path.resolve().parent / "traces" / f"{timestamp}_{stable_agent_id}_{stable_trace_id}"
        else:
            root = Path(trace_dir).resolve()
        root.mkdir(parents=True, exist_ok=True)
        writer = cls(
            trace_id=stable_trace_id,
            agent_id=stable_agent_id,
            task_type=stable_task_type,
            trace_dir=root,
            created_at=created_at,
            prompt=prompt,
            schema_path=schema_path,
            output_path=output_path,
            image_paths=[Path(path) for path in image_paths or []],
            input_summary_refs=[str(item) for item in input_summary_refs or []],
            cwd=cwd,
            config=config,
        )
        (root / "prompt.md").write_text(prompt, encoding="utf-8")
        _write_json(root / "schema.json", _schema_snapshot(schema_path))
        (root / "events.jsonl").write_text("", encoding="utf-8")
        return writer

    def finish(
        self,
        *,
        report: dict[str, Any],
        validation: dict[str, Any] | None,
        command: list[str] | None = None,
        completed: subprocess.CompletedProcess[str] | None = None,
    ) -> dict[str, Any]:
        stdout = completed.stdout if completed is not None and completed.stdout else ""
        stderr = completed.stderr if completed is not None and completed.stderr else ""
        context_audit = report.get("contextLeakAudit")
        if not isinstance(context_audit, dict):
            context_audit = _context_leak_audit(stderr)
            report["contextLeakAudit"] = context_audit
        (self.trace_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
        (self.trace_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
        _write_json(self.trace_dir / "context_leak_audit.json", context_audit)
        command_payload: dict[str, Any] = {
            "schemaVersion": TRACE_SCHEMA_VERSION,
            "status": "built" if command is not None else "not_built",
            "sanitized": True,
            "command": command or [],
            "cwd": str(self.cwd),
            "timeoutSeconds": self.config.timeout_seconds,
            "stdinRef": "prompt.md",
            "eventsStream": {
                "requested": False,
                "status": "reserved_for_codex_exec_json",
                "path": "events.jsonl",
            },
        }
        _write_json(self.trace_dir / "command.json", command_payload)
        _write_json(self.trace_dir / "last_message.json", _last_message_snapshot(self.output_path))
        gate_decision = _build_gate_decision(report, validation)
        _write_json(self.trace_dir / "gate_decision.json", gate_decision)
        report["modelTrace"] = {
            "traceId": self.trace_id,
            "agentId": self.agent_id,
            "taskType": self.task_type,
            "traceDir": str(self.trace_dir),
            "exportManifestPath": str(self.trace_dir / "export_manifest.json"),
            "contextLeakAuditPath": str(self.trace_dir / "context_leak_audit.json"),
            "manifestPath": str(self.trace_dir / "trace_manifest.json"),
            "reviewPath": str(self.trace_dir / "trace_review.json"),
            "summaryPath": str(self.trace_dir / "trace_summary.md"),
        }
        _write_json(self.trace_dir / "normalized_output.json", report)
        manifest = {
            "schemaVersion": TRACE_SCHEMA_VERSION,
            "traceId": self.trace_id,
            "agentId": self.agent_id,
            "taskType": self.task_type,
            "createdAt": self.created_at,
            "traceDir": str(self.trace_dir),
            "provider": "codex_cli",
            "route": "codex_cli_local",
            "modelStrategy": {
                "model": self.config.model,
                "reasoningEffort": self.config.reasoning_effort,
                "sandbox": self.config.sandbox,
                "ignoreRules": self.config.ignore_rules,
                "ignoreUserConfig": self.config.ignore_user_config,
                "skipGitRepoCheck": self.config.skip_git_repo_check,
            },
            "inputs": {
                "schemaPath": str(self.schema_path.resolve()),
                "outputPath": str(self.output_path.resolve()),
                "imagePaths": [str(path.resolve()) for path in self.image_paths],
                "summaryRefs": self.input_summary_refs,
            },
            "files": {
                "prompt": "prompt.md",
                "schemaSnapshot": "schema.json",
                "command": "command.json",
                "stdout": "stdout.txt",
                "stderr": "stderr.txt",
                "events": "events.jsonl",
                "lastMessage": "last_message.json",
                "normalizedOutput": "normalized_output.json",
                "gateDecision": "gate_decision.json",
                "exportManifest": "export_manifest.json",
                "contextLeakAudit": "context_leak_audit.json",
                "traceReview": "trace_review.json",
                "traceSummary": "trace_summary.md",
            },
            "modelProviderStatus": report.get("modelProviderStatus", {}),
            "gateDecision": gate_decision,
        }
        _write_json(self.trace_dir / "trace_manifest.json", manifest)
        trace_review = write_trace_review(self.trace_dir)
        report["modelTrace"]["traceReviewStatus"] = trace_review.get("status")
        _write_json(self.trace_dir / "normalized_output.json", report)
        return report


def run_codex_cli_review(
    *,
    prompt: str,
    schema_path: Path,
    output_path: Path,
    image_paths: Sequence[Path] | None = None,
    input_summary_refs: Sequence[str | Path] | None = None,
    config: CodexCliReviewConfig | None = None,
    runner: Runner = subprocess.run,
    cwd: Path | None = None,
    agent_id: str = "model_review",
    task_type: str = "model_review",
    trace_id: str | None = None,
    trace_dir: Path | None = None,
) -> dict[str, object]:
    """Run a read-only Codex CLI review and load its final JSON message."""

    cfg = config or CodexCliReviewConfig.from_environment()
    stable_trace_id = _safe_slug(trace_id or uuid4().hex[:12])
    run_cwd = _model_bridge_cwd(stable_trace_id)
    trace = _TraceWriter.start(
        prompt=prompt,
        schema_path=schema_path,
        output_path=output_path,
        image_paths=image_paths,
        input_summary_refs=input_summary_refs,
        config=cfg,
        cwd=run_cwd,
        agent_id=agent_id,
        task_type=task_type,
        trace_id=stable_trace_id,
        trace_dir=trace_dir,
    )
    export_manifest = build_model_export_manifest(
        agent_id=agent_id,
        trace_id=trace.trace_id,
        prompt_text=prompt,
        schema_path=schema_path,
        payload_refs=[str(item) for item in input_summary_refs or []],
        image_paths=[str(item) for item in image_paths or []],
        approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#default-allowed-data"],
    )
    _write_json(trace.trace_dir / "export_manifest.json", export_manifest)
    if export_manifest.get("status") == "blocked":
        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": False,
                "reason": CONTEXT_EXPORT_BLOCKED,
                "blockingReasons": list(export_manifest.get("blockingReasons", [])),
                "exportManifest": export_manifest,
            },
            provider="codex_cli",
            route="codex_cli_local",
            reason=CONTEXT_EXPORT_BLOCKED,
        )
        return trace.finish(report=report, validation=None)
    if not cfg.enabled:
        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": False,
                "reason": "codex cli model review disabled",
            },
            provider="codex_cli",
            route="codex_cli_local",
        )
        return trace.finish(report=report, validation=None)

    executable = _resolve_executable(cfg.executable)
    if not executable:
        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": False,
                "reason": f"codex cli executable not found: {cfg.executable}",
            },
            provider="codex_cli",
            route="codex_cli_local",
        )
        return trace.finish(report=report, validation=None)

    schema_arg = schema_path.resolve()
    output_arg = output_path.resolve()
    image_args = [image_path.resolve() for image_path in image_paths or []]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        executable,
        "exec",
        "--model",
        cfg.model,
        "--sandbox",
        cfg.sandbox,
        "--ephemeral",
    ]
    if cfg.reasoning_effort:
        command.extend(["-c", f'model_reasoning_effort="{cfg.reasoning_effort}"'])
    if cfg.ignore_rules:
        command.append("--ignore-rules")
    if cfg.ignore_user_config:
        command.append("--ignore-user-config")
    if cfg.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    command.extend(
        [
            "--output-schema",
            str(schema_arg),
            "--output-last-message",
            str(output_arg),
        ]
    )
    for image_path in image_args:
        command.extend(["--image", str(image_path)])
    command.append("-")

    try:
        completed = runner(
            command,
            input=prompt,
            cwd=run_cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=cfg.timeout_seconds,
            check=False,
        )
    except Exception as exc:
        report = with_model_provider_status(
            {"status": "unavailable", "modelInvoked": False, "reason": f"codex cli review failed to start: {exc}"},
            provider="codex_cli",
            route="codex_cli_local",
        )
        return trace.finish(report=report, validation=None, command=command)

    if completed.returncode != 0:
        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": True,
                "reason": "codex cli review returned non-zero exit",
                "returnCode": completed.returncode,
                "stderr": completed.stderr[-1200:] if completed.stderr else "",
            },
            provider="codex_cli",
            route="codex_cli_local",
        )
        return trace.finish(report=report, validation=None, command=command, completed=completed)

    context_audit = _context_leak_audit(completed.stderr)
    if context_audit.get("blocking") is True:
        report = with_model_provider_status(
            {
                "status": "unavailable",
                "modelInvoked": True,
                "reason": "context_leak_blocked",
                "contextLeakAudit": context_audit,
            },
            provider="codex_cli",
            route="codex_cli_local",
            reason="context_leak_blocked",
        )
        return trace.finish(report=report, validation=None, command=command, completed=completed)

    report = _load_json_object(output_path)
    report["modelInvoked"] = True
    missing = _check_required_fields(report, schema_path)
    if missing:
        validation = {
            "status": "fail",
            "issues": ["codex cli review missing schema fields"],
            "missingFields": missing,
        }
        report = with_model_provider_status(
            {
                **report,
                "status": "fail",
                "reason": "codex cli review missing schema fields",
                "missingFields": missing,
            },
            validation=validation,
            provider="codex_cli",
            route="codex_cli_local",
        )
        return trace.finish(report=report, validation=validation, command=command, completed=completed)
    validation = {"status": "pass", "issues": [], "missingFields": []}
    report = with_model_provider_status(report, validation=validation, provider="codex_cli", route="codex_cli_local")
    return trace.finish(report=report, validation=validation, command=command, completed=completed)
