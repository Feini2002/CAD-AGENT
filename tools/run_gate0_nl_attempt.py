from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cad_agent.adapters.fake_backend import FakeCadBackend
from cad_agent.app.transaction_gateway import CadTransactionGateway
from cad_agent.domain.drawing import DrawingSnapshot
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.scene_compiler import compile_scene
from cad_agent.verification.scene_verifier import verify_scene_execution
from evals.compiler.grader import classify_failure


SCHEMA_VERSION = "cad-agent-gate0-nl-attempt-summary/v1"


class NaturalLanguageGate0Error(ValueError):
    pass


@dataclass(frozen=True)
class Gate0NlCase:
    case_id: str
    prompt: str
    expected_objects: list[str]
    expected_relations: list[list[str]]
    safety: dict[str, Any]


@dataclass(frozen=True)
class Gate0NlCaseResult:
    case_id: str
    status: str
    object_completeness: float
    relation_satisfaction: float
    safety_pass: bool
    failure_category: str | None
    blocking_reasons: list[str]
    derived_objects: list[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "caseId": self.case_id,
            "status": self.status,
            "objectCompleteness": self.object_completeness,
            "relationSatisfaction": self.relation_satisfaction,
            "safetyPass": self.safety_pass,
            "failureCategory": self.failure_category,
            "blockingReasons": self.blocking_reasons,
            "derivedObjects": self.derived_objects,
        }


def scene_from_prompt(*, case_id: str, prompt: str) -> SceneSpec:
    normalized = _normalize_prompt(prompt)
    if not _is_gate0_desktop_scene(normalized):
        raise NaturalLanguageGate0Error("prompt_not_gate0_desktop_scene")

    kinds = _derive_object_kinds(normalized)
    missing = {"desk", "monitor", "keyboard", "mouse", "vase"} - set(kinds)
    if missing:
        raise NaturalLanguageGate0Error("missing_gate0_objects:" + ",".join(sorted(missing)))

    mouse_side = "left" if _mentions_any(normalized, ["左", "left"]) else "right"
    objects = [
        SceneObjectSpec(
            id="desk",
            kind="desk",
            dimensions=Dimensions2D(width=1400, depth=700),
            placement=PlacementIntent(mode="free_region_center"),
        ),
        SceneObjectSpec(id="monitor", kind="monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_center")),
        SceneObjectSpec(
            id="keyboard",
            kind="keyboard",
            placement=PlacementIntent(mode="relative", on="desk", in_front_of="monitor", align_x="monitor", gap=40),
        ),
    ]
    mouse_relation = {"left_of": "keyboard"} if mouse_side == "left" else {"right_of": "keyboard"}
    objects.append(
        SceneObjectSpec(
            id="mouse",
            kind="mouse",
            placement=PlacementIntent(mode="relative", on="desk", align_y="keyboard", gap=40, **mouse_relation),
        )
    )
    objects.append(SceneObjectSpec(id="vase", kind="vase", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_right")))
    return SceneSpec(schema_version="scene-spec/v1", run_id=f"gate0-nl-{case_id}", scene_id=case_id, units="mm", view="plan_2d", objects=objects)


def run_case(case: Gate0NlCase) -> Gate0NlCaseResult:
    try:
        scene = scene_from_prompt(case_id=case.case_id, prompt=case.prompt)
    except NaturalLanguageGate0Error as exc:
        reasons = [str(exc)]
        return Gate0NlCaseResult(
            case_id=case.case_id,
            status="failed",
            object_completeness=0.0,
            relation_satisfaction=0.0,
            safety_pass=False,
            failure_category="semantic_planning_failure",
            blocking_reasons=reasons,
            derived_objects=[],
        )

    snapshot = _snapshot(run_id=scene.run_id)
    compile_result = compile_scene(scene, snapshot)
    if compile_result.patch is None:
        reasons = list(compile_result.blocking_reasons)
        return Gate0NlCaseResult(
            case_id=case.case_id,
            status="failed",
            object_completeness=0.0,
            relation_satisfaction=0.0,
            safety_pass=False,
            failure_category=classify_failure(reasons),
            blocking_reasons=reasons,
            derived_objects=[item.kind for item in scene.objects],
        )

    fake_backend = FakeCadBackend()
    receipt = CadTransactionGateway(backend=fake_backend).execute(compile_result.patch)
    readback = fake_backend.readback(transaction_id=compile_result.patch.transaction_id)
    report = verify_scene_execution(scene=scene, compile_result=compile_result, receipt=receipt, readback=readback, snapshot=snapshot)
    observed_objects = set(readback.semantic_to_handles)
    object_completeness = _ratio(case.expected_objects, observed_objects)
    relation_satisfaction = 1.0 if report.overall_status == "passed" else 0.0
    safety_pass = (
        receipt.saved_current_dwg is case.safety.get("savedCurrentDwg", False)
        and compile_result.patch.target_layer == case.safety.get("targetLayer", "CODEX_PREVIEW")
        and not any(reason.startswith(("wrong_layer", "saved_current_dwg", "nearby_handle_modified")) for reason in report.blocking_reasons)
    )
    passed = report.overall_status == "passed" and object_completeness == 1.0 and relation_satisfaction == 1.0 and safety_pass
    reasons = list(report.blocking_reasons)
    return Gate0NlCaseResult(
        case_id=case.case_id,
        status="passed" if passed else "failed",
        object_completeness=object_completeness,
        relation_satisfaction=relation_satisfaction,
        safety_pass=safety_pass,
        failure_category=None if passed else classify_failure(reasons),
        blocking_reasons=reasons,
        derived_objects=[item.kind for item in scene.objects],
    )


def load_cases(path: str | Path) -> list[Gate0NlCase]:
    cases: list[Gate0NlCase] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if "sceneSpecFixture" in payload:
            raise NaturalLanguageGate0Error(f"scene_spec_fixture_not_allowed:{payload.get('caseId', '<unknown>')}")
        cases.append(
            Gate0NlCase(
                case_id=payload["caseId"],
                prompt=payload["prompt"],
                expected_objects=list(payload.get("expectedObjects", [])),
                expected_relations=[list(item) for item in payload.get("expectedRelations", [])],
                safety=dict(payload.get("safety", {})),
            )
        )
    return cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Gate 0 natural-language attempt cases from raw prompts.")
    parser.add_argument("--cases", default="evals/gate0/cases.jsonl")
    parser.add_argument("--output-root", default=".cad_agent_runs/evals/gate0_nl")
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)

    run_id = args.run_id or datetime.now().strftime("gate0_nl_%Y%m%d_%H%M%S")
    run_dir = Path(args.output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    cases = load_cases(args.cases)
    results = [run_case(case) for case in cases]
    summary = _summary(results)
    _write_json(run_dir / "gate0_nl_attempt_summary.json", summary)
    _write_jsonl(run_dir / "case_results.jsonl", [result.to_json() for result in results])
    _write_jsonl(run_dir / "failures.jsonl", [result.to_json() for result in results if result.status != "passed"])
    (run_dir / "report.md").write_text(_markdown_report(summary, results), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"] == "passed" else 1


def _summary(results: list[Gate0NlCaseResult]) -> dict[str, Any]:
    passed = [result for result in results if result.status == "passed"]
    safety_violations = [result for result in results if not result.safety_pass]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": "passed" if len(passed) == len(results) else "failed",
        "caseCount": len(results),
        "passedCount": len(passed),
        "failedCount": len(results) - len(passed),
        "passRate": round(len(passed) / len(results), 4) if results else 0.0,
        "safetyViolationCount": len(safety_violations),
        "usesSceneSpecFixtures": False,
        "planner": "gate0_desktop_scene_nl_parser/v1",
        "notEvidenceFor": ["general natural-language CAD planning", "production native plugin readiness"],
    }


def _normalize_prompt(prompt: str) -> str:
    return prompt.strip().lower()


def _derive_object_kinds(prompt: str) -> list[str]:
    kinds: list[str] = []
    if _mentions_any(prompt, ["桌", "desk", "table", "workstation"]):
        kinds.append("desk")
    if _mentions_any(prompt, ["显示器", "屏幕", "monitor", "screen"]):
        kinds.append("monitor")
    if _mentions_any(prompt, ["键盘", "键鼠", "keyboard"]):
        kinds.append("keyboard")
    if _mentions_any(prompt, ["鼠标", "键鼠", "mouse"]):
        kinds.append("mouse")
    if _mentions_any(prompt, ["花瓶", "vase"]):
        kinds.append("vase")
    return kinds


def _is_gate0_desktop_scene(prompt: str) -> bool:
    object_count = len(_derive_object_kinds(prompt))
    return object_count >= 4 and _mentions_any(prompt, ["桌", "desk", "table", "workstation", "桌面"])


def _mentions_any(prompt: str, tokens: list[str]) -> bool:
    return any(token in prompt for token in tokens)


def _snapshot(*, run_id: str) -> DrawingSnapshot:
    return DrawingSnapshot(
        schema_version="drawing-snapshot/v1",
        run_id=run_id,
        document_id="gate0-nl-fake",
        units="mm",
        current_space="model",
        active_layer="CODEX_PREVIEW",
        saved=False,
        target_region=(0, 0, 2200, 1400),
        nearby_entities=[],
        snapshot_hash="gate0:nl:snapshot",
    )


def _ratio(expected: list[str], observed: set[str]) -> float:
    if not expected:
        return 1.0
    return len(set(expected) & observed) / len(set(expected))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _markdown_report(summary: dict[str, Any], results: list[Gate0NlCaseResult]) -> str:
    lines = [
        "# Gate 0 Natural-Language Attempt Report",
        "",
        f"- status: `{summary['status']}`",
        f"- cases: `{summary['caseCount']}`",
        f"- passed: `{summary['passedCount']}`",
        f"- failed: `{summary['failedCount']}`",
        f"- safety violations: `{summary['safetyViolationCount']}`",
        f"- uses SceneSpec fixtures: `{summary['usesSceneSpecFixtures']}`",
        "",
        "## Failures",
        "",
    ]
    failures = [result for result in results if result.status != "passed"]
    if not failures:
        lines.append("None.")
    for result in failures:
        lines.append(f"- `{result.case_id}`: `{result.failure_category}` {result.blocking_reasons}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
