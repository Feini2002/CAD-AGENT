#!/usr/bin/env python3
"""Scan a raw standard CAD library batch into reference-only asset metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets import build_raw_reference_intake, write_raw_reference_intake  # noqa: E402


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build conservative reference intake from standard_cad_library_raw.")
    parser.add_argument("--source-slug", required=True, help="Folder under standard_cad_library_raw.")
    parser.add_argument("--description", default="", help="Optional user note, e.g. 'residential sofa plan pack'.")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--object-tags", default="", help="Optional comma-separated tags. Missing tags are inferred.")
    parser.add_argument("--part-tags", default="", help="Optional comma-separated tags. Missing tags are inferred.")
    parser.add_argument("--style-tags", default="", help="Optional comma-separated tags. Missing tags are inferred.")
    parser.add_argument(
        "--view-type",
        choices=["plan", "elevation", "perspective", "detail", "unknown"],
        default=None,
    )
    parser.add_argument(
        "--source-type",
        choices=["user_provided", "public_reference", "vendor_catalog", "generated_reference", "self_authored", "synthetic"],
        default="user_provided",
    )
    parser.add_argument(
        "--license-status",
        choices=["allowed", "restricted", "unknown", "internal_only", "owned", "permitted"],
        default="unknown",
    )
    parser.add_argument(
        "--usage-boundary",
        choices=["reference_only", "annotation_allowed", "derived_summary_only", "metadata_only"],
        default="reference_only",
    )
    parser.add_argument(
        "--privacy-boundary",
        choices=["raw", "redacted", "synthetic", "public", "anonymized", "project_confidential"],
        default="raw",
    )
    parser.add_argument("--write", action="store_true", help="Write notes, manifests, and annotations.")
    parser.add_argument("--dry-run", action="store_true", help="Only print JSON. This is the default.")
    args = parser.parse_args()

    intake = build_raw_reference_intake(
        args.source_slug,
        project_root=PROJECT_ROOT,
        description=args.description,
        source_type=args.source_type,
        license_status=args.license_status,
        usage_boundary=args.usage_boundary,
        privacy_boundary=args.privacy_boundary,
        domain=args.domain,
        object_tags=_parse_csv(args.object_tags),
        part_tags=_parse_csv(args.part_tags),
        style_tags=_parse_csv(args.style_tags),
        view_type=args.view_type,
    )
    if args.write and intake.get("status") == "ready":
        intake["written_files"] = write_raw_reference_intake(intake, project_root=PROJECT_ROOT)
    elif args.write:
        intake["write_skipped"] = "no raw files found under original/"

    print(json.dumps(intake, ensure_ascii=False, indent=2))
    return 0 if intake.get("status") == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
