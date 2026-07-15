from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from tests._load import load_script


def valid_design() -> dict[str, object]:
    return {
        "goal": {"statement": "Ship a verified change", "completion": ["full suite passes"]},
        "authority": {"project_root": "/tmp/project", "source_write": False},
        "forces": [{"name": "Exponential Defect Cost", "evidence": "Late failure is costly"}],
        "stages": [
            {"id": "recon", "produces": ["recon.json"], "depends_on": []},
            {"id": "verify", "produces": ["verification.json"], "depends_on": ["recon"]},
            {"id": "release", "produces": ["release.json"], "depends_on": ["verify"]},
        ],
        "context_flow": [{"context": "source", "source": "project_root", "lands_at": ["recon"], "mechanism": "prompt variable"}],
        "injections": [{"path": "/tmp/input.md", "lands_at": ["recon"], "required": True}],
        "proof_obligations": [{"artifact": "verification.json", "checks": ["full suite"]}],
        "repair_loop": {"repair_stage": "recon", "reevaluate_stage": "verify", "max_iterations": 2},
        "release": {"stage": "release", "candidate_hash_required": True, "requires": ["verify"]},
    }


class CompositionDesignGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script(
            "marianne/skills/composing/scripts/check_design.py",
            "composition_design_gate",
        )

    def _check(self, data: dict[str, object]) -> list[str]:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "design.yaml"
            path.write_text(yaml.safe_dump(data), encoding="utf-8")
            return self.module.check_design(path)

    def test_valid_design_passes(self) -> None:
        self.assertEqual(self._check(valid_design()), [])

    def test_missing_authority_fails(self) -> None:
        data = valid_design()
        del data["authority"]
        self.assertTrue(any("authority" in item for item in self._check(data)))

    def test_dangling_dependency_fails(self) -> None:
        data = valid_design()
        data["stages"][1]["depends_on"] = ["missing"]
        self.assertTrue(any("missing" in item for item in self._check(data)))

    def test_release_requires_reevaluation_stage(self) -> None:
        data = valid_design()
        data["release"]["requires"] = ["recon"]
        self.assertTrue(any("reevalu" in item.lower() for item in self._check(data)))

    def test_composing_skill_requires_executable_release_gates(self) -> None:
        skill = (
            Path(__file__).resolve().parents[1]
            / "marianne"
            / "skills"
            / "composing"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("scripts/check_design.py", skill)
        self.assertIn("scripts/check_score_release.py", skill)
        self.assertIn("candidate digest", skill.lower())
        self.assertIn("per_sheet_fallbacks", skill)
        self.assertNotIn("Every assignment needs a fallback chain", skill)

    def test_score_authoring_routes_release_scores_to_composition_gate(self) -> None:
        skill = (
            Path(__file__).resolve().parents[1]
            / "marianne"
            / "skills"
            / "score-authoring"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("check_score_release.py", skill)
        self.assertIn("deterministic", skill.lower())
        self.assertIn("per_sheet_fallbacks", skill)


if __name__ == "__main__":
    unittest.main()
