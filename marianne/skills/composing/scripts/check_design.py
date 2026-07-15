#!/usr/bin/env python3
"""Validate a Marianne composition design gate before score YAML exists."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


REQUIRED = {
    "goal",
    "authority",
    "forces",
    "stages",
    "context_flow",
    "injections",
    "proof_obligations",
    "repair_loop",
    "release",
}


def check_design(path: Path) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"design: cannot load: {exc}"]
    if not isinstance(data, dict):
        return ["design: top level must be a mapping"]
    findings = [f"design.{key}: required" for key in sorted(REQUIRED - data.keys())]
    if findings:
        return findings
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        return ["design.stages: non-empty list required"]
    ids: list[str] = []
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict) or not isinstance(stage.get("id"), str):
            findings.append(f"design.stages[{index}].id: string required")
            continue
        ids.append(stage["id"])
    if len(ids) != len(set(ids)):
        findings.append("design.stages: ids must be unique")
    known = set(ids)
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            continue
        dependencies = stage.get("depends_on", [])
        if not isinstance(dependencies, list):
            findings.append(f"design.stages[{index}].depends_on: list required")
            continue
        for dependency in dependencies:
            if dependency not in known:
                findings.append(
                    f"design.stages[{index}].depends_on: unknown stage {dependency!r}"
                )
    repair = data.get("repair_loop")
    release = data.get("release")
    if not isinstance(repair, dict):
        findings.append("design.repair_loop: mapping required")
    if not isinstance(release, dict):
        findings.append("design.release: mapping required")
    if isinstance(repair, dict) and isinstance(release, dict):
        reevaluate = repair.get("reevaluate_stage")
        if reevaluate not in known:
            findings.append("design.repair_loop.reevaluate_stage: known stage required")
        if reevaluate not in release.get("requires", []):
            findings.append("design.release.requires: must include reevaluation stage")
        if release.get("stage") not in known:
            findings.append("design.release.stage: known stage required")
        if not release.get("candidate_hash_required"):
            findings.append("design.release.candidate_hash_required: must be true")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path)
    args = parser.parse_args()
    findings = check_design(args.design)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print("composition design verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
