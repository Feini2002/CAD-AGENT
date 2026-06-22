from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Type

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cad_agent_vnext.domain.brief import UserBrief
from cad_agent_vnext.domain.drawing import DrawingSnapshot
from cad_agent_vnext.domain.patch import CadPatch
from cad_agent_vnext.domain.primitives import Primitive
from cad_agent_vnext.domain.receipt import ExecutionReceipt
from cad_agent_vnext.domain.scene import SceneSpec
from cad_agent_vnext.domain.verification import VerificationReport


SCHEMA_VERSION = "cad-agent-vnext-schema-export/v1"
DEFAULT_OUTPUT_DIR = ROOT / "schemas" / "vnext" / "generated"
MODEL_REGISTRY: dict[str, Type[BaseModel]] = {
    "user-brief": UserBrief,
    "drawing-snapshot": DrawingSnapshot,
    "scene-spec": SceneSpec,
    "primitive": Primitive,
    "cad-patch": CadPatch,
    "execution-receipt": ExecutionReceipt,
    "verification-report": VerificationReport,
}


def schema_payload(model: Type[BaseModel]) -> str:
    schema = model.model_json_schema()
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def schema_path(output_dir: Path, name: str) -> Path:
    return output_dir / f"{name}.schema.json"


def write_schemas(output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, model in MODEL_REGISTRY.items():
        path = schema_path(output_dir, name)
        path.write_text(schema_payload(model), encoding="utf-8")
        written.append(str(path))
    return written


def check_schemas(output_dir: Path) -> tuple[bool, list[str]]:
    stale: list[str] = []
    for name, model in MODEL_REGISTRY.items():
        path = schema_path(output_dir, name)
        expected = schema_payload(model)
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            stale.append(str(path))
    return not stale, stale


def build_report(status: str, output_dir: Path, *, stale: list[str] | None = None) -> dict[str, object]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "outputDir": str(output_dir),
        "schemaCount": len(MODEL_REGISTRY),
        "schemas": [f"{name}.schema.json" for name in MODEL_REGISTRY],
        "stale": stale or [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export vNext Pydantic JSON Schemas.")
    parser.add_argument("--check", action="store_true", help="Check generated schemas are up to date.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Schema output directory.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    if args.check:
        ok, stale = check_schemas(output_dir)
        print(json.dumps(build_report("pass" if ok else "blocked", output_dir, stale=stale), ensure_ascii=False, indent=2))
        return 0 if ok else 1

    write_schemas(output_dir)
    print(json.dumps(build_report("written", output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
