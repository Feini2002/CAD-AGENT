from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "cad-agent-vnext-gate0-anti-cheat/v1"
FORBIDDEN_SOURCE_TOKENS = [
    "computer_desk_scene",
    "desk_with_monitor_keyboard_mouse_vase",
    "EXACT_ROUTE",
    "PHRASE_ROUTE",
]


def build_report(root: str | Path = ".") -> dict[str, object]:
    root_path = Path(root)
    public_cases = _load_jsonl(root_path / "evals" / "gate0" / "cases.jsonl")
    hidden_cases = _load_jsonl(root_path / "evals" / "gate0" / "hidden_cases.example.jsonl")
    public_prompts = [str(item.get("prompt", "")) for item in public_cases if item.get("prompt")]
    hidden_prompts = [str(item.get("prompt", "")) for item in hidden_cases if item.get("prompt")]
    case_ids = [str(item.get("caseId", "")) for item in public_cases if item.get("caseId")]

    findings: list[dict[str, str]] = []
    for path in _iter_text_files(root_path / "src" / "cad_agent_vnext", suffixes={".py"}):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root_path).as_posix()
        for prompt in public_prompts:
            if prompt and prompt in text:
                findings.append(_finding("public_prompt_leaked_to_source", relative, prompt))
        for case_id in case_ids:
            if case_id and case_id in text:
                findings.append(_finding("case_id_leaked_to_source", relative, case_id))
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                findings.append(_finding("forbidden_gate0_route_token", relative, token))

    for path in _iter_text_files(root_path / ".agents" / "skills", suffixes={".md"}):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root_path).as_posix()
        for prompt in hidden_prompts:
            if prompt and prompt in text:
                findings.append(_finding("hidden_prompt_leaked_to_skill", relative, prompt))

    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "blocked" if findings else "pass",
        "root": str(root_path.resolve()),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Gate 0 eval anti-cheat rules.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    report = build_report(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["status"] == "blocked" else 0


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _iter_text_files(root: Path, *, suffixes: set[str]) -> Iterable[Path]:
    if not root.exists():
        return []
    return (path for path in root.rglob("*") if path.is_file() and path.suffix in suffixes)


def _finding(code: str, path: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": "blocked", "path": path, "detail": detail}


if __name__ == "__main__":
    raise SystemExit(main())
