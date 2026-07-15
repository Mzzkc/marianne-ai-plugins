#!/usr/bin/env python3
"""Gate a composed Marianne score and lock its load-bearing inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jinja2

from marianne.core.config.job import JobConfig
from marianne.core.sheet import Sheet, build_sheets


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


def _injection_paths(config: JobConfig) -> tuple[list[tuple[str, Path]], list[str]]:
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
            path = Path(rendered)
            if not path.is_absolute():
                path = sheet.workspace / path
            path = path.resolve()
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


def check_score(score_path: Path, project_root: Path) -> list[str]:
    try:
        config = JobConfig.from_yaml(score_path)
    except Exception as exc:
        return [f"score schema: {exc}"]
    _, injection_findings = _injection_paths(config)
    return [
        *_workspace_findings(config, project_root),
        *_fallback_findings(config),
        *_validation_findings(config),
        *injection_findings,
    ]


def build_lock(score_path: Path, project_root: Path) -> dict[str, Any]:
    findings = check_score(score_path, project_root)
    if findings:
        raise ValueError("cannot lock invalid score: " + "; ".join(findings))
    config = JobConfig.from_yaml(score_path)
    paths, _ = _injection_paths(config)
    material = {
        "schema_version": 1,
        "score_sha256": _sha256(score_path),
        "injections": {key: _sha256(path) for key, path in paths},
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return {**material, "candidate_sha256": hashlib.sha256(encoded).hexdigest()}


def verify_lock(
    score_path: Path, project_root: Path, expected: dict[str, Any]
) -> list[str]:
    try:
        current = build_lock(score_path, project_root)
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
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--write-lock", action="store_true")
    args = parser.parse_args()
    findings = check_score(args.score, args.project_root)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    lock_path = args.lock or args.score.with_name("composition-lock.json")
    if args.write_lock:
        lock = build_lock(args.score, args.project_root)
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"composition lock written: {lock_path}")
        return 0
    if lock_path.is_file():
        expected = json.loads(lock_path.read_text(encoding="utf-8"))
        findings = verify_lock(args.score, args.project_root, expected)
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
