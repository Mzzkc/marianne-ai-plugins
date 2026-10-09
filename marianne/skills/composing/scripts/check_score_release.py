#!/usr/bin/env python3
"""Gate a composed Marianne score and lock its load-bearing inputs.

Candidate extension — explicitly declared run-generated inputs
==============================================================

The canonical helper checks every prelude/cadenza injection path before the
run, so a score whose later sheet consumes a required cadenza file produced
by an earlier sheet cannot be release-locked, even though the native
PromptRenderer resolves required cadenzas correctly at consumer time. This
candidate closes that gap without losing any canonical refusal.

A score may declare generated inputs in a declaration file placed next to
the score: ``<score-stem>.generated-inputs.yaml`` (or via ``--generated``)::

    schema_version: 1
    generated_inputs:
      - consumer_sheet: 2
        producer_sheet: 1
        path: "{{ workspace }}/generated/body.md"

Contract enforced for each declared entry:

- The consumer and producer sheets must exist in the score (unknown producer
  or consumer fails).
- ``producer_sheet < consumer_sheet``: strict producer-before-consumer
  order. Self-production and circular production are impossible by
  construction under this rule.
- The consumer sheet must list the producer in ``sheet.dependencies``, so
  the declaration matches the score's actual execution ordering.
- The declared Jinja path must resolve, with the consumer sheet's template
  variables, to exactly one single-file cadenza injection item on that
  consumer sheet. Prelude items and directory injections cannot be declared
  generated (declaration/path mismatch fails otherwise).
- Duplicate declarations of the same consumer path are ambiguous and fail.

A declared generated input is exempt from release-time existence/empty
checks and is intentionally NOT hashed into the release lock: its bytes do
not exist at release time and its integrity is enforced at consumption time
by the native required-cadenza resolution (``FileNotFoundError`` on a missing
required attachment) plus the context-delivery receipt (source/resolved
path, byte count, sha256). The declaration file itself is hashed into the
lock, so any declaration mutation invalidates the lock, as do score and
immutable-input mutations.

Scores without a declaration file behave exactly like the canonical helper,
including byte-identical lock material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jinja2
import yaml

from marianne.core.config.job import JobConfig
from marianne.core.sheet import Sheet, build_sheets

DECLARATION_SUFFIX = ".generated-inputs.yaml"
_GENERATED_ENTRY_KEYS = {"consumer_sheet", "producer_sheet", "path"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _template_vars(sheet: Sheet, total_sheets: int) -> dict[str, Any]:
    values: dict[str, Any] = {
        "workspace": str(sheet.workspace),
        "sheet_num": sheet.num,
        "total_sheets": total_sheets,
        "movement": sheet.movement,
        "stage": sheet.movement,
        "voice": sheet.voice,
        "voice_count": sheet.voice_count,
    }
    values.update(sheet.variables)
    return values


def _resolve_against_workspace(rendered: str, workspace: Path) -> Path:
    path = Path(rendered)
    if not path.is_absolute():
        path = workspace / path
    return path.resolve()


def default_declaration_path(score_path: Path) -> Path:
    """Declaration file location for a score: sibling of the score file."""
    return score_path.with_name(f"{score_path.stem}{DECLARATION_SUFFIX}")


def load_generated_declaration(
    score_path: Path, override: Path | None = None
) -> tuple[Path | None, list[dict[str, Any]], list[str]]:
    """Locate and syntax-check the generated-input declaration, if any.

    Returns ``(declaration_path_or_None, raw_entries, findings)``. When no
    declaration file exists and none was forced, the score keeps canonical
    all-initial-input behavior.
    """
    path = override if override is not None else default_declaration_path(score_path)
    if not path.is_file():
        if override is not None:
            return None, [], [f"generated declaration file not found: {path}"]
        return None, [], []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return path, [], [f"generated declaration unreadable: {path}: {exc}"]
    except yaml.YAMLError as exc:
        return path, [], [f"generated declaration unparseable: {path}: {exc}"]
    findings: list[str] = []
    if not isinstance(data, dict):
        return path, [], [f"generated declaration must be a mapping: {path}"]
    if data.get("schema_version") != 1:
        findings.append(
            f"generated declaration {path}: schema_version must be 1, "
            f"got {data.get('schema_version')!r}"
        )
    entries = data.get("generated_inputs")
    if not isinstance(entries, list):
        findings.append(
            f"generated declaration {path}: 'generated_inputs' must be a list, "
            f"got {type(entries).__name__}"
        )
        entries = []
    cleaned: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(
                f"generated declaration {path} entry {index}: must be a mapping"
            )
            continue
        unknown = sorted(set(entry) - _GENERATED_ENTRY_KEYS)
        missing = sorted(_GENERATED_ENTRY_KEYS - set(entry))
        if unknown or missing:
            findings.append(
                f"generated declaration {path} entry {index}: keys must be exactly "
                f"{sorted(_GENERATED_ENTRY_KEYS)} (unknown: {unknown}, missing: {missing})"
            )
            continue
        consumer = entry["consumer_sheet"]
        producer = entry["producer_sheet"]
        declared = entry["path"]
        bad_int = [
            name
            for name, value in (
                ("consumer_sheet", consumer),
                ("producer_sheet", producer),
            )
            if not isinstance(value, int) or isinstance(value, bool) or value < 1
        ]
        if bad_int:
            findings.append(
                f"generated declaration {path} entry {index}: "
                f"{', '.join(bad_int)} must be a positive integer"
            )
            continue
        if not isinstance(declared, str) or not declared.strip():
            findings.append(
                f"generated declaration {path} entry {index}: "
                "'path' must be a non-empty string"
            )
            continue
        cleaned.append(
            {
                "consumer_sheet": consumer,
                "producer_sheet": producer,
                "path": declared,
            }
        )
    return path, cleaned, findings


def resolve_generated_inputs(
    config: JobConfig,
    entries: list[dict[str, Any]],
    declaration_path: Path | None,
) -> tuple[dict[int, set[Path]], list[dict[str, Any]], list[str]]:
    """Validate declared generated inputs against the parsed score.

    Returns ``(exemptions per consumer sheet, lock records, findings)``.
    See the module docstring for the exact contract. Findings here are
    release-blocking: a malformed, ambiguous, or mismatching declaration
    can never silently relax the canonical missing-input refusals.
    """
    where = str(declaration_path) if declaration_path is not None else "<declaration>"
    findings: list[str] = []
    sheets = build_sheets(config)
    total = len(sheets)
    by_num = {sheet.num: sheet for sheet in sheets}
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=False)

    # Single-file cadenza items per sheet, keyed by resolved path. Prelude
    # items and directory injections are deliberately excluded: generated
    # inputs must be consumed through a per-sheet cadenza file.
    cadenza_file_paths: dict[int, dict[Path, str]] = {}
    for sheet in sheets:
        values = _template_vars(sheet, total)
        for item in sheet.cadenza:
            if item.file is None:
                continue
            try:
                rendered = env.from_string(item.file).render(**values)
            except jinja2.TemplateError:
                continue  # already reported by _injection_paths
            resolved = _resolve_against_workspace(rendered, sheet.workspace)
            cadenza_file_paths.setdefault(sheet.num, {})[resolved] = item.file

    exempt: dict[int, set[Path]] = {}
    records: list[dict[str, Any]] = []
    seen: dict[int, set[Path]] = {}
    for entry in entries:
        consumer = entry["consumer_sheet"]
        producer = entry["producer_sheet"]
        declared = entry["path"]
        if consumer not in by_num:
            findings.append(
                f"generated declaration {where}: consumer sheet {consumer} does not "
                f"exist (valid: 1-{total})"
            )
            continue
        if producer not in by_num:
            findings.append(
                f"generated declaration {where}: unknown producer sheet {producer} "
                f"(valid: 1-{total})"
            )
            continue
        if producer >= consumer:
            findings.append(
                f"generated declaration {where}: producer sheet {producer} must run "
                f"strictly before consumer sheet {consumer}; self-production and "
                "circular production are rejected"
            )
            continue
        dependencies = config.sheet.dependencies.get(consumer, [])
        if producer not in dependencies:
            findings.append(
                f"generated declaration {where}: consumer sheet {consumer} must "
                f"declare producer sheet {producer} in sheet.dependencies "
                f"(got {dependencies})"
            )
            continue
        sheet = by_num[consumer]
        try:
            rendered = env.from_string(declared).render(
                **_template_vars(sheet, total)
            )
        except jinja2.TemplateError as exc:
            findings.append(
                f"generated declaration {where}: path template {declared!r} failed "
                f"to render: {exc}"
            )
            continue
        resolved = _resolve_against_workspace(rendered, sheet.workspace)
        if resolved not in cadenza_file_paths.get(consumer, {}):
            findings.append(
                f"generated declaration {where}: declared path {declared!r} does not "
                f"match any single-file cadenza injection on consumer sheet "
                f"{consumer} (declaration/path mismatch)"
            )
            continue
        consumers_seen = seen.setdefault(consumer, set())
        if resolved in consumers_seen:
            findings.append(
                f"generated declaration {where}: duplicate declaration for consumer "
                f"sheet {consumer} path {declared!r}"
            )
            continue
        consumers_seen.add(resolved)
        exempt.setdefault(consumer, set()).add(resolved)
        records.append(
            {
                "consumer_sheet": consumer,
                "producer_sheet": producer,
                "declared_path": declared,
                "resolved_path": str(resolved),
            }
        )
    return exempt, records, findings


def _generated_context(
    config: JobConfig, score_path: Path, declaration_path: Path | None
) -> tuple[Path | None, dict[int, set[Path]], list[dict[str, Any]], list[str]]:
    decl_path, entries, findings = load_generated_declaration(
        score_path, declaration_path
    )
    if decl_path is None or findings:
        return decl_path, {}, [], findings
    exempt, records, semantic_findings = resolve_generated_inputs(
        config, entries, decl_path
    )
    return decl_path, exempt, records, findings + semantic_findings


def _injection_paths(
    config: JobConfig, exempt: dict[int, set[Path]] | None = None
) -> tuple[list[tuple[str, Path]], list[str]]:
    sheets = build_sheets(config)
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=False)
    resolved: dict[str, Path] = {}
    findings: list[str] = []
    for sheet in sheets:
        values = _template_vars(sheet, len(sheets))
        for item in [*sheet.prelude, *sheet.cadenza]:
            raw = item.file if item.file is not None else item.directory
            kind = "file" if item.file is not None else "directory"
            assert raw is not None
            try:
                rendered = env.from_string(raw).render(**values)
            except jinja2.TemplateError as exc:
                findings.append(
                    f"sheet {sheet.num} injection {raw!r}: template error: {exc}"
                )
                continue
            path = _resolve_against_workspace(rendered, sheet.workspace)
            if (
                exempt is not None
                and kind == "file"
                and path in exempt.get(sheet.num, set())
            ):
                # Declared run-generated input: existence and integrity are
                # consumer-time contracts (native required-cadenza resolution
                # plus delivery receipt), so this path is neither checked nor
                # hashed into the release lock.
                continue
            key = f"sheet:{sheet.num}:{kind}:{raw}"
            if kind == "file":
                if not path.is_file():
                    findings.append(f"sheet {sheet.num} injection missing file: {path}")
                elif path.stat().st_size == 0:
                    findings.append(f"sheet {sheet.num} injection file is empty: {path}")
                else:
                    resolved[key] = path
            else:
                if not path.is_dir():
                    findings.append(f"sheet {sheet.num} injection missing directory: {path}")
                    continue
                files = sorted(candidate for candidate in path.glob("*") if candidate.is_file())
                if not files:
                    findings.append(f"sheet {sheet.num} injection directory is empty: {path}")
                    continue
                for candidate in files:
                    resolved[f"{key}/{candidate.name}"] = candidate.resolve()
    return sorted(resolved.items()), findings


def _workspace_findings(config: JobConfig, project_root: Path) -> list[str]:
    workspace = config.workspace.resolve()
    project = project_root.resolve()
    if workspace == project or project.is_relative_to(workspace):
        return [
            f"workspace policy: {workspace} must not equal or contain project root {project}"
        ]
    return []


def _fallback_findings(config: JobConfig) -> list[str]:
    findings: list[str] = []
    for sheet in build_sheets(config):
        if sheet.instrument_name != "cli":
            continue
        explicit = config.sheet.per_sheet_fallbacks.get(sheet.num)
        if explicit != []:
            findings.append(
                f"sheet {sheet.num} fallback policy: deterministic cli requires "
                "explicit per_sheet_fallbacks entry []"
            )
    return findings


def _validation_findings(config: JobConfig) -> list[str]:
    types = {rule.type for rule in config.validations}
    if not types:
        return ["validation policy: at least one outcome validation is required"]
    if types == {"file_exists"}:
        return [
            "validation policy: file_exists-only validation is decorative; "
            "add structure or behavior proof"
        ]
    return []


def check_score(
    score_path: Path, project_root: Path, declaration_path: Path | None = None
) -> list[str]:
    try:
        config = JobConfig.from_yaml(score_path)
    except Exception as exc:
        return [f"score schema: {exc}"]
    _, exempt, _, generated_findings = _generated_context(
        config, score_path, declaration_path
    )
    _, injection_findings = _injection_paths(config, exempt)
    return [
        *_workspace_findings(config, project_root),
        *_fallback_findings(config),
        *_validation_findings(config),
        *generated_findings,
        *injection_findings,
    ]


def build_lock(
    score_path: Path, project_root: Path, declaration_path: Path | None = None
) -> dict[str, Any]:
    findings = check_score(score_path, project_root, declaration_path)
    if findings:
        raise ValueError("cannot lock invalid score: " + "; ".join(findings))
    config = JobConfig.from_yaml(score_path)
    decl_file, exempt, records, _ = _generated_context(
        config, score_path, declaration_path
    )
    paths, _ = _injection_paths(config, exempt)
    material: dict[str, Any] = {
        "schema_version": 1,
        "score_sha256": _sha256(score_path),
        "injections": {key: _sha256(path) for key, path in paths},
    }
    if decl_file is not None:
        # Declaration bytes are load-bearing: any mutation must invalidate
        # the lock. Generated output bytes are deliberately not hashed; they
        # do not exist at release time and are enforced at consumption.
        material["declaration_sha256"] = _sha256(decl_file)
        material["generated_inputs"] = {
            f"sheet:{record['consumer_sheet']}:{record['declared_path']}": record
            for record in records
        }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return {**material, "candidate_sha256": hashlib.sha256(encoded).hexdigest()}


def verify_lock(
    score_path: Path,
    project_root: Path,
    expected: dict[str, Any],
    declaration_path: Path | None = None,
) -> list[str]:
    try:
        current = build_lock(score_path, project_root, declaration_path)
    except ValueError as exc:
        return [str(exc)]
    if current.get("candidate_sha256") != expected.get("candidate_sha256"):
        return [
            "candidate digest mismatch: score or load-bearing injection changed; "
            "reevaluation required"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument(
        "--generated",
        type=Path,
        default=None,
        help=(
            "Generated-input declaration file; defaults to "
            f"<score-stem>{DECLARATION_SUFFIX} next to the score"
        ),
    )
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--write-lock", action="store_true")
    args = parser.parse_args()
    findings = check_score(args.score, args.project_root, args.generated)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    lock_path = args.lock or args.score.with_name("composition-lock.json")
    if args.write_lock:
        lock = build_lock(args.score, args.project_root, args.generated)
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"composition lock written: {lock_path}")
        return 0
    if lock_path.is_file():
        expected = json.loads(lock_path.read_text(encoding="utf-8"))
        findings = verify_lock(args.score, args.project_root, expected, args.generated)
        if findings:
            for finding in findings:
                print(f"ERROR: {finding}")
            return 1
        print("composition score and lock verified")
    else:
        print("composition score verified (no lock supplied)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
