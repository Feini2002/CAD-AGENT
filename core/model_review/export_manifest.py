"""Deterministic export boundary manifest for model bridge calls."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "model-export-manifest/v1"
ROUTE = "codex_cli_local"

_WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\[^\s\"'`<>)]*")
_SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9_-]{12,}|secret\s*[:=]\s*[A-Za-z0-9_-]{12,})",
    re.IGNORECASE,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text_artifact(kind: str, text: str) -> dict[str, Any]:
    data = text.encode("utf-8")
    return {"kind": kind, "path": "", "byteCount": len(data), "sha256": _sha256_bytes(data), "status": "inline"}


def _file_artifact(kind: str, path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        data = resolved.read_bytes()
    except OSError:
        data = b""
    artifact: dict[str, Any] = {
        "kind": kind,
        "path": _display_path(resolved),
        "byteCount": len(data),
        "sha256": _sha256_bytes(data),
        "status": "present" if resolved.is_file() else "missing",
    }
    return artifact


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def _resolve_ref(ref: str | Path) -> Path | None:
    text = str(ref)
    if not text:
        return None
    path = Path(text)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _allowed_paths(schema_path: Path, payload_refs: Iterable[str | Path], image_paths: Iterable[str | Path]) -> set[str]:
    paths = {str(schema_path.resolve()).casefold()}
    for item in [*payload_refs, *image_paths]:
        path = _resolve_ref(item)
        if path is not None:
            paths.add(str(path).casefold())
    return paths


def _local_paths_in_text(text: str) -> list[Path]:
    paths: list[Path] = []
    for match in _WINDOWS_PATH_RE.findall(text):
        cleaned = match.rstrip(".,;:，。；：")
        paths.append(Path(cleaned).resolve())
    return paths


def _forbidden_scan(prompt_text: str) -> dict[str, Any]:
    lowered = prompt_text.casefold()
    return {
        "secretLikeCount": len(_SECRET_RE.findall(prompt_text)),
        "wholeRepoRequested": any(term in lowered for term in ["whole repo", "entire repo", "全仓", "整个仓库"]),
        "wholeOutputRequested": any(term in lowered for term in ["whole output", "all output", "整个 output", "全部 output"]),
        "fullScreenScreenshotRequested": any(
            term in lowered for term in ["full screen screenshot", "capture-screen", "--capture-screen", "整屏截图"]
        ),
    }


def _payload_artifacts(payload_refs: Iterable[str | Path]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for ref in payload_refs:
        path = _resolve_ref(ref)
        if path is not None and path.is_file():
            artifacts.append(_file_artifact("payload_ref", path))
        else:
            text = str(ref)
            artifacts.append({"kind": "payload_ref", "path": text, "byteCount": 0, "sha256": "", "status": "reference_only"})
    return artifacts


def build_model_export_manifest(
    *,
    agent_id: str,
    trace_id: str,
    prompt_text: str,
    schema_path: Path,
    payload_refs: list[str | Path] | None = None,
    image_paths: list[str | Path] | None = None,
    approval_basis: list[str] | None = None,
) -> dict[str, Any]:
    """Build a no-network manifest for the exact payload intended for a model call."""

    payload_refs = payload_refs or []
    image_paths = image_paths or []
    allowed = _allowed_paths(schema_path, payload_refs, image_paths)
    unexpected_paths = [
        path for path in _local_paths_in_text(prompt_text) if str(path.resolve()).casefold() not in allowed
    ]
    forbidden_scan = _forbidden_scan(prompt_text)

    blocked_artifacts: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    for path in unexpected_paths:
        blocked_artifacts.append({"kind": "unauthorized_local_path", "path": _display_path(path)})
    if blocked_artifacts:
        blocking_reasons.append("unauthorized_local_path")
    if forbidden_scan["secretLikeCount"]:
        blocking_reasons.append("secret_like_text")
    if forbidden_scan["wholeRepoRequested"]:
        blocking_reasons.append("whole_repo_requested")
    if forbidden_scan["wholeOutputRequested"]:
        blocking_reasons.append("whole_output_requested")
    if forbidden_scan["fullScreenScreenshotRequested"]:
        blocking_reasons.append("full_screen_screenshot_requested")

    sent_artifacts = [
        _text_artifact("prompt_text", prompt_text),
        _file_artifact("schema_snapshot", schema_path),
        *_payload_artifacts(payload_refs),
    ]
    sent_artifacts.extend(_file_artifact("image", Path(path)) for path in image_paths)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "blocked" if blocking_reasons else "pass",
        "route": ROUTE,
        "agentId": str(agent_id),
        "traceId": str(trace_id),
        "approvalBasis": [str(item) for item in approval_basis or []],
        "sentArtifacts": sent_artifacts,
        "blockedArtifacts": blocked_artifacts,
        "unexpectedLocalFiles": [_display_path(path) for path in unexpected_paths],
        "forbiddenScan": forbidden_scan,
        "blockingReasons": list(dict.fromkeys(blocking_reasons)),
        "evidenceBoundary": [
            "manifest pass only proves export boundary, not model quality or CAD geometry",
            "manifest pass does not prove provider availability or user acceptance",
        ],
    }
