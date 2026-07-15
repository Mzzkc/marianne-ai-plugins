from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._load import load_script


class ExpertPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script(
            "marianne/skills/marianne-expert/scripts/preflight.py",
            "marianne_expert_preflight",
        )

    def _repo(self, root: Path) -> Path:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
        (root / "tracked.txt").write_text("one\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
        return root

    def test_write_authority_is_explicit_not_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            result = self.module.collect_capabilities(repo, False, False)
            self.assertTrue(result["capabilities"]["current_source_read"])
            self.assertFalse(result["capabilities"]["current_source_write_authorized"])

    def test_dirty_file_has_content_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
            result = self.module.collect_capabilities(repo, True, False)
            dirty = result["source_state"]["dirty"]
            self.assertEqual([entry["path"] for entry in dirty], ["tracked.txt"])
            self.assertRegex(dirty[0]["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(result["capabilities"]["current_source_write_authorized"])

    def test_non_repository_is_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.module.collect_capabilities(Path(temp), False, False)
            self.assertFalse(result["capabilities"]["current_source_read"])
            self.assertIsNone(result["source_state"])


if __name__ == "__main__":
    unittest.main()

