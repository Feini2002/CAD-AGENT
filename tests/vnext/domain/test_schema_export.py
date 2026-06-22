from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_export_schema_check_passes_for_generated_files():
    completed = subprocess.run(
        [sys.executable, "scripts/vnext/export_schemas.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "pass"
    assert payload["schemaCount"] >= 6


def test_generated_scene_schema_rejects_additional_properties():
    schema_path = ROOT / "schemas" / "vnext" / "generated" / "scene-spec.schema.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert schema["properties"]["target_layer"]["const"] == "CODEX_PREVIEW"
