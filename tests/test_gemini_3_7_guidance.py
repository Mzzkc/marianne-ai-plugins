from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1] / "marianne"
CATALOG_PATH = ROOT / "docs" / "ref" / "instrument-catalog.yaml"


def _catalog() -> dict[str, object]:
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_gemini_3_7_catalog_records_exact_official_contract() -> None:
    catalog = _catalog()
    musicians = catalog["musicians"]
    assert isinstance(musicians, dict)
    gemini = musicians["gemini-3.7-flash"]

    assert gemini["provider"] == "google"
    assert gemini["status"] == "stable"
    assert gemini["release_stage"] == "ga"
    assert gemini["released"] == "2026-08-13"
    assert gemini["context_window"] == 1_048_576
    assert gemini["max_output_tokens"] == 65_536
    assert gemini["input_modalities"] == ["text", "image", "video", "audio", "pdf"]
    assert gemini["output_modalities"] == ["text"]
    assert gemini["thinking_levels"] == ["low", "medium", "high"]
    assert "minimal" not in gemini["thinking_levels"]
    assert gemini["capabilities"] == [
        "caching",
        "code_execution",
        "computer_use_preview",
        "file_search",
        "function_calling",
        "google_maps_grounding",
        "search_grounding",
        "structured_output",
        "thinking",
        "url_context",
    ]
    assert gemini["available_via"] == ["gemini-cli", "antigravity"]
    assert gemini["source_urls"] == {
        "model": "https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash",
        "models": "https://ai.google.dev/gemini-api/docs/models",
        "changelog": "https://ai.google.dev/gemini-api/docs/changelog",
    }


def test_gemini_3_7_catalog_keeps_evidence_lanes_and_ratings_honest() -> None:
    catalog = _catalog()
    musicians = catalog["musicians"]
    assert isinstance(musicians, dict)
    gemini = musicians["gemini-3.7-flash"]

    assert gemini["ratings"] == {}
    assert gemini["ratings_status"] == "provisional_pending_independent_evaluation"
    evidence = gemini["evidence_lanes"]
    assert set(evidence) == {
        "catalog",
        "configured",
        "dispatch_compatible",
        "live_verified",
    }
    assert "official Google" in evidence["catalog"]
    assert "does not prove" in evidence["configured"]
    assert "not established" in evidence["dispatch_compatible"]
    assert "not attempted" in evidence["live_verified"]


def test_current_gemini_flash_routes_use_3_7_and_older_entries_are_historical() -> None:
    catalog = _catalog()
    musicians = catalog["musicians"]
    chains = catalog["use_case_chains"]
    assert isinstance(musicians, dict)
    assert isinstance(chains, dict)

    assert "gemini-3.7-flash" in str(chains)
    assert "gemini-3-flash-preview" not in str(chains)
    historical = musicians["gemini-3-flash-preview"]
    assert historical["status"] == "historical"
    assert historical["routing"] == "historical_fallback_only"


def test_human_catalog_changelog_and_composing_guidance_are_synchronized() -> None:
    catalog_md = (ROOT / "docs" / "ref" / "instrument-catalog.md").read_text(
        encoding="utf-8"
    )
    changelog = (
        ROOT / "docs" / "ref" / "CHANGELOG-instrument-catalog.md"
    ).read_text(encoding="utf-8")
    composing = (ROOT / "skills" / "composing" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "`gemini-3.7-flash`" in catalog_md
    assert "1,048,576" in catalog_md
    assert "65,536" in catalog_md
    assert "stable / GA" in catalog_md
    assert "current Gemini view is stale" not in catalog_md
    assert "2026-08-17 — Gemini 3.7 Flash stable catalog refresh" in changelog

    for phrase in (
        "high thinking for load-bearing coding and agentic work",
        "medium thinking as the balanced default",
        "low thinking for cheap, bounded work",
        "never request `minimal`",
        "catalog availability",
        "configured profile availability",
        "dispatch compatibility",
        "live verification",
    ):
        assert phrase in composing
