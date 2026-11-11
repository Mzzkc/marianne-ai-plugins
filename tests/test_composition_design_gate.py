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
            {
                "id": "recon",
                "produces": ["recon.json"],
                "depends_on": [],
                "sizing": {
                    "role": "recon",
                    "tier": "small",
                    "effort": None,
                    "tools": ["Read", "Grep", "Glob", "Write"],
                    "reason": "reads the tree and writes one inventory",
                },
            },
            {
                "id": "verify",
                "produces": ["verification.json"],
                "depends_on": ["recon"],
                "sizing": {
                    "role": "rubric review",
                    "tier": "middle",
                    "effort": None,
                    "tools": ["Read", "Write", "Bash"],
                    "reason": "runs the suite and writes a verdict",
                },
            },
            {
                "id": "release",
                "produces": ["release.json"],
                "depends_on": ["verify"],
                "instrument": "cli",
                "sizing": {
                    "role": "deterministic command",
                    "tier": "none",
                    "reason": "hashes the candidate; no model",
                },
            },
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

    def test_empty_substantive_sections_fail(self) -> None:
        for field in ("goal", "authority", "proof_obligations"):
            for empty in (None, {}, [], ""):
                with self.subTest(field=field, empty=empty):
                    data = valid_design()
                    data[field] = empty
                    self.assertTrue(any(field in item for item in self._check(data)))

    def test_cyclic_dependencies_fail(self) -> None:
        for dependency in ("recon", "release"):
            with self.subTest(dependency=dependency):
                data = valid_design()
                data["stages"][0]["depends_on"] = [dependency]
                self.assertTrue(any("cycle" in item for item in self._check(data)))

    def test_malformed_dependency_is_reported_not_crashed(self) -> None:
        data = valid_design()
        data["stages"][1]["depends_on"] = [{"id": "recon"}]
        self.assertTrue(any("depends_on" in item for item in self._check(data)))

    def test_parallel_diamond_is_not_a_cycle(self) -> None:
        data = valid_design()
        data["stages"].insert(
            2,
            {
                "id": "peer",
                "depends_on": ["recon"],
                "sizing": {"role": "adversarial review", "tier": "top", "reason": "second voice"},
            },
        )
        data["stages"][-1]["depends_on"] = ["verify", "peer"]
        self.assertEqual(self._check(data), [])

    def test_nonempty_proof_mapping_remains_supported(self) -> None:
        data = valid_design()
        data["proof_obligations"] = {"verification.json": ["full suite"]}
        self.assertEqual(self._check(data), [])

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

    def test_single_ai_stage_may_omit_sizing(self) -> None:
        data = valid_design()
        data["stages"] = [
            {"id": "recon", "produces": ["recon.json"], "depends_on": []},
            {"id": "verify", "depends_on": ["recon"], "instrument": "cli"},
            {"id": "release", "depends_on": ["verify"], "instrument": "cli"},
        ]
        self.assertEqual(self._check(data), [])

    def test_multiple_ai_stages_require_sizing_on_each(self) -> None:
        data = valid_design()
        del data["stages"][1]["sizing"]
        findings = self._check(data)
        self.assertTrue(any("stages[1].sizing" in item for item in findings))

    def test_deterministic_stage_is_not_an_ai_stage(self) -> None:
        data = valid_design()
        data["stages"][2] = {"id": "release", "depends_on": ["verify"], "deterministic": True}
        self.assertEqual(self._check(data), [])

    def test_sizing_must_name_role_and_tier(self) -> None:
        data = valid_design()
        data["stages"][0]["sizing"] = {"role": "recon"}
        self.assertTrue(any("tier" in item for item in self._check(data)))
        data["stages"][0]["sizing"] = {"tier": "small"}
        self.assertTrue(any("role" in item for item in self._check(data)))

    def test_effort_max_requires_reason(self) -> None:
        for reason in (None, "", "   "):
            with self.subTest(reason=reason):
                data = valid_design()
                data["stages"][1]["sizing"] = {
                    "role": "adversarial review",
                    "tier": "top",
                    "effort": "max",
                    "reason": reason,
                }
                self.assertTrue(any("max" in item for item in self._check(data)))
        data = valid_design()
        data["stages"][1]["sizing"].update(effort="max", reason="hard design call")
        self.assertEqual(self._check(data), [])

    def test_sizing_effort_and_tools_are_validated(self) -> None:
        data = valid_design()
        data["stages"][0]["sizing"]["effort"] = "turbo"
        self.assertTrue(any("effort" in item for item in self._check(data)))
        data = valid_design()
        data["stages"][0]["sizing"]["tools"] = "Read"
        self.assertTrue(any("tools" in item for item in self._check(data)))

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
