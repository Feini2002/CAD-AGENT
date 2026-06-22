from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path

from cad_agent_vnext import __version__
from cad_agent_vnext.app.run_service import begin_run
from cad_agent_vnext.tools.cad_tools import execute_preview, rollback_run
from cad_agent_vnext.tools.inspect_tools import inspect_run
from cad_agent_vnext.tools.scene_tools import compile_run, validate_scene
from cad_agent_vnext.tools.verify_tools import closeout_run, repair_run, verify_run


def dependency_status(module_name: str) -> dict[str, object]:
    spec = importlib.util.find_spec(module_name)
    return {
        "available": spec is not None,
        "module": module_name,
    }


def build_doctor_report() -> dict[str, object]:
    output_path = Path("output/vnext/runs")
    output_parent = output_path.parent.parent if output_path.parent.name == "vnext" else output_path.parent
    return {
        "schemaVersion": "cad-agent-vnext-doctor/v1",
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "package": {
            "name": "cad-agent-vnext",
            "version": __version__,
        },
        "dependencies": {
            "pydantic": dependency_status("pydantic"),
            "shapely": dependency_status("shapely"),
        },
        "autocadAdapter": {
            "available": importlib.util.find_spec("pythoncom") is not None
            and importlib.util.find_spec("win32com") is not None,
            "checkedWithoutConnecting": True,
        },
        "outputPath": {
            "path": str(output_path),
            "writable": output_parent.exists() and os.access(output_parent, os.W_OK),
        },
        "cad": {
            "connected": False,
            "modified": False,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cad-agent-vnext")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("version", help="Print vNext package version.")
    subparsers.add_parser("doctor", help="Report local vNext environment without touching CAD.")

    begin = subparsers.add_parser("begin-run", help="Create a run workspace and user brief artifact.")
    begin.add_argument("--request", required=True)
    begin.add_argument("--run-id")
    _add_output_root(begin)

    inspect = subparsers.add_parser("inspect", help="Inspect a backend and write drawing_snapshot.json.")
    inspect.add_argument("--run", required=True)
    inspect.add_argument("--backend", choices=["fake", "autocad-existing"], default="fake")
    _add_output_root(inspect)

    validate = subparsers.add_parser("validate-scene", help="Validate scene_spec.json.")
    validate.add_argument("--run", required=True)
    _add_output_root(validate)

    compile_parser = subparsers.add_parser("compile", help="Compile scene_spec.json into cad_patch.json.")
    compile_parser.add_argument("--run", required=True)
    _add_output_root(compile_parser)

    execute = subparsers.add_parser("execute-preview", help="Execute cad_patch.json through a preview backend.")
    execute.add_argument("--run", required=True)
    execute.add_argument("--backend", choices=["fake", "autocad-existing"], default="fake")
    _add_output_root(execute)

    verify = subparsers.add_parser("verify", help="Run deterministic verification.")
    verify.add_argument("--run", required=True)
    _add_output_root(verify)

    repair = subparsers.add_parser("repair", help="Plan a local repair patch from verification_report.json.")
    repair.add_argument("--run", required=True)
    _add_output_root(repair)

    rollback = subparsers.add_parser("rollback", help="Rollback the fake artifact state for this run.")
    rollback.add_argument("--run", required=True)
    _add_output_root(rollback)

    closeout = subparsers.add_parser("closeout", help="Close out a verified run.")
    closeout.add_argument("--run", required=True)
    _add_output_root(closeout)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(f"cad-agent-vnext {__version__}")
        return 0

    if args.command == "doctor":
        print(json.dumps(build_doctor_report(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "begin-run":
        return _print_envelope(begin_run(args.request, output_root=args.output_root, run_id=args.run_id))

    if args.command == "inspect":
        return _print_envelope(inspect_run(run_id=args.run, output_root=args.output_root, backend=args.backend))

    if args.command == "validate-scene":
        return _print_envelope(validate_scene(run_id=args.run, output_root=args.output_root))

    if args.command == "compile":
        return _print_envelope(compile_run(run_id=args.run, output_root=args.output_root))

    if args.command == "execute-preview":
        return _print_envelope(execute_preview(run_id=args.run, output_root=args.output_root, backend=args.backend))

    if args.command == "verify":
        return _print_envelope(verify_run(run_id=args.run, output_root=args.output_root))

    if args.command == "repair":
        return _print_envelope(repair_run(run_id=args.run, output_root=args.output_root))

    if args.command == "rollback":
        return _print_envelope(rollback_run(run_id=args.run, output_root=args.output_root))

    if args.command == "closeout":
        return _print_envelope(closeout_run(run_id=args.run, output_root=args.output_root))

    parser.error(f"unknown command: {args.command}")
    return 2


def _add_output_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-root", default="output/vnext/runs")


def _print_envelope(envelope) -> int:
    print(json.dumps(envelope.model_dump(mode="json"), ensure_ascii=False, sort_keys=True))
    return 0 if envelope.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
