#!/usr/bin/env python3
"""Verify the pinned claim registry and source-slice hashes offline."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "evidence" / "claims.jsonl"
SLICES = ROOT / "evidence" / "source-slices"


def main() -> int:
    errors: list[str] = []
    seen: set[str] = set()
    count = 0
    for line_no, raw in enumerate(CLAIMS.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            claim = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"claims.jsonl:{line_no}: invalid JSON: {exc}")
            continue
        claim_id = claim.get("id")
        expected = claim.get("excerpt_hash")
        if not isinstance(claim_id, str) or not isinstance(expected, str):
            errors.append(f"claims.jsonl:{line_no}: id/excerpt_hash must be strings")
            continue
        if claim_id in seen:
            errors.append(f"duplicate claim id: {claim_id}")
            continue
        seen.add(claim_id)
        count += 1
        source_slice = SLICES / f"{claim_id}.txt"
        if not source_slice.is_file():
            errors.append(f"missing source slice: {source_slice.relative_to(ROOT)}")
            continue
        actual = hashlib.sha256(source_slice.read_bytes()).hexdigest()
        if actual[: len(expected)].lower() != expected.lower():
            errors.append(f"{claim_id}: expected {expected}, got {actual}")

    extras = sorted(p.stem for p in SLICES.glob("*.txt") if p.stem not in seen)
    if extras:
        errors.append("unregistered source slices: " + ", ".join(extras))
    if errors:
        print("CLAIMS_INVALID", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"CLAIMS_VERIFIED {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

