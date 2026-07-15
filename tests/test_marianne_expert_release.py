from __future__ import annotations

import re
import unittest
from pathlib import Path


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

    def test_release_metadata_is_candidate_honest(self) -> None:
        release = (EXPERT_ROOT / "RELEASE.md").read_text(encoding="utf-8")
        manifest = (EXPERT_ROOT / "MANIFEST.md").read_text(encoding="utf-8")
        self.assertIn("1.1.0", release)
        self.assertIn("PENDING_ACTING_ACCEPTANCE", release)
        self.assertIn("capability vector", release.lower())
        self.assertNotIn("This package is self-regenerating", release)
        self.assertIn("scripts/preflight.py", manifest)
        self.assertIn("scripts/release_manifest.py", manifest)


if __name__ == "__main__":
    unittest.main()
