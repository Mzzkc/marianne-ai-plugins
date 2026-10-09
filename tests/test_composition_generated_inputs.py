"""Behavioral tests for explicitly declared run-generated inputs.

Contract under test (candidate helper extension):

A score whose later sheet consumes a required cadenza file that an earlier
sheet produces during the run is unlockable by the canonical release helper,
because the helper checks every injection path before the run while the native
PromptRenderer resolves required cadenzas at consumer time. The candidate
helper accepts an explicit, score-side declaration
(``<score>.generated-inputs.yaml``) that distinguishes immutable initial
inputs from declared run-generated inputs:

- a declared generated input is exempt from release-time existence/empty
  checks and is intentionally absent from the release lock; its integrity is
  enforced at consumption time by the native required-cadenza resolution and
  its delivery receipt;
- the declaration must resolve, on the consumer sheet, to exactly one
  single-file cadenza injection item (declaration/path mismatch fails);
- the producer sheet must exist, run strictly before the consumer sheet
  (self-production and circular production are impossible by construction),
  and be declared in the consumer's ``sheet.dependencies``;
- duplicate or malformed declarations fail visibly;
- every canonical refusal for undeclared or invalid inputs, the workspace
  policy, and lock-mutation detection are preserved.

A score without a declaration file keeps byte-identical canonical behavior
and lock material.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from tests._load import load_script

CANDIDATE_PLUGINS = Path(__file__).resolve().parents[1]

BODY_RELPATH = "{{ workspace }}/generated/body.md"
BODY_ABSPATH = "/generated/body.md"
DECLARATION = {
    "schema_version": 1,
    "generated_inputs": [
        {
            "consumer_sheet": 2,
            "producer_sheet": 1,
            "path": BODY_RELPATH,
        }
    ],
}


class GeneratedInputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_script(
            "marianne/skills/composing/scripts/check_score_release.py",
            "composition_generated_inputs",
        )

    def setUp(self) -> None:
        self.assertTrue(
            str(Path(self.module.__file__)).startswith(str(CANDIDATE_PLUGINS)),
            f"helper is not candidate-bound: {self.module.__file__}",
        )

    def _fixture(
        self,
        root: Path,
        *,
        with_declaration: bool = True,
        dependencies: dict[int, list[int]] | None = None,
        cadenza_path: str = BODY_RELPATH,
        cadenza_kind: str = "file",
        declaration: dict | None | str = DECLARATION,
        produce_body: bool = False,
    ) -> tuple[Path, Path]:
        project = root / "project"
        project.mkdir()
        workspace = root / "workspace"
        workspace.mkdir()
        immutable = root / "initial.md"
        immutable.write_text("IMMUTABLE_INITIAL\n", encoding="utf-8")
        sheet: dict = {
            "size": 1,
            "total_items": 2,
            "prelude": [{"file": str(immutable), "as": "skill"}],
            "cadenzas": {
                2: [{cadenza_kind: cadenza_path, "as": "context", "required": True}]
            },
        }
        sheet["dependencies"] = {2: [1]} if dependencies is None else dependencies
        data = {
            "name": "generated-inputs-contract",
            "workspace": str(workspace),
            "instrument": "claude-code",
            "sheet": sheet,
            "prompt": {"template": "perform sheet {{ sheet_num }}"},
            "validations": [
                {"type": "file_exists", "path": "{workspace}/done.md"},
                {
                    "type": "command_succeeds",
                    "command": "test -f {workspace}/done.md",
                },
            ],
        }
        score = root / "score.yaml"
        score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        if with_declaration and declaration is not None:
            declaration_file = root / "score.generated-inputs.yaml"
            if isinstance(declaration, str):
                declaration_file.write_text(declaration, encoding="utf-8")
            else:
                declaration_file.write_text(
                    yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
                )
        if produce_body:
            body = workspace / "generated" / "body.md"
            body.parent.mkdir(parents=True, exist_ok=True)
            body.write_text("PRODUCED BODY\n", encoding="utf-8")
        return score, project

    # ------------------------------------------------------------------
    # Producer-before-consumer locking (the corrected mismatch)
    # ------------------------------------------------------------------

    def test_declared_generated_input_locks_before_output_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            self.assertEqual(self.module.check_score(score, project), [])
            lock = self.module.build_lock(score, project)
            self.assertRegex(lock["candidate_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                self.module.verify_lock(score, project, lock),
                [],
            )
            self.assertIn("declaration_sha256", lock)
            self.assertIn("generated_inputs", lock)
            (record,) = lock["generated_inputs"].values()
            self.assertEqual(record["producer_sheet"], 1)
            self.assertEqual(record["consumer_sheet"], 2)

    def test_lock_survives_actual_production_of_declared_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            lock = self.module.build_lock(score, project)
            body = Path(temp) / "workspace" / "generated" / "body.md"
            body.parent.mkdir(parents=True)
            body.write_text("PRODUCED BODY\n", encoding="utf-8")
            self.assertEqual(
                self.module.verify_lock(score, project, lock),
                [],
                "producing a declared generated output must not invalidate the "
                "release lock; its bytes are enforced at consumption time",
            )

    # ------------------------------------------------------------------
    # Preserved canonical refusals
    # ------------------------------------------------------------------

    def test_undeclared_missing_input_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp), with_declaration=False)
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("missing" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_empty_immutable_input_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            (Path(temp) / "initial.md").write_text("", encoding="utf-8")
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("empty" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_score_without_declaration_keeps_canonical_lock_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp), with_declaration=False, produce_body=True
            )
            self.assertEqual(self.module.check_score(score, project), [])
            lock = self.module.build_lock(score, project)
            self.assertNotIn("generated_inputs", lock)
            self.assertNotIn("declaration_sha256", lock)

    # ------------------------------------------------------------------
    # Declaration integrity failures
    # ------------------------------------------------------------------

    def test_declaration_path_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            declaration = {
                "schema_version": 1,
                "generated_inputs": [
                    {
                        "consumer_sheet": 2,
                        "producer_sheet": 1,
                        "path": "{{ workspace }}/elsewhere/other.md",
                    }
                ],
            }
            (Path(temp) / "score.generated-inputs.yaml").write_text(
                yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("mismatch" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_self_production_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [
                        {
                            "consumer_sheet": 2,
                            "producer_sheet": 2,
                            "path": BODY_RELPATH,
                        }
                    ],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("before" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_producer_after_consumer_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                dependencies={2: [1]},
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [
                        {
                            "consumer_sheet": 1,
                            "producer_sheet": 2,
                            "path": BODY_RELPATH,
                        }
                    ],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("before" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_unknown_producer_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [
                        {
                            "consumer_sheet": 2,
                            "producer_sheet": 9,
                            "path": BODY_RELPATH,
                        }
                    ],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("producer" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_missing_dependency_edge_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp), dependencies={})
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("depend" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_directory_injection_cannot_be_declared_generated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                cadenza_path="{{ workspace }}/generated",
                cadenza_kind="directory",
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [
                        {
                            "consumer_sheet": 2,
                            "producer_sheet": 1,
                            "path": "{{ workspace }}/generated",
                        }
                    ],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("directory" in item.lower() or "mismatch" in item.lower()
                    for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_duplicate_declaration_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [DECLARATION["generated_inputs"][0],
                                         DECLARATION["generated_inputs"][0]],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("duplicate" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_malformed_declaration_fails_visibly(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp), declaration="schema_version: 1\nformatted: [oops\n"
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("declaration" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    def test_unknown_declaration_entry_key_fails_visibly(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(
                Path(temp),
                declaration={
                    "schema_version": 1,
                    "generated_inputs": [
                        {
                            "consumer_sheet": 2,
                            "producer_sheet": 1,
                            "path": BODY_RELPATH,
                            "exempt": True,
                        }
                    ],
                },
            )
            findings = self.module.check_score(score, project)
            self.assertTrue(
                any("keys" in item.lower() for item in findings),
                findings,
            )
            with self.assertRaises(ValueError):
                self.module.build_lock(score, project)

    # ------------------------------------------------------------------
    # Lock mutation detection
    # ------------------------------------------------------------------

    def test_declaration_mutation_invalidates_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            lock = self.module.build_lock(score, project)
            declaration_file = Path(temp) / "score.generated-inputs.yaml"
            # Byte-level mutation that stays semantically valid: the "./"
            # segment normalizes to the same resolved path, so the only
            # changed lock input is the declaration file's digest.
            mutated = {
                "schema_version": 1,
                "generated_inputs": [
                    {
                        "consumer_sheet": 2,
                        "producer_sheet": 1,
                        "path": "{{ workspace }}/generated/./body.md",
                    }
                ],
            }
            declaration_file.write_text(
                yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8"
            )
            findings = self.module.verify_lock(score, project, lock)
            self.assertEqual(self.module.check_score(score, project), [])
            self.assertTrue(
                any("digest" in item.lower() for item in findings),
                findings,
            )

    def test_immutable_injection_mutation_invalidates_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            lock = self.module.build_lock(score, project)
            (Path(temp) / "initial.md").write_text("TAMPERED\n", encoding="utf-8")
            findings = self.module.verify_lock(score, project, lock)
            self.assertTrue(
                any("digest" in item.lower() for item in findings),
                findings,
            )

    def test_score_mutation_invalidates_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            score, project = self._fixture(Path(temp))
            lock = self.module.build_lock(score, project)
            data = yaml.safe_load(score.read_text(encoding="utf-8"))
            data["name"] = "mutated"
            score.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            findings = self.module.verify_lock(score, project, lock)
            self.assertTrue(
                any("digest" in item.lower() for item in findings),
                findings,
            )


if __name__ == "__main__":
    unittest.main()
