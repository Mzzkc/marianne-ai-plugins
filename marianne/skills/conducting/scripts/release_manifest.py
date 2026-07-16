#!/usr/bin/env python3
"""Build or verify a relocatable SHA-256 manifest for a skill release."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


MANIFEST_NAME = "MANIFEST.sha256"
EXCLUDED_PARTS = {".git", "__pycache__"}


def _included(path: Path, root: Path, manifest_name: str) -> bool:
    relative = path.relative_to(root)
    return (
        path.is_file()
        and relative.as_posix() != manifest_name
        and not any(part in EXCLUDED_PARTS for part in relative.parts)
        and path.suffix != ".pyc"
    )


def _digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _current(root: Path, manifest_name: str) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _digest(path)
        for path in sorted(root.rglob("*"))
        if _included(path, root, manifest_name)
    }


def build_manifest(root: Path, manifest_name: str = MANIFEST_NAME) -> Path:
    root = root.resolve()
    entries = _current(root, manifest_name)
    output = root / manifest_name
    output.write_text(
        "".join(f"{digest}  {path}\n" for path, digest in entries.items()),
        encoding="utf-8",
    )
    return output


def verify_manifest(
    root: Path,
    manifest_name: str = MANIFEST_NAME,
) -> list[str]:
    root = root.resolve()
    manifest = root / manifest_name
    if not manifest.is_file():
        return [f"missing manifest: {manifest_name}"]
    expected: dict[str, str] = {}
    findings: list[str] = []
    for number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(),
        1,
    ):
        try:
            digest, path = line.split("  ", 1)
        except ValueError:
            findings.append(f"invalid manifest line {number}")
            continue
        expected[path] = digest
    current = _current(root, manifest_name)
    for path in sorted(expected.keys() - current.keys()):
        findings.append(f"missing file: {path}")
    for path in sorted(current.keys() - expected.keys()):
        findings.append(f"unlisted file: {path}")
    for path in sorted(expected.keys() & current.keys()):
        if expected[path] != current[path]:
            findings.append(f"digest mismatch: {path}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", default=MANIFEST_NAME)
    args = parser.parse_args()
    if args.command == "build":
        print(build_manifest(args.root, args.output))
        return 0
    findings = verify_manifest(args.root, args.output)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print("manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
