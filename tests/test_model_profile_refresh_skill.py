from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = (
    Path(__file__).resolve().parents[1]
    / "marianne"
    / "skills"
    / "marianne-model-profile-refresh"
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_skill_package_has_compact_progressive_structure() -> None:
    required = {
        "SKILL.md",
        "TASK-MAP.md",
        "VERSION",
        "MANIFEST.sha256",
        "references/scope.md",
        "references/research.md",
        "references/backup-surfaces.md",
        "references/commissioning.md",
    }
    assert sorted(path for path in required if not (ROOT / path).is_file()) == []
    assert len(read("SKILL.md").split()) <= 500


def test_frontmatter_is_trigger_only_and_covers_user_phrases() -> None:
    match = re.match(r"^---\n(.*?)\n---", read("SKILL.md"), re.DOTALL)
    assert match is not None
    fields = yaml.safe_load(match.group(1))
    assert set(fields) == {"name", "description"}
    assert fields["name"] == "marianne-model-profile-refresh"
    description = fields["description"]
    assert description.startswith("Use when ")
    assert "workflow" not in description.lower()
    for phrase in (
        "update Marianne models",
        "refresh instrument profiles",
        "upgrade musician profiles",
        "audit stale model IDs",
        "run the Marianne model updater",
    ):
        assert phrase.lower() in description.lower()


def test_router_assigns_full_transaction_to_runtime_and_preserves_coverage() -> None:
    router = read("SKILL.md").lower()
    for phrase in (
        "score/scripts/run_refresh.py", "no approval pause", "all providers marianne ships",
        "locally declared providers", "never install", "protected transaction state",
        "compensation", "--resume-workspace", "temporary-technique", "task-map.md",
    ):
        assert phrase in router
    assert "submitting a job is not completion" in router
    assert "without installing it" in router
    assert "every runner exit" not in router


def test_task_map_routes_score_musicians_and_unproved_compensation() -> None:
    task_map = read("TASK-MAP.md").lower()
    for phrase in (
        "research musician", "apply musician", "unproved compensation",
        "score/scripts/run_refresh.py", "--resume-workspace",
        "references/scope.md", "references/research.md",
        "references/backup-surfaces.md", "references/commissioning.md",
    ):
        assert phrase in task_map


def test_progressive_references_hold_the_detailed_contract() -> None:
    scope = read("references/scope.md").lower()
    for classification in (
        "active",
        "generated",
        "pinned",
        "frozen",
        "retired",
        "unknown",
    ):
        assert classification in scope
    assert "search matches" in scope
    assert "explicitly named" in scope

    research = read("references/research.md").lower()
    for phrase in (
        "all providers marianne ships",
        "official model",
        "official client",
        "local evidence",
        "secondary",
        "contradiction",
    ):
        assert phrase in research

    backup = read("references/backup-surfaces.md").lower()
    for client in (
        "marianne",
        "claude code",
        "codex",
        "gemini cli",
        "antigravity",
        "opencode",
        "aider",
        "goose",
        "crush",
        "cline cli",
        "ollama",
    ):
        assert client in backup
    for phrase in (
        "exact bytes",
        "symlink target",
        "prior absence",
        "secret",
        "reverse order",
        "transaction state",
        "recovery-index digest",
        "exact target spellings",
        "0700",
        "0600",
    ):
        assert phrase in backup

    commissioning = read("references/commissioning.md").lower()
    for phrase in (
        "configured",
        "parsed",
        "live-smoked",
        "unauthenticated",
        "unsupported",
        "failed",
        "gemini cli",
        "oauth",
        "rolled_back",
        "unproved compensation",
    ):
        assert phrase in commissioning


def test_public_router_and_references_are_machine_independent() -> None:
    paths = [ROOT / "SKILL.md", ROOT / "TASK-MAP.md", *sorted((ROOT / "references").glob("*.md"))]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "/home/emzi" not in combined
    assert "Projects/WORSKPACES" not in combined
    assert "Projects/SCORES" not in combined


def test_discovery_docs_have_no_fixed_expected_release_or_provider_subset() -> None:
    combined = "\n".join(read(name) for name in (
        "score/request.md", "score/technique/SKILL.md", "references/research.md", "score/runbook.md"))
    assert "gemini-3.8-flash" not in combined
    assert "--provider " not in combined
    assert "schema-v2" in combined
    assert "empty targets array" in combined
    assert "locally" in combined
