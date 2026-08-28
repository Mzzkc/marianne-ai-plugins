from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1] / "marianne" / "skills" / "conducting"


class ConductingSkillReleaseTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = {
            "SKILL.md",
            "TASK-MAP.md",
            "VERSION",
            "agents/openai.yaml",
            "evals/scenarios.yaml",
            "evals/rubric.md",
            "references/orient-and-shape.md",
            "references/direct-and-monitor.md",
            "references/intervene-and-cast.md",
            "references/complete-and-steward.md",
            "references/marianne-operations.md",
            "templates/vision-libretto-brief.md",
            "templates/performance-graph.yaml",
            "templates/directive-ledger.md",
            "templates/unresolved-work.md",
            "templates/musician-standing.md",
            "templates/completion-record.md",
            "scripts/release_manifest.py",
        }
        self.assertEqual(
            sorted(path for path in required if not (ROOT / path).is_file()),
            [],
        )

    def test_frontmatter_is_trigger_only(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        self.assertIsNotNone(match)
        fields = yaml.safe_load(match.group(1))
        self.assertEqual(set(fields), {"name", "description"})
        self.assertTrue(fields["description"].startswith("Use when "))
        self.assertNotIn("Covers ", fields["description"])
        self.assertNotIn("workflow", fields["description"].lower())

    def test_router_is_compact_and_names_binding_doctrine(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 500)
        for phrase in (
            "The conductor is god",
            "Long term wins",
            "primary conductor",
            "venue libretto",
            "commission",
            "Completion",
            "consensus",
            "behavioral evidence",
        ):
            self.assertIn(phrase.lower(), text.lower())

    def test_router_forbids_substantive_performance_work(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("control artifacts", text)
        self.assertIn("scores, code, specifications", text)
        self.assertNotIn("update compiler code", text)
        self.assertNotIn("compile, do not hand-maintain", text)

    def test_router_rejects_fake_utilization(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("manufacture utilization", text)
        self.assertRegex(text, r"pause or\s+release")

    def test_package_contains_no_volatile_machine_doctrine(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".py"}
        )
        for forbidden in (
            "GLM 5.2",
            "Gemini CLI 0.46.0",
            "UNSUPPORTED_CLIENT",
            "/home/emzi/",
            "generic-fleet-technique-research.yaml",
        ):
            self.assertNotIn(forbidden, combined)

    def test_scenarios_and_yaml_templates_parse(self) -> None:
        for relative in (
            "evals/scenarios.yaml",
            "templates/performance-graph.yaml",
        ):
            self.assertIsInstance(
                yaml.safe_load((ROOT / relative).read_text(encoding="utf-8")),
                dict,
            )

    def test_artifact_contracts_have_required_fields(self) -> None:
        expectations = {
            "templates/vision-libretto-brief.md": (
                "intended shape",
                "non-negotiables",
                "long-term",
            ),
            "templates/directive-ledger.md": (
                "recipient",
                "propagation",
                "proof",
            ),
            "templates/unresolved-work.md": (
                "deferred",
                "evidence",
                "owner",
            ),
            "templates/musician-standing.md": (
                "reliability",
                "scope",
                "casting",
            ),
            "templates/completion-record.md": (
                "council",
                "dissent",
                "side effects",
            ),
        }
        for relative, phrases in expectations.items():
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            for phrase in phrases:
                self.assertIn(phrase, text, relative)

    def test_task_map_routes_one_hop(self) -> None:
        text = (ROOT / "TASK-MAP.md").read_text(encoding="utf-8")
        for reference in (
            "references/orient-and-shape.md",
            "references/direct-and-monitor.md",
            "references/intervene-and-cast.md",
            "references/complete-and-steward.md",
            "references/marianne-operations.md",
        ):
            self.assertIn(reference, text)

    def test_version_records_composer_doctrine(self) -> None:
        text = (ROOT / "VERSION").read_text(encoding="utf-8")
        self.assertIn("version: 1.2.0", text)
        self.assertIn("doctrine: truthful-convergence-2026-08-28", text)


if __name__ == "__main__":
    unittest.main()
