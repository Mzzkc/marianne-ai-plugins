from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


EXPERT_ROOT = (
    Path(__file__).resolve().parents[1] / "marianne" / "skills" / "marianne-expert"
)


class MarianneExpertPackageTests(unittest.TestCase):
    def test_required_runtime_files_exist(self) -> None:
        required = {
            "SKILL.md",
            "BOOTSTRAP.md",
            "TASK-MAP.md",
            "VERSION",
            "evidence/claims.jsonl",
            "evidence/implementation-status.json",
            "playbooks/develop.md",
            "scripts/preflight.py",
            "scripts/release_manifest.py",
            "agents/openai.yaml",
        }
        missing = sorted(path for path in required if not (EXPERT_ROOT / path).is_file())
        self.assertEqual(missing, [])

    def test_router_uses_capability_vector_and_explicit_authority(self) -> None:
        text = (EXPERT_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("capability", text.lower())
        self.assertIn("authorization", text.lower())
        self.assertNotRegex(text, r"capability level:.*advise.*adapter.*source")
        self.assertLessEqual(len(text.split()), 250)

    def test_frontmatter_has_only_name_and_description(self) -> None:
        text = (EXPERT_ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        self.assertIsNotNone(match)
        keys = {
            line.split(":", 1)[0]
            for line in match.group(1).splitlines()
            if ":" in line
        }
        self.assertEqual(keys, {"name", "description"})

    def test_runtime_instructions_do_not_embed_moved_workspace_paths(self) -> None:
        offenders: list[str] = []
        for path in EXPERT_ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".yaml", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "/workspaces/marianne-expertise-" in text:
                offenders.append(str(path.relative_to(EXPERT_ROOT)))
        self.assertEqual(offenders, [])

    def test_release_metadata_records_completed_acting_acceptance(self) -> None:
        release = (EXPERT_ROOT / "RELEASE.md").read_text(encoding="utf-8")
        manifest = (EXPERT_ROOT / "MANIFEST.md").read_text(encoding="utf-8")
        version = (EXPERT_ROOT / "VERSION").read_text(encoding="utf-8")
        self.assertIn("1.1.0", release)
        self.assertIn("RELEASED", release)
        self.assertIn("final-score", release)
        self.assertIn("10739 passed", release)
        self.assertIn("status: released", version)
        self.assertIn("verdict: RELEASED", version)
        self.assertIn("capability vector", release.lower())
        self.assertNotIn("This package is self-regenerating", release)
        self.assertIn("scripts/preflight.py", manifest)
        self.assertIn("scripts/release_manifest.py", manifest)

    def test_development_playbook_requires_explicit_contract_disposition(self) -> None:
        text = (EXPERT_ROOT / "playbooks" / "develop.md").read_text(encoding="utf-8")
        self.assertIn("compatibility authority", text.lower())
        self.assertIn("retired", text.lower())
        self.assertIn("migrated", text.lower())
        self.assertIn("replacement", text.lower())
        self.assertIn("capability", text.lower())

    def test_development_playbook_binds_verification_to_candidate_source(self) -> None:
        router = (EXPERT_ROOT / "SKILL.md").read_text(encoding="utf-8")
        playbook = (EXPERT_ROOT / "playbooks" / "develop.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("import provenance", router.lower())
        self.assertIn("candidate source", playbook.lower())
        self.assertIn("__file__", playbook)
        self.assertIn("one full suite", playbook.lower())
        self.assertIn("terminate", playbook.lower())
        self.assertIn("reap", playbook.lower())

    def test_acting_guidance_does_not_promote_pinned_backend_snapshot(self) -> None:
        acting_paths = [
            EXPERT_ROOT / "BOOTSTRAP.md",
            EXPERT_ROOT / "playbooks" / "architecture.md",
            EXPERT_ROOT / "playbooks" / "compose.md",
            EXPERT_ROOT / "playbooks" / "debug.md",
            EXPERT_ROOT / "playbooks" / "develop.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in acting_paths)
        self.assertNotIn("Doctrine Exception", combined)
        self.assertNotIn("instrument: recursive_light", combined)
        self.assertNotIn(
            "specialized native clients are Anthropic and Ollama only",
            combined,
        )
        for path in acting_paths:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("current source", text, str(path))
        bootstrap = acting_paths[0].read_text(encoding="utf-8")
        self.assertIn("Pinned backend claims are historical", bootstrap)

    def test_instrument_catalog_matches_clean_provider_boundary(self) -> None:
        catalog_root = EXPERT_ROOT.parents[1] / "docs" / "ref"
        catalog = yaml.safe_load(
            (catalog_root / "instrument-catalog.yaml").read_text(encoding="utf-8")
        )
        instruments = catalog["instruments"]
        self.assertNotIn("anthropic_api", instruments)
        self.assertNotIn("recursive_light", instruments)
        self.assertEqual(
            instruments["ollama"]["capabilities"],
            ["local", "offline", "no_rate_limit", "structured_output"],
        )
        self.assertEqual(instruments["claude-code"]["fallback_instruments"], ["codex-cli"])
        for musician in catalog["musicians"].values():
            self.assertNotIn("anthropic_api", musician.get("available_via", []))
        markdown = (catalog_root / "instrument-catalog.md").read_text(encoding="utf-8")
        self.assertNotIn("`anthropic_api`", markdown)
        self.assertNotIn("`recursive_light`", markdown)


if __name__ == "__main__":
    unittest.main()
