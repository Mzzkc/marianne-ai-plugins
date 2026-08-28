from __future__ import annotations

import re
from pathlib import Path

import yaml

from tests._load import load_script


ROOT = Path(__file__).resolve().parents[1] / "marianne" / "skills" / "conducting"

LEGACY_SCENARIOS = {
    "slowest-worker",
    "false-progress",
    "acknowledgement-only",
    "collision",
    "completion-pressure",
    "harmful-short-term-request",
    "compiler-boundary",
    "proportionate-single-score",
    "long-running-multi-lane",
    "mixed-cli-marianne-fleet",
    "paused-job-active-interaction",
    "reviewer-promise-not-executed",
    "mutable-lifecycle-release-input",
    "persistent-agent-context",
    "proof-spiral-convergence",
}

EFFICIENCY_SCENARIOS = {
    "failure-classification-matrix",
    "artifact-latency",
    "rendered-topology-mismatch",
    "automation-rewrites-red",
    "freshness-dimensions",
    "browser-profile-resource-growth",
    "one-off-deterministic-fixture",
    "recurring-domain-steward",
    "redundant-review-oracle",
    "green-without-organic-evidence",
}

EFFICIENCY_CATEGORIES = {
    "closure-mode",
    "failure-classification",
    "artifact-trajectory",
    "routed-context",
    "rendered-topology",
    "automation-custody",
    "persistent-selection",
    "resource-stewardship",
    "freshness-control",
    "epistemic-instrument-fit",
    "review-economy",
    "layered-completion",
}


def _scenario_bundle() -> dict:
    data = yaml.safe_load((ROOT / "evals/scenarios.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _rubric_categories() -> set[str]:
    text = (ROOT / "evals/rubric.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| `([^`]+)` \|", text, flags=re.MULTILINE))


def test_efficiency_scenarios_extend_without_replacing_legacy_suite() -> None:
    scenarios = _scenario_bundle()["scenarios"]
    ids = [item["id"] for item in scenarios]

    assert len(ids) == len(set(ids))
    assert LEGACY_SCENARIOS <= set(ids)
    assert EFFICIENCY_SCENARIOS <= set(ids)
    assert len(set(ids) - LEGACY_SCENARIOS) == len(EFFICIENCY_SCENARIOS)


def test_efficiency_scenarios_route_to_real_references_and_defined_categories() -> None:
    bundle = _scenario_bundle()
    scenarios = [
        item for item in bundle["scenarios"] if item["id"] in EFFICIENCY_SCENARIOS
    ]
    rubric_categories = _rubric_categories()

    assert EFFICIENCY_CATEGORIES <= rubric_categories
    for item in scenarios:
        assert (ROOT / item["route"]).is_file(), item["id"]
        assert set(item["categories"]) <= rubric_categories, item["id"]
        assert len(item["pressures"]) >= 3, item["id"]


def test_efficiency_suite_covers_domains_and_task_sizes() -> None:
    scenarios = [
        item
        for item in _scenario_bundle()["scenarios"]
        if item["id"] in EFFICIENCY_SCENARIOS
    ]

    assert {item["family"] for item in scenarios} == {
        "software-release",
        "research-knowledge",
        "creative-business",
    }
    assert {item["scale"] for item in scenarios} == {
        "small",
        "medium",
        "long-running",
    }


def test_truthful_convergence_release_metadata_and_closed_manifest() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8")
    assert "version: 1.2.0" in version
    assert "doctrine: truthful-convergence-2026-08-28" in version

    manifest = load_script(
        "marianne/skills/conducting/scripts/release_manifest.py",
        "conducting_efficiency_manifest",
    )
    assert manifest.verify_manifest(ROOT) == []


def test_automation_replay_preserves_causal_red_and_green() -> None:
    doctrine = (ROOT / "references/complete-and-steward.md").read_text(
        encoding="utf-8"
    )
    assert "immutable pre-repair subject" in doctrine
    assert "same final test bytes" in doctrine
    assert "expected failure" in doctrine
    assert "repaired candidate" in doctrine


def test_authority_brief_separates_scope_and_write_authority() -> None:
    doctrine = (ROOT / "references/direct-and-monitor.md").read_text(
        encoding="utf-8"
    )
    ledger = (ROOT / "templates/directive-ledger.md").read_text(encoding="utf-8")
    for phrase in (
        "observable outcome and non-goals",
        "writable roots",
        "read-only roots",
    ):
        assert phrase in doctrine
        assert phrase.capitalize() in ledger


def test_efficiency_ledger_records_movement_level_evidence() -> None:
    graph = yaml.safe_load(
        (ROOT / "templates/performance-graph.yaml").read_text(encoding="utf-8")
    )
    movement = graph["efficiency_ledger"]["movements"][0]
    assert set(movement) == {
        "movement",
        "owner",
        "started_at",
        "ended_at",
        "instrument_class",
        "attempts",
        "artifacts_produced",
        "proofs_executed",
        "rework_cause",
        "conductor_intervention",
        "disk_delta_bytes",
        "cost_or_quota_confidence",
        "next_dependency",
    }


def test_persistent_casting_binds_authority_and_resource_custody() -> None:
    doctrine = (ROOT / "references/intervene-and-cast.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "exact recurring subject",
        "authoritative and memory roots",
        "writable and read-only roots",
        "disk, process, context, provider capacity",
        "measure reclamation",
        "recheck surviving",
    ):
        assert phrase in doctrine


def test_topology_admission_keeps_resource_and_completion_gates_visible() -> None:
    doctrine = (ROOT / "references/direct-and-monitor.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "process, context, provider, and workspace custody",
        "cleanup owner and stop condition",
        "survivor recheck",
        "revalidate and rerender after either repair or intentional reshape",
        "fallback for every sheet",
        "measure reclaimed capacity",
        "recheck surviving resources",
        "artifact and custody",
        "live or organic behavior",
        "release or integration",
    ):
        assert phrase in doctrine


def test_rerun_freshness_replays_automation_and_liveness_lanes() -> None:
    doctrine = (ROOT / "references/marianne-operations.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "repaired harness and rerun machinery as writers",
        "recompute custody on the final produced bytes",
        "replay the same causal proof",
        "process or session termination",
        "interaction state",
        "same evidence basis",
    ):
        assert phrase in doctrine


def test_authority_receipts_are_admission_gates() -> None:
    direct = (ROOT / "references/direct-and-monitor.md").read_text(
        encoding="utf-8"
    )
    casting = (ROOT / "references/intervene-and-cast.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "before split, recast, or cancellation becomes active",
        "concrete authoritative roots",
        "exact immutable input identities",
        "generic labels are not evidence",
        "even a conditional transfer",
        "unknown fields are blockers",
        "must enumerate every authority field in its response",
        "do not compress roots and inputs into generic constraints",
        "every consequential directive carries an authority receipt",
        "unchanged — orientation snapshot ref",
        "fields are never omitted",
    ):
        assert phrase in direct.lower()
    for phrase in (
        "casting is not admitted",
        "exact versioned recurring subject",
        "concrete authoritative and memory roots",
        "exact immutable input identities",
        "conceptual root names are not enough",
        "every response proposing persistent casting must render the authority receipt",
        "unknown — lifecycle owner",
    ):
        assert phrase in casting.lower()
