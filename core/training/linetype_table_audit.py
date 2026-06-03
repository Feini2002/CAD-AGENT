"""Independent readback audit for the line-type summary table."""

from __future__ import annotations

from typing import Any

from core.runtime.encoding_guard import detect_text_encoding_corruption


CANONICAL_TEXT_TERMS = ("线型", "样线", "用途与测试点")
FILL_TYPES = {"hatch", "solid", "wipeout", "solid_fill"}


def _entity_bbox(entity: dict[str, Any]) -> dict[str, list[float]] | None:
    bbox = entity.get("bbox")
    if isinstance(bbox, dict) and isinstance(bbox.get("min"), list) and isinstance(bbox.get("max"), list):
        return {"min": [float(bbox["min"][0]), float(bbox["min"][1])], "max": [float(bbox["max"][0]), float(bbox["max"][1])]}
    xs: list[float] = []
    ys: list[float] = []
    for key in ("start_point", "end_point", "position", "center"):
        point = entity.get(key)
        if isinstance(point, list) and len(point) >= 2:
            xs.append(float(point[0]))
            ys.append(float(point[1]))
    radius = entity.get("radius")
    center = entity.get("center")
    if isinstance(center, list) and len(center) >= 2 and radius is not None:
        value = float(radius)
        xs.extend([float(center[0]) - value, float(center[0]) + value])
        ys.extend([float(center[1]) - value, float(center[1]) + value])
    if not xs or not ys:
        return None
    return {"min": [min(xs), min(ys)], "max": [max(xs), max(ys)]}


def _bbox_inside(inner: dict[str, list[float]], outer: dict[str, list[float]], *, tolerance: float = 1.0) -> bool:
    return (
        inner["min"][0] >= outer["min"][0] - tolerance
        and inner["max"][0] <= outer["max"][0] + tolerance
        and inner["min"][1] >= outer["min"][1] - tolerance
        and inner["max"][1] <= outer["max"][1] + tolerance
    )


def _snapshot_from_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = report.get("styleVerification", {}).get("rows", [])
    if not isinstance(rows, list):
        return []
    snapshot: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("componentReadbacks"), list):
            snapshot.extend(item for item in row["componentReadbacks"] if isinstance(item, dict))
    return snapshot


def _text_audit(report: dict[str, Any], snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    readback = report.get("visibleTextReadback") if isinstance(report.get("visibleTextReadback"), dict) else {}
    texts = [str(text) for text in readback.get("texts", []) if str(text)]
    if not texts:
        texts = [str(entity.get("text", "")) for entity in snapshot if entity.get("type") == "text" and entity.get("text")]
    encoding = detect_text_encoding_corruption(texts)
    joined = "".join(texts)
    missing_terms = [term for term in CANONICAL_TEXT_TERMS if term not in joined]
    status = "pass" if encoding["status"] == "pass" and not missing_terms else "fail"
    return {
        "status": status,
        "encodingPreflight": encoding,
        "canonicalTerms": list(CANONICAL_TEXT_TERMS),
        "missingCanonicalTerms": missing_terms,
        "textCount": len(texts),
    }


def _no_fill_audit(snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    offenders = []
    for entity in snapshot:
        entity_type = str(entity.get("type", "")).lower()
        if entity_type in FILL_TYPES or entity.get("fill") is True:
            offenders.append({"handle": str(entity.get("handle", "")), "type": entity.get("type", ""), "fill": entity.get("fill")})
    return {"status": "pass" if not offenders else "fail", "fillEntityCount": len(offenders), "offenders": offenders}


def _sample_containment_audit(report: dict[str, Any], snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    by_handle = {str(entity.get("handle")): entity for entity in snapshot if entity.get("handle")}
    failures: list[dict[str, Any]] = []
    missing_handles: list[dict[str, Any]] = []
    for record in report.get("rowHandles", []):
        if not isinstance(record, dict):
            continue
        cell = record.get("sampleCellBbox")
        if not isinstance(cell, dict):
            continue
        for handle in record.get("sampleHandles", []):
            entity = by_handle.get(str(handle))
            if entity is None:
                missing_handles.append({"rowIndex": record.get("rowIndex"), "visibleName": record.get("visibleName"), "handle": str(handle)})
                continue
            bbox = _entity_bbox(entity)
            if bbox is not None and not _bbox_inside(bbox, cell):
                failures.append(
                    {
                        "rowIndex": record.get("rowIndex"),
                        "visibleName": record.get("visibleName"),
                        "handle": str(handle),
                        "bbox": bbox,
                        "cell": cell,
                    }
                )
    status = "pass" if not failures and not missing_handles else "fail"
    return {
        "status": status,
        "sampleOutOfCellCount": len(failures),
        "sampleOutOfCellRows": failures,
        "missingSampleHandleCount": len(missing_handles),
        "missingSampleHandles": missing_handles,
    }


def _adaptive_layout_audit(report: dict[str, Any]) -> dict[str, Any]:
    policy = report.get("layoutPolicy") if isinstance(report.get("layoutPolicy"), dict) else {}
    margin = float(policy.get("sampleCellMargin", 20.0))
    failures: list[dict[str, Any]] = []
    for record in report.get("rowHandles", []):
        if not isinstance(record, dict):
            continue
        row_height = float(record.get("rowHeight") or 0.0)
        cell = record.get("sampleCellBbox")
        if not isinstance(cell, dict):
            failures.append({"rowIndex": record.get("rowIndex"), "reason": "missing sampleCellBbox"})
            continue
        cell_height = float(cell["max"][1]) - float(cell["min"][1])
        if row_height <= 0 or cell_height <= 0 or row_height + 1e-6 < cell_height + margin * 2.0:
            failures.append({"rowIndex": record.get("rowIndex"), "rowHeight": row_height, "cellHeight": cell_height, "margin": margin})
    panels = report.get("panels", []) if isinstance(report.get("panels"), list) else []
    row_count = int(report.get("dryRun", {}).get("row_count", len(report.get("rowHandles", []))))
    return {
        "status": "pass" if not failures and row_count == len(report.get("rowHandles", [])) else "fail",
        "rowCount": row_count,
        "panelCount": len(panels),
        "fixedRowLimitUsed": False,
        "rowHeightFailureCount": len(failures),
        "rowHeightFailures": failures,
    }


def _style_audit(report: dict[str, Any]) -> dict[str, Any]:
    rows = report.get("styleVerification", {}).get("rows", [])
    colors: set[str] = set()
    lineweights: set[str] = set()
    linetypes: set[str] = set()
    by_layer_rows = 0
    mismatch_rows = 0
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        if row.get("mismatch", {}).get("status") != "pass":
            mismatch_rows += 1
        expected = row.get("expectedStyle") if isinstance(row.get("expectedStyle"), dict) else {}
        if expected.get("styleSource") == "by_layer":
            by_layer_rows += 1
        if expected.get("colorName"):
            colors.add(str(expected["colorName"]))
        if expected.get("lineweightMm") is not None:
            lineweights.add(str(expected["lineweightMm"]))
        if expected.get("linetype"):
            linetypes.add(str(expected["linetype"]))
    row_count = len(rows) if isinstance(rows, list) else 0
    required_diversity = min(3, max(1, row_count))
    status = "pass" if mismatch_rows == 0 and len(colors) >= required_diversity and len(lineweights) >= 1 and len(linetypes) >= 1 else "fail"
    return {
        "status": status,
        "styleMismatchRowCount": mismatch_rows,
        "distinctColorCount": len(colors),
        "distinctLineweightCount": len(lineweights),
        "distinctLinetypeCount": len(linetypes),
        "byLayerRowCount": by_layer_rows,
    }


def audit_linetype_table_layout(report: dict[str, Any], *, snapshot: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Audit line-type table evidence from readback data."""

    entities = list(snapshot) if snapshot is not None else _snapshot_from_report(report)
    text_audit = _text_audit(report, entities)
    no_fill_audit = _no_fill_audit(entities)
    sample_audit = _sample_containment_audit(report, entities)
    adaptive_audit = _adaptive_layout_audit(report)
    style_audit = _style_audit(report)
    evidence_boundary = {
        "status": "pass",
        "readbackSource": report.get("styleVerification", {}).get("evidenceSource", "unknown"),
        "plotOutputVerified": False,
        "savedDwg": bool(report.get("plotEvidenceBoundary", {}).get("savedDwg", False)),
        "note": "Audit validates entity/text/layout readback only; it does not prove CTB/STB or printed output.",
    }
    sections = {
        "encodingAudit": text_audit,
        "noFillAudit": no_fill_audit,
        "sampleCellContainmentAudit": sample_audit,
        "adaptiveLayoutAudit": adaptive_audit,
        "styleAudit": style_audit,
        "evidenceBoundary": evidence_boundary,
    }
    return {
        "status": "pass" if all(section.get("status") == "pass" for section in sections.values()) else "fail",
        **sections,
    }
