"""The skill installer distributes the shipped tree byte-exactly, with evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import unittest
from pathlib import Path

from tests._load import PLUGIN_ROOT, load_script

SCRIPT = PLUGIN_ROOT / "scripts" / "install_skills.py"


def _run(*args: str, roots: list[Path], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, MARIANNE_SKILL_ROOTS=":".join(str(r) for r in roots),
               MARIANNE_SKILL_INSTALL_ALLOW_DIRTY="1")
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, cwd=cwd,
    )


class InstallSkillsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script("scripts/install_skills.py", "install_skills")
        cls.skills = cls.module.shipped_skills()

    def _roots(self, tmp: Path, n: int = 2) -> list[Path]:
        roots = []
        for i in range(n):
            root = tmp / f"harness{i}" / "skills"
            root.mkdir(parents=True)
            roots.append(root)
        return roots

    def test_status_reports_missing_then_install_makes_current(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp)
            roots = self._roots(tmp)
            (roots[0] / "unrelated").mkdir()
            (roots[0] / "unrelated" / "SKILL.md").write_text("mine\n")
            status = _run("status", "--json", roots=roots, cwd=tmp)
            self.assertEqual(status.returncode, 1, status.stderr)
            report = json.loads(status.stdout)
            self.assertFalse(report["all_current"])
            self.assertEqual(sorted(report["roots"][0]["missing"]), self.skills)

            install = _run("install", "--evidence-dir", str(tmp / "ev"), roots=roots, cwd=tmp)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            first, verify = install.stdout.strip().splitlines()[:2]
            self.assertEqual(json.loads(first)["status"], "installed")
            self.assertEqual(json.loads(verify)["status"], "verified")

            # Byte-exact apart from the installation note; the note maps the plugin root.
            for root in roots:
                for skill in self.skills:
                    installed = (root / skill / "SKILL.md").read_bytes()
                    source = (self.module.SKILLS / skill / "SKILL.md").read_bytes()
                    self.assertEqual(self.module.strip_note(installed), source, skill)
                    self.assertIn(str(self.module.PLUGIN_ROOT).encode(), installed)
                # Docs land beside the root, by package layout.
                self.assertTrue((root.parent / "docs" / "ref").is_dir())
            # The unrelated skill in the same root is untouched.
            self.assertEqual((roots[0] / "unrelated" / "SKILL.md").read_text(), "mine\n")

            status = _run("status", "--json", roots=roots, cwd=tmp)
            self.assertEqual(status.returncode, 0, status.stdout)
            self.assertTrue(json.loads(status.stdout)["all_current"])

    def test_install_archives_preimages_and_verify_catches_drift(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp)
            roots = self._roots(tmp, 1)
            stale = roots[0] / "conducting"
            stale.mkdir()
            (stale / "SKILL.md").write_text("old doctrine\n")
            (stale / "leftover.md").write_text("stale extra\n")
            install = _run("install", "--evidence-dir", str(tmp / "ev"), roots=roots, cwd=tmp)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            result = json.loads(install.stdout.strip().splitlines()[0])
            with tarfile.open(result["backup"]) as tf:
                names = tf.getnames()
            self.assertTrue(any(n.endswith("/leftover.md") for n in names), names)
            self.assertFalse((stale / "leftover.md").exists(), "stale extras are removed")

            verify = _run("verify", roots=roots, cwd=tmp)
            self.assertEqual(verify.returncode, 0, verify.stdout)
            (stale / "SKILL.md").write_bytes((stale / "SKILL.md").read_bytes() + b"\ndrift\n")
            verify = _run("verify", roots=roots, cwd=tmp)
            self.assertEqual(verify.returncode, 1)
            self.assertIn("conducting", verify.stdout)

    def test_expert_manifest_verifies_on_the_installed_copy(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp)
            roots = self._roots(tmp, 1)
            install = _run("install", "--evidence-dir", str(tmp / "ev"), roots=roots, cwd=tmp)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            target = roots[0] / "marianne-expert"
            proc = subprocess.run(
                [sys.executable, str(target / "scripts/release_manifest.py"),
                 "verify", str(target)],
                capture_output=True, text=True,
            )
            self.assertNotIn("mismatch", proc.stdout + proc.stderr)

    def test_dry_run_writes_nothing(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp)
            roots = self._roots(tmp, 1)
            proc = _run("install", "--dry-run", "--evidence-dir", str(tmp / "ev"),
                        roots=roots, cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], "planned")
            self.assertEqual(list(roots[0].iterdir()), [])


if __name__ == "__main__":
    unittest.main()
