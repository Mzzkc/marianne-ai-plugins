from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1] / "marianne"
CATALOG_PATH = ROOT / "docs" / "ref" / "instrument-catalog.yaml"


def _catalog() -> dict[str, object]:
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_glm_5_3_catalog_capacity_and_calibration() -> None:
    catalog = _catalog()
    musicians = catalog["musicians"]
    assert isinstance(musicians, dict)
    glm = musicians["glm-5.3"]

    assert glm["context_window"] == 1_000_000
    assert glm["max_output_tokens"] == 131_072
    assert set(glm["available_via"]) >= {
        "claude-code-z-ai-gateway",
        "opencode",
        "z-ai-coding-plan",
    }
    assert set(glm["reasoning_effort"]) == {"high", "max"}
    guidance = " ".join(glm["strengths"] + glm["notes"])
    assert "Fable 5-level" in guidance
    assert "well-bounded" in guidance
    assert "post-training" in guidance
    assert "authorized defensive cybersecurity" in guidance


def test_current_glm_routes_and_security_chain_use_5_3() -> None:
    catalog = _catalog()
    musicians = catalog["musicians"]
    assert isinstance(musicians, dict)
    chains = catalog["use_case_chains"]
    assert isinstance(chains, dict)
    assert "glm-5.2" not in str(chains)
    assert chains["careful_long_running_analysis"]["primary"] == ["glm-5.3"]
    security = chains["authorized_vulnerability_discovery"]
    assert security["primary"] == ["glm-5.3"]
    assert "authorized" in security["description"].lower()
    assert "specialized score" in security["rationale"].lower()

    historical_guidance = " ".join(
        str(musicians[model][field])
        for model in ("glm-5.2", "glm-5.1")
        for field in ("strengths", "notes")
    )
    assert "current frontier GLM" not in historical_guidance
    assert "chains now point to" not in historical_guidance


def test_composing_names_current_glm_but_conducting_stays_provider_neutral() -> None:
    composing = (ROOT / "skills" / "composing" / "SKILL.md").read_text(encoding="utf-8")
    assert "GLM 5.3" in composing
    assert "high or max reasoning" in composing
    assert "specialized vulnerability-discovery score" in composing

    conducting = (
        ROOT / "skills" / "conducting" / "references" / "marianne-operations.md"
    ).read_text(encoding="utf-8")
    assert "GLM 5.3" not in conducting
    for phrase in (
        "authorized task",
        "configured specialist",
        "not a guardrail bypass",
        "reproducible findings",
        "independently validate",
    ):
        assert phrase in conducting
