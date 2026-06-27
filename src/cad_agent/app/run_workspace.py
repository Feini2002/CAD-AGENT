from __future__ import annotations

import json
import secrets
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_ROOT = Path(".cad_agent_runs")


def new_run_id(now: datetime | None = None) -> str:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return f"run_{timestamp}_{secrets.token_hex(4)}"


@dataclass
class RunWorkspace:
    root: Path
    run_id: str
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    @classmethod
    def create(cls, *, output_root: str | Path = DEFAULT_OUTPUT_ROOT, run_id: str | None = None) -> "RunWorkspace":
        resolved_run_id = run_id or new_run_id()
        _validate_run_id(resolved_run_id)
        root = Path(output_root) / resolved_run_id
        root.mkdir(parents=True, exist_ok=False)
        (root / "screenshots").mkdir()
        (root / "debug").mkdir()
        (root / "events.jsonl").touch()
        return cls(root=root, run_id=resolved_run_id)

    @classmethod
    def open(cls, *, output_root: str | Path = DEFAULT_OUTPUT_ROOT, run_id: str) -> "RunWorkspace":
        _validate_run_id(run_id)
        output_root_path = Path(output_root).resolve()
        root = (Path(output_root) / run_id).resolve()
        if root != output_root_path and output_root_path not in root.parents:
            raise ValueError(f"run id resolves outside output root: {run_id}")
        if not root.is_dir():
            raise FileNotFoundError(f"run workspace not found: {run_id}")
        return cls(root=root, run_id=run_id)

    def artifact_path(self, artifact_ref: str) -> Path:
        if not artifact_ref or Path(artifact_ref).is_absolute():
            raise ValueError("artifact path must be relative to run root")
        candidate = (self.root / artifact_ref).resolve()
        root = self.root.resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"artifact path outside run root: {artifact_ref}")
        return candidate

    def write_json_artifact(self, artifact_ref: str, payload: dict[str, Any]) -> str:
        path = self.artifact_path(artifact_ref)
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        temp_path = path.with_name(f".{path.name}.{secrets.token_hex(4)}.tmp")

        with self._lock:
            temp_path.write_text(encoded, encoding="utf-8")
            temp_path.replace(path)
            self.append_event("artifact_written", artifact_ref=artifact_ref)
        return artifact_ref

    def read_json_artifact(self, artifact_ref: str) -> dict[str, Any]:
        path = self.artifact_path(artifact_ref)
        return json.loads(path.read_text(encoding="utf-8"))

    def append_event(self, event: str, *, artifact_ref: str | None = None, detail: dict[str, Any] | None = None) -> None:
        with self._lock:
            events_path = self.root / "events.jsonl"
            current_count = 0
            if events_path.exists():
                current_count = sum(1 for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip())
            payload: dict[str, Any] = {
                "sequence": current_count + 1,
                "event": event,
            }
            if artifact_ref is not None:
                payload["artifactRef"] = artifact_ref
            if detail:
                payload["detail"] = detail
            with events_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

    def evidence_refs(self) -> list[str]:
        refs: list[str] = []
        events_path = self.root / "events.jsonl"
        if not events_path.exists():
            return refs
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            artifact_ref = event.get("artifactRef")
            if event.get("event") == "artifact_written" and artifact_ref and not artifact_ref.startswith("debug/"):
                if artifact_ref not in refs:
                    refs.append(artifact_ref)
        return refs


def _validate_run_id(run_id: str) -> None:
    if not run_id or Path(run_id).name != run_id or "/" in run_id or "\\" in run_id:
        raise ValueError(f"run id must be a single path segment: {run_id}")
