from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from tests._load import load_script


class CompositionScoreGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script(
            "marianne/skills/composing/scripts/check_score_release.py",
            "composition_score_gate",
        )

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        project = root / "project"
        project.mkdir()
        workspace = root / "workspace"
        workspace.mkdir()
        injected = root / "required.md"
        injected.write_text("RELEASE_SENTINEL\n", encoding="utf-8")
        score = root / "score.yaml"
        data = {
            "name": "gate-test",
            "workspace": str(workspace),
            "instrument": "cli",
            "sheet": {
                "size": 1,
                "total_items": 1,
                "per_sheet_fallbacks": {1: []},
                "prelude": [{"file": str(injected), "as": "skill"}],
            },
            "prompt": {
                "template": "printf '%s\\n' RELEASE_SENTINEL > {{ workspace }}/result.md"
            },
            "validations": [
                {"type": "file_exists", "path": "{workspace}/result.md"},
                {
                    "type": "command_succeeds",
                    "command": "grep -q RELEASE_SENTINEL {workspace}/result.md",
                },
            ],
        }
        score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return score, project, injected

    def test_valid_score_passes_and_lock_is_relocatable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, _ = self._fixture(Path(temp))
            self.assertEqual(self.module.check_score(score, project), [])
            lock = self.module.build_lock(score, project)
            self.assertRegex(lock["candidate_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(self.module.verify_lock(score, project, lock), [])

    def test_missing_required_injection_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, injected = self._fixture(Path(temp))
            injected.unlink()
            self.assertTrue(any("injection" in item.lower() for item in self.module.check_score(score, project)))

    def test_empty_required_injection_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, injected = self._fixture(Path(temp))
            injected.write_text("", encoding="utf-8")
            self.assertTrue(any("empty" in item.lower() for item in self.module.check_score(score, project)))

    def test_workspace_must_not_overlap_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, _ = self._fixture(Path(temp))
            data = yaml.safe_load(score.read_text(encoding="utf-8"))
            data["workspace"] = str(project)
            score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            self.assertTrue(any("workspace" in item.lower() for item in self.module.check_score(score, project)))

    def test_deterministic_cli_requires_explicit_empty_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, _ = self._fixture(Path(temp))
            data = yaml.safe_load(score.read_text(encoding="utf-8"))
            del data["sheet"]["per_sheet_fallbacks"]
            score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            self.assertTrue(any("fallback" in item.lower() for item in self.module.check_score(score, project)))

    def test_file_exists_only_is_rejected_as_decorative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, _ = self._fixture(Path(temp))
            data = yaml.safe_load(score.read_text(encoding="utf-8"))
            data["validations"] = [data["validations"][0]]
            score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            self.assertTrue(any("decorative" in item.lower() for item in self.module.check_score(score, project)))

    def test_lock_mismatch_detects_changed_injection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project, injected = self._fixture(Path(temp))
            lock = self.module.build_lock(score, project)
            injected.write_text("changed\n", encoding="utf-8")
            self.assertTrue(any("digest" in item.lower() for item in self.module.verify_lock(score, project, lock)))


if __name__ == "__main__":
    unittest.main()
