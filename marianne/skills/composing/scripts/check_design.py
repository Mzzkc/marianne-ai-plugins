#!/usr/bin/env python3
"""Validate a Marianne composition design gate before score YAML exists."""

from __future__ import annotations

import argparse
from graphlib import CycleError, TopologicalSorter
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
    "compatibility",
    "test_disposition",
    "verification_context",
    "repair_loop",
    "release",
}

EFFORT_LEVELS = {"minimal", "low", "medium", "high", "xhigh", "max"}


def _is_ai_stage(stage: dict) -> bool:
    """A stage is deterministic when it runs the cli instrument or says so."""
    return stage.get("instrument") != "cli" and stage.get("deterministic") is not True


def _check_sizing(index: int, sizing: object) -> list[str]:
    prefix = f"design.stages[{index}].sizing"
    if not isinstance(sizing, dict):
        return [f"{prefix}: mapping with role, tier and reason required"]
    findings = []
    for key in ("role", "tier"):
        value = sizing.get(key)
        if not isinstance(value, str) or not value.strip():
            findings.append(f"{prefix}.{key}: non-empty string required")
    effort = sizing.get("effort")
    if effort is not None and effort not in EFFORT_LEVELS:
        findings.append(
            f"{prefix}.effort: absent or one of {', '.join(sorted(EFFORT_LEVELS))}"
        )
    tools = sizing.get("tools")
    if tools is not None and (
        not isinstance(tools, list) or not all(isinstance(t, str) for t in tools)
    ):
        findings.append(f"{prefix}.tools: absent or a list of tool names")
    reason = sizing.get("reason")
    if effort == "max" and (not isinstance(reason, str) or not reason.strip()):
        findings.append(f"{prefix}.reason: required when effort is max")
    return findings


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
    for key, expected in (("goal", dict), ("authority", dict)):
        if not isinstance(data[key], expected) or not data[key]:
            findings.append(f"design.{key}: non-empty {expected.__name__} required")
    if not isinstance(data["proof_obligations"], (list, dict)) or not data["proof_obligations"]:
        findings.append("design.proof_obligations: non-empty list or mapping required")
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
    ai_stages = [
        index
        for index, stage in enumerate(stages)
        if isinstance(stage, dict) and isinstance(stage.get("id"), str) and _is_ai_stage(stage)
    ]
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict) or not isinstance(stage.get("id"), str):
            continue
        if "sizing" in stage:
            findings.extend(_check_sizing(index, stage["sizing"]))
        elif len(ai_stages) > 1 and index in ai_stages:
            findings.append(
                f"design.stages[{index}].sizing: required when the design has "
                "more than one AI stage (role, tier, effort, tools, reason)"
            )
    known = set(ids)
    graph: dict[str, set[str]] = {stage_id: set() for stage_id in ids}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            continue
        dependencies = stage.get("depends_on", [])
        if not isinstance(dependencies, list):
            findings.append(f"design.stages[{index}].depends_on: list required")
            continue
        for dependency in dependencies:
            if not isinstance(dependency, str) or dependency not in known:
                findings.append(
                    f"design.stages[{index}].depends_on: unknown stage {dependency!r}"
                )
            elif isinstance(stage.get("id"), str) and stage["id"] in graph:
                graph[stage["id"]].add(dependency)
    try:
        tuple(TopologicalSorter(graph).static_order())
    except CycleError:
        findings.append("design.stages: dependency cycle; encode bounded repair as execution control, not a cyclic DAG")
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

    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict):
        findings.append("design.compatibility: mapping required")
    else:
        policy = compatibility.get("policy")
        allowed = {"preserve", "intentional_break", "not_applicable"}
        if policy not in allowed:
            findings.append(
                "design.compatibility.policy: preserve, intentional_break, "
                "or not_applicable required"
            )
        if not compatibility.get("rationale"):
            findings.append("design.compatibility.rationale: required")
        migrations = compatibility.get("migration_targets")
        if not isinstance(migrations, list):
            findings.append("design.compatibility.migration_targets: list required")
        elif policy == "intentional_break" and not migrations:
            findings.append(
                "design.compatibility.migration_targets: intentional break must "
                "name every consumer/example to update"
            )

    disposition = data.get("test_disposition")
    if not isinstance(disposition, dict):
        findings.append("design.test_disposition: mapping required")
    else:
        removed = disposition.get("removed")
        if not isinstance(removed, list):
            findings.append("design.test_disposition.removed: list required")
        else:
            for index, entry in enumerate(removed):
                prefix = f"design.test_disposition.removed[{index}]"
                if not isinstance(entry, dict):
                    findings.append(f"{prefix}: mapping required")
                    continue
                if not entry.get("path"):
                    findings.append(f"{prefix}.path: required")
                if not entry.get("reason"):
                    findings.append(f"{prefix}.reason: required")
                contract = entry.get("contract")
                if contract not in {"retired", "migrated", "redundant"}:
                    findings.append(
                        f"{prefix}.contract: retired, migrated, or redundant required"
                    )
                if contract in {"migrated", "redundant"} and not entry.get(
                    "replacement"
                ):
                    findings.append(
                        f"{prefix}.replacement: required for {contract} contract"
                    )

    verification = data.get("verification_context")
    if not isinstance(verification, dict):
        findings.append("design.verification_context: mapping required")
    else:
        source_binding = verification.get("source_binding")
        binding_markers = ("PYTHONPATH", "editable install", "built wheel", "container")
        if not isinstance(source_binding, str) or not any(
            marker in source_binding for marker in binding_markers
        ):
            findings.append(
                "design.verification_context.source_binding: explicitly bind "
                "the candidate source via PYTHONPATH, an isolated editable "
                "install, a built wheel, or a container"
            )
        import_probe = verification.get("import_probe")
        if not isinstance(import_probe, str) or not any(
            marker in import_probe for marker in ("__file__", "inspect.getfile")
        ):
            findings.append(
                "design.verification_context.import_probe: command must print "
                "the imported candidate module path"
            )
        process_control = verification.get("process_control")
        if not isinstance(process_control, dict):
            findings.append(
                "design.verification_context.process_control: mapping required"
            )
        else:
            if process_control.get("one_suite_at_a_time") is not True:
                findings.append(
                    "design.verification_context.process_control."
                    "one_suite_at_a_time: must be true"
                )
            cleanup = process_control.get("yielded_process_cleanup")
            if not isinstance(cleanup, str) or not cleanup.strip():
                findings.append(
                    "design.verification_context.process_control."
                    "yielded_process_cleanup: required"
                )
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
