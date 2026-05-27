"""ActiveDocument snapshot and session guard helpers for real CAD safety."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PREVIEW_LAYER = "CODEX_PREVIEW"
SNAPSHOT_VERSION = "cad_session_guard_v1"


def _stable_fingerprint(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _type_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        entity_type = str(entity.get("type", "unknown"))
        counts[entity_type] = counts.get(entity_type, 0) + 1
    return dict(sorted(counts.items()))


def _layer_counts(entities: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entity in entities:
        layer = str(entity.get("layer", ""))
        counts[layer] = counts.get(layer, 0) + 1
    return dict(sorted(counts.items()))


def blocked_snapshot(*, phase: str, reason: str, preview_layer: str = PREVIEW_LAYER) -> dict[str, Any]:
    return {
        "version": SNAPSHOT_VERSION,
        "phase": phase,
        "status": "blocked",
        "blocked_reason": reason,
        "preview_layer": preview_layer,
        "document": {
            "name": "",
            "full_name": "",
            "fingerprint": "",
        },
        "preview_layer_entity_count": 0,
        "modelspace_summary": {
            "entity_count": 0,
            "type_counts": {},
            "layer_counts": {},
            "fingerprint": "",
        },
        "open_document_count": None,
    }


def _read_document_identity(driver: Any) -> dict[str, str]:
    doc = getattr(driver, "doc", None)
    name = str(getattr(doc, "Name", "") or "")
    full_name = str(getattr(doc, "FullName", "") or "")
    identity = f"name={name}|full_name={full_name}"
    return {
        "name": name,
        "full_name": full_name,
        "fingerprint": _stable_fingerprint(identity) if name or full_name else "",
    }


def _read_open_document_count(driver: Any) -> int | None:
    app = getattr(driver, "app", None)
    if app is None:
        return None
    documents = getattr(app, "Documents", None)
    if documents is None:
        return None
    try:
        return int(documents.Count)
    except Exception:
        return None


def _summarize_modelspace(entities: list[dict[str, Any]]) -> dict[str, Any]:
    type_counts = _type_counts(entities)
    layer_counts = _layer_counts(entities)
    summary_payload = json.dumps(
        {"entity_count": len(entities), "type_counts": type_counts, "layer_counts": layer_counts},
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "entity_count": len(entities),
        "type_counts": type_counts,
        "layer_counts": layer_counts,
        "fingerprint": _stable_fingerprint(summary_payload),
    }


def capture_active_document_snapshot(
    driver: Any,
    *,
    phase: str,
    preview_layer: str = PREVIEW_LAYER,
) -> dict[str, Any]:
    """Capture ActiveDocument identity and modelspace summary for a CAD session phase."""

    document = _read_document_identity(driver)
    if not document["name"] and not document["full_name"]:
        return blocked_snapshot(phase=phase, reason="active_document_unavailable", preview_layer=preview_layer)

    open_document_count = _read_open_document_count(driver)
    if open_document_count is not None and open_document_count < 1:
        return blocked_snapshot(phase=phase, reason="no_open_documents", preview_layer=preview_layer)

    if not hasattr(driver, "snapshot_modelspace"):
        return blocked_snapshot(phase=phase, reason="driver_missing_snapshot_modelspace", preview_layer=preview_layer)

    try:
        all_entities = driver.snapshot_modelspace()
        preview_entities = driver.snapshot_modelspace(layer=preview_layer)
    except Exception as exc:
        snapshot = blocked_snapshot(phase=phase, reason="snapshot_failed", preview_layer=preview_layer)
        snapshot["error"] = str(exc)
        return snapshot

    all_entities = [entity for entity in all_entities if isinstance(entity, dict)]
    preview_entities = [entity for entity in preview_entities if isinstance(entity, dict)]

    return {
        "version": SNAPSHOT_VERSION,
        "phase": phase,
        "status": "captured",
        "blocked_reason": "",
        "preview_layer": preview_layer,
        "document": document,
        "preview_layer_entity_count": len(preview_entities),
        "modelspace_summary": _summarize_modelspace(all_entities),
        "open_document_count": open_document_count,
    }


def compare_active_document_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare two snapshots and return machine-readable consistency checks."""

    checks: list[dict[str, str]] = []
    if before.get("status") == "blocked" or after.get("status") == "blocked":
        checks.append(
            _check(
                "snapshot_captured",
                "fail",
                f"before={before.get('status')} after={after.get('status')} reason={after.get('blocked_reason') or before.get('blocked_reason')}",
            )
        )
        return {"status": "blocked", "checks": checks}

    before_doc = before.get("document", {})
    after_doc = after.get("document", {})
    before_fp = str(before_doc.get("fingerprint", ""))
    after_fp = str(after_doc.get("fingerprint", ""))
    identity_ok = bool(before_fp) and before_fp == after_fp
    checks.append(
        _check(
            "active_document_identity_stable",
            "pass" if identity_ok else "fail",
            f"before={before_doc.get('name', '')} after={after_doc.get('name', '')}",
        )
    )

    before_preview = int(before.get("preview_layer_entity_count", 0))
    after_preview = int(after.get("preview_layer_entity_count", 0))
    preview_delta = after_preview - before_preview
    checks.append(
        _check(
            "preview_layer_entity_delta",
            "pass" if preview_delta >= 0 else "fail",
            f"before={before_preview} after={after_preview} delta={preview_delta}",
        )
    )

    before_ms = str(before.get("modelspace_summary", {}).get("fingerprint", ""))
    after_ms = str(after.get("modelspace_summary", {}).get("fingerprint", ""))
    modelspace_changed = before_ms != after_ms
    checks.append(
        _check(
            "modelspace_summary_changed",
            "pass" if modelspace_changed or preview_delta > 0 else "warn",
            f"before={before_ms} after={after_ms}",
        )
    )

    failed = [check for check in checks if check["status"] == "fail"]
    if failed:
        status = "document_changed" if not identity_ok else "inconsistent"
    else:
        status = "consistent"
    return {"status": status, "checks": checks, "preview_layer_entity_delta": preview_delta}


def build_capability_probe_session_guard(
    driver: Any,
    after_connect: dict[str, Any],
    *,
    after_write_phase: str = "after_write",
) -> dict[str, Any]:
    """Build connect/write phase snapshots for preview-only capability probe runs."""

    return build_session_guard_report(
        before_connect=blocked_snapshot(phase="before_connect", reason="cad_not_connected"),
        after_connect=after_connect,
        after_write=capture_active_document_snapshot(driver, phase=after_write_phase),
    )


def build_session_guard_report(
    *,
    before_connect: dict[str, Any],
    after_connect: dict[str, Any],
    after_write: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a session guard report from connect/write phase snapshots."""

    checks: list[dict[str, str]] = []
    if before_connect.get("status") != "blocked":
        checks.append(_check("before_connect_blocked_expected", "warn", "before_connect should be blocked until CAD connects."))

    if after_connect.get("status") == "blocked":
        checks.append(
            _check(
                "after_connect_snapshot",
                "fail",
                str(after_connect.get("blocked_reason") or "after_connect snapshot blocked"),
            )
        )
        return {
            "version": SNAPSHOT_VERSION,
            "status": "blocked",
            "before_connect": before_connect,
            "after_connect": after_connect,
            "after_write": after_write,
            "comparison": None,
            "checks": checks,
        }

    open_count = after_connect.get("open_document_count")
    if isinstance(open_count, int) and open_count > 1:
        checks.append(
            _check(
                "multi_document_uncertain",
                "fail",
                f"{open_count} open documents; target ActiveDocument is not pinned.",
            )
        )
        return {
            "version": SNAPSHOT_VERSION,
            "status": "blocked",
            "before_connect": before_connect,
            "after_connect": after_connect,
            "after_write": after_write,
            "comparison": None,
            "checks": checks,
        }

    checks.append(_check("after_connect_snapshot", "pass", "ActiveDocument snapshot captured after connect."))
    comparison = None
    if after_write is not None:
        comparison = compare_active_document_snapshots(after_connect, after_write)
        checks.extend(comparison.get("checks", []))

    failed = [check for check in checks if check["status"] == "fail"]
    if failed:
        guard_status = "blocked" if any(check["name"] == "multi_document_uncertain" for check in failed) else "inconsistent"
    elif comparison is not None:
        guard_status = str(comparison.get("status", "consistent"))
    else:
        guard_status = "consistent"

    return {
        "version": SNAPSHOT_VERSION,
        "status": guard_status,
        "before_connect": before_connect,
        "after_connect": after_connect,
        "after_write": after_write,
        "comparison": comparison,
        "checks": checks,
    }


def write_session_guard_report(output_dir: Path | None, report: dict[str, Any]) -> None:
    if output_dir is None:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "active_document_snapshot.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
