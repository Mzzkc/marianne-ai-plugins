#!/usr/bin/env python3
"""Standalone structural validator for scores pinned to this kit's contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALIDATIONS = {
    "file_exists": {"path"}, "file_modified": {"path"},
    "content_contains": {"path", "pattern"},
    "content_regex": {"path", "pattern"},
    "command_succeeds": {"command"}, "path_in_scope": {"path"},
    "field_match": {"path", "field_path"},
    "file_sha256": {"path", "sha256"},
    "csv_unique_key": {"path", "key_field"},
}


def load_score(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError("YAML input requires PyYAML; JSON input uses only the standard library") from exc
    return yaml.safe_load(text)


def validate(score: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(score, dict):
        return ["score root must be a mapping"]
    if not isinstance(score.get("name"), str) or not score["name"].strip():
        errors.append("name must be a non-empty string")
    workspace = score.get("workspace", "./workspace")
    if not isinstance(workspace, str):
        errors.append("workspace must be a path string")
    elif workspace.strip() in {"/", "~", "~/"}:
        errors.append("workspace must not be a filesystem root or home directory")
    sheet = score.get("sheet")
    if not isinstance(sheet, dict):
        errors.append("sheet must be a mapping")
    else:
        for field in ("size", "total_items"):
            value = sheet.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"sheet.{field} must be an integer >= 1")
        deps = sheet.get("dependencies", {})
        if not isinstance(deps, dict):
            errors.append("sheet.dependencies must be a mapping")
        else:
            graph: dict[int, list[int]] = {}
            for node, parents in deps.items():
                try:
                    node_i = int(node)
                except (TypeError, ValueError):
                    errors.append(f"dependency key {node!r} is not an integer")
                    continue
                if not isinstance(parents, list) or any(not isinstance(p, int) for p in parents):
                    errors.append(f"dependencies[{node!r}] must be a list of integers")
                    continue
                graph[node_i] = parents
            visiting: set[int] = set()
            visited: set[int] = set()
            def visit(node: int) -> None:
                if node in visiting:
                    errors.append(f"dependency cycle includes sheet {node}")
                    return
                if node in visited:
                    return
                visiting.add(node)
                for parent in graph.get(node, []):
                    visit(parent)
                visiting.remove(node)
                visited.add(node)
            for node in graph:
                visit(node)
    prompt = score.get("prompt")
    if not isinstance(prompt, dict):
        errors.append("prompt must be a mapping")
    else:
        present = [key for key in ("template", "template_file") if prompt.get(key) is not None]
        if len(present) != 1:
            errors.append("prompt must specify exactly one of template or template_file")
        template = prompt.get("template")
        if isinstance(template, str) and score.get("instrument") == "cli":
            if "${#" in template and "{% raw %}" not in template:
                errors.append("cli prompt contains ${#...}, which collides with Jinja comments; use a raw block")
            if "```" in template or any(line.lstrip().startswith(("## ", "- ")) for line in template.splitlines()):
                errors.append("cli prompt contains markdown that is not executable shell")
    rules = score.get("validations", [])
    if not isinstance(rules, list):
        errors.append("validations must be a list")
    else:
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                errors.append(f"validations[{index}] must be a mapping")
                continue
            kind = rule.get("type")
            if kind not in VALIDATIONS:
                errors.append(f"validations[{index}].type is not one of the 9 pinned types")
                continue
            missing = sorted(VALIDATIONS[kind] - rule.keys())
            if missing:
                errors.append(f"validations[{index}] missing: {', '.join(missing)}")
            for field in ("path", "working_directory", "path_scope", "source_path"):
                value = rule.get(field)
                if isinstance(value, str) and ("{{" in value or "}}" in value):
                    errors.append(
                        f"validations[{index}].{field} uses Jinja braces; validation paths use single-brace .format()"
                    )
            if kind == "field_match" and "expected_value" not in rule and "source_path" not in rule:
                errors.append(f"validations[{index}] field_match needs expected_value or source_path")
    state_backend = score.get("state_backend", "sqlite")
    if state_backend not in {"json", "sqlite"}:
        errors.append("state_backend must be json or sqlite")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(load_score(args.score))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"SCORE_INVALID: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("SCORE_INVALID", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("SCORE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
