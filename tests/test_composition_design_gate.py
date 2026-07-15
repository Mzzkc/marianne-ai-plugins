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
        "compatibility": {
            "policy": "not_applicable",
            "rationale": "No public contract changes",
            "migration_targets": [],
        },
        "test_disposition": {"removed": []},
        "verification_context": {
            "source_binding": "PYTHONPATH=$PWD/src uv run --no-sync pytest -q",
            "import_probe": "python -c 'import package; print(package.__file__)'",
            "process_control": {
                "one_suite_at_a_time": True,
                "yielded_process_cleanup": "poll to completion or terminate the scoped process group",
            },
        },
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

    def test_intentional_break_requires_migration_targets(self) -> None:
        data = valid_design()
        data["compatibility"] = {
            "policy": "intentional_break",
            "rationale": "Only the composer uses this surface",
            "migration_targets": [],
        }
        self.assertTrue(any("migration" in item.lower() for item in self._check(data)))

    def test_migrated_test_requires_replacement(self) -> None:
        data = valid_design()
        data["test_disposition"] = {
            "removed": [
                {
                    "path": "tests/test_old_backend.py",
                    "contract": "migrated",
                    "reason": "Provider class removed",
                }
            ]
        }
        self.assertTrue(any("replacement" in item.lower() for item in self._check(data)))

    def test_retired_test_does_not_require_replacement(self) -> None:
        data = valid_design()
        data["test_disposition"] = {
            "removed": [
                {
                    "path": "tests/test_old_alias.py",
                    "contract": "retired",
                    "reason": "The alias is intentionally removed",
                }
            ]
        }
        self.assertEqual(self._check(data), [])

    def test_missing_verification_context_fails(self) -> None:
        data = valid_design()
        del data["verification_context"]
        self.assertTrue(any("verification_context" in item for item in self._check(data)))

    def test_verification_requires_candidate_source_provenance(self) -> None:
        data = valid_design()
        data["verification_context"] = {
            "source_binding": "pytest -q",
            "import_probe": "",
            "process_control": {
                "one_suite_at_a_time": False,
                "yielded_process_cleanup": "",
            },
        }
        findings = self._check(data)
        self.assertTrue(any("source_binding" in item for item in findings))
        self.assertTrue(any("import_probe" in item for item in findings))
        self.assertTrue(any("one_suite_at_a_time" in item for item in findings))
        self.assertTrue(any("yielded_process_cleanup" in item for item in findings))

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
        self.assertIn("compatibility", skill.lower())
        self.assertIn("test disposition", skill.lower())
        self.assertIn("verification_context", skill)
        self.assertIn("import_probe", skill)
        self.assertIn("one_suite_at_a_time", skill)
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
