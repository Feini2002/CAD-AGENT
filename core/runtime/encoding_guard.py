"""UTF-8 runtime and mojibake guards for CAD-facing workflows."""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Mapping, Sequence
from typing import Any, TextIO


REPLACEMENT_CHAR = "\ufffd"
QUESTION_RUN_RE = re.compile(r"\?{2,}")
LATIN1_MOJIBAKE_RE = re.compile(r"(?:Ã.|Â.|â€.|â€™|â€œ|â€|ä¸|äº|å[^\s]?|ç[^\s]?|è[^\s]?)")
GBK_MOJIBAKE_HINTS = (
    "绾垮",
    "鏍峰",
    "璧勪骇",
    "褰撳",
    "浠庣",
    "涓嶆",
    "寮€",
    "鏀惧",
    "鎻掑",
    "璋冪",
)


def configure_utf8_process(stdout: TextIO | None = None, stderr: TextIO | None = None) -> dict[str, Any]:
    """Force predictable UTF-8 stdio/env defaults for script entrypoints."""

    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    configured_streams: list[str] = []
    for name, stream in (("stdout", stdout or sys.stdout), ("stderr", stderr or sys.stderr)):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
            configured_streams.append(name)
    return {
        "status": "pass",
        "pythonUtf8": os.environ.get("PYTHONUTF8", ""),
        "pythonIoEncoding": os.environ.get("PYTHONIOENCODING", ""),
        "configuredStreams": configured_streams,
    }


def _iter_text_values(value: Any, *, path: str) -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        result: list[tuple[str, str]] = []
        for key, item in value.items():
            result.extend(_iter_text_values(item, path=f"{path}.{key}"))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        result = []
        for index, item in enumerate(value):
            result.extend(_iter_text_values(item, path=f"{path}[{index}]"))
        return result
    return []


def detect_text_encoding_corruption(*values: Any) -> dict[str, Any]:
    """Detect text that is already corrupted before reaching CAD."""

    issues: list[dict[str, str]] = []
    checked = 0
    for index, value in enumerate(values):
        for path, text in _iter_text_values(value, path=f"value[{index}]"):
            checked += 1
            if not text:
                continue
            if REPLACEMENT_CHAR in text:
                issues.append({"path": path, "kind": "replacement_character", "text": text})
            if QUESTION_RUN_RE.search(text):
                issues.append({"path": path, "kind": "question_mark_run", "text": text})
            if LATIN1_MOJIBAKE_RE.search(text):
                issues.append({"path": path, "kind": "latin1_mojibake", "text": text})
            for marker in GBK_MOJIBAKE_HINTS:
                if marker in text:
                    issues.append({"path": path, "kind": "gbk_mojibake_hint", "text": text, "marker": marker})
                    break
    return {
        "status": "pass" if not issues else "fail",
        "checkedTextCount": checked,
        "issueCount": len(issues),
        "issues": issues,
        "policy": "fail_before_cad_write_or_asset_contract_write",
    }


def assert_no_text_encoding_corruption(*values: Any) -> dict[str, Any]:
    report = detect_text_encoding_corruption(*values)
    if report["status"] != "pass":
        raise ValueError(f"text encoding preflight failed before CAD write: {report}")
    return report
