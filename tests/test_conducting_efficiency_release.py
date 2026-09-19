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
    "assurance-recursion",
    "capability-denominator",
    "vertical-vs-horizontal",
    "status-andon-wait-pairing",
    "successful-child-failed-wrapper",
    "retained-author-timeout",
    "construction-awaits-qualification",
    "unread-stop-child-loop",
    "prompt-economy-claim",
    "baseline-green-and-handoff",
    "breaker-existing-authority",
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
    assert len(set(ids) - LEGACY_SCENARIOS) == len(EFFICIENCY_SCENARIOS | {'bounded-known-defect', 'still-bound-transfer-delta', 'partial-next-dependency', 'shipped-not-installed', 'integrity-stop-no-substitute', 'rich-life-small-custody', 'repertoire-before-custom', 'native-record-simple-task', 'ordinary-stock-engagement', 'venue-enforcement-gap', 'dual-role-explicit'})


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
    assert "version: 1.7.0" in version
    assert "doctrine: venue-owned-custody-2026-09-19" in version

    manifest = load_script(
        "marianne/skills/conducting/scripts/release_manifest.py",
        "conducting_efficiency_manifest",
    )
    assert manifest.verify_manifest(ROOT) == []


def test_automation_replay_preserves_causal_red_and_green() -> None:
    doctrine = (ROOT / "references/venue-maintenance.md").read_text(
        encoding="utf-8"
    )
    assert "immutable pre-repair subject" in doctrine
    assert "same final test bytes" in " ".join(doctrine.split())
    assert "expected RED" in doctrine
    assert "repaired subject" in doctrine


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
        assert phrase.capitalize() in ledger
    for phrase in ("supported engagement interface", "non-goals", "authority", "relevant context"):
        assert phrase in doctrine


def test_optional_efficiency_observation_measures_custody_not_life() -> None:
    graph = yaml.safe_load((ROOT / "templates/performance-graph.yaml").read_text())
    ledger = graph["efficiency_ledger"]
    assert ledger["enabled"] is False
    assert {"custody_attention_minutes", "hand_authored_wrappers", "repeated_evidence_bytes", "semantic_direction_observation"} <= set(ledger)
    assert "Full lifecycle" in (ROOT / "templates/performance-graph.yaml").read_text()


def test_stock_casting_preserves_rich_lifecycle_without_parallel_custody() -> None:
    doctrine = (ROOT / "references/intervene-and-cast.md").read_text()
    for phrase in ("supported engagement", "full lifecycle", "lifecycle-integration", "without hand-administering", "integrity stop"):
        assert phrase in doctrine


def test_venue_owner_preserves_rerun_freshness_and_liveness_checks() -> None:
    doctrine = (ROOT / "references/venue-maintenance.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "repaired harness and rerun machinery as writers",
        "existing Git/native evidence",
        "replay affected causal proof",
        "process or session termination",
        "interaction state",
        "same evidence basis",
    ):
        assert phrase in doctrine


def test_venue_owner_keeps_expert_and_package_integrity_procedures() -> None:
    doctrine = (ROOT / "references/venue-maintenance.md").read_text()
    for phrase in ("REQUIRED SUB-SKILL", "agent-scores/", "Shipped means", "installed means", "bound means", "running requires", "integrity failure pauses", "Never hand-copy", "install-package", "bind-score-routes"):
        assert phrase in doctrine


def test_every_scenario_has_real_route_and_rubric_categories() -> None:
    for item in _scenario_bundle()["scenarios"]:
        assert (ROOT / item["route"]).is_file()
        assert set(item["categories"]) <= _rubric_categories()
