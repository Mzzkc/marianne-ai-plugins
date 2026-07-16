from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tests._load import load_script


class ConductingManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script(
            "marianne/skills/conducting/scripts/release_manifest.py",
            "conducting_manifest",
        )

    def test_manifest_is_relocatable_and_detects_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first"
            second = Path(temp) / "second"
            first.mkdir()
            (first / "SKILL.md").write_text("skill\n", encoding="utf-8")
            (first / "nested").mkdir()
            (first / "nested" / "data.txt").write_text("data\n", encoding="utf-8")
            self.module.build_manifest(first)
            shutil.copytree(first, second)
            self.assertEqual(self.module.verify_manifest(first), [])
            self.assertEqual(self.module.verify_manifest(second), [])
            (second / "nested" / "data.txt").write_text(
                "changed\n",
                encoding="utf-8",
            )
            findings = self.module.verify_manifest(second)
            self.assertTrue(
                any("nested/data.txt" in finding for finding in findings)
            )

    def test_manifest_detects_unlisted_extra_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("skill\n", encoding="utf-8")
            self.module.build_manifest(root)
            (root / "extra.txt").write_text("surprise\n", encoding="utf-8")
            self.assertTrue(
                any("extra.txt" in item for item in self.module.verify_manifest(root))
            )


if __name__ == "__main__":
    unittest.main()
