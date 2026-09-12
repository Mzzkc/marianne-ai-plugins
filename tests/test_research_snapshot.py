"""Preserved historical snapshot/UTF-8 boundary regressions, retargeted to retained lab dependency."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE if (HERE/'scripts/trial.py').is_file() else HERE/'marianne/skills/research'
HELPER=ROOT/'lab/scripts/snapshot.py'

_spec = importlib.util.spec_from_file_location("marianne_search_helper", HELPER)
ms = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ms)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def findings(
    *,
    run_id: str = "11111111-1111-1111-1111-111111111111",
    lane: int = 1,
    status: str = "complete",
    summary: str = "Found maintained candidates.",
    queries: list | None = None,
    items: list | None = None,
    gaps: list | None = None,
    recommendation: dict | None = None,
    **extra,
) -> dict:
    payload = {
        "schema_version": 1,
        "kind": "marianne-search-findings",
        "run_id": run_id,
        "lane": lane,
        "status": status,
        "summary": summary,
        "queries": queries
        if queries is not None
        else [{"query": "python cli cache ttl", "tool": "websearch", "result_count": 5}],
        "findings": items
        if items is not None
        else [
            {
                "url": "https://docs.example-project.dev/cache",
                "title": "Example Cache Docs",
                "accessed": "2026-09-11",
                "claims": ["Supports TTL eviction since v2.0."],
                "integration": "pip install example-cache; wrap the CLI store.",
                "constraints": "MIT; single maintainer, unknown.",
            }
        ],
        "gaps": gaps if gaps is not None else ["Windows named-lock behavior unverified."],
        "recommendation": recommendation
        or {"mode": "reuse", "reasoning": "Maintained, permissive license, fits stdlib+pip stack."},
    }
    payload.update(extra)
    return payload


class PrepareTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.input_dir = self.base / "in"
        self.workspace = self.base / "ws out"
        self.workspace.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_prepare(self, input_dir: str | None = None) -> int:
        return ms.main(
            [
                "prepare",
                "--input-dir",
                input_dir if input_dir is not None else str(self.input_dir),
                "--workspace",
                str(self.workspace),
            ]
        )

    def test_prepare_snapshots_exact_bytes_and_receipt(self) -> None:
        write(self.input_dir / "prompt.md", "Research caching options.\n")
        write(self.input_dir / "notes.md", "Stack: Python 3.12\n")
        rc = self.run_prepare()
        self.assertEqual(rc, ms.EXIT_OK)
        snap = self.workspace / "input-snapshot"
        self.assertEqual(
            (snap / "prompt.md").read_bytes(),
            (self.input_dir / "prompt.md").read_bytes(),
        )
        receipt = json.loads((self.workspace / "run-receipt.json").read_text())
        self.assertEqual(receipt["kind"], "marianne-search-run-receipt")
        self.assertRegex(receipt["run_id"], r"[0-9a-f-]{36}")
        self.assertRegex(receipt["input_sha256"], r"[0-9a-f]{64}")
        self.assertEqual([f["name"] for f in receipt["files"]], ["notes.md", "prompt.md"])

    def test_prepare_rejects_missing_dir(self) -> None:
        rc = self.run_prepare(input_dir=str(self.base / "nope"))
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_empty_var(self) -> None:
        rc = self.run_prepare(input_dir="")
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_empty_prompt(self) -> None:
        write(self.input_dir / "prompt.md", "   \n\t\n")
        rc = self.run_prepare()
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_missing_prompt(self) -> None:
        write(self.input_dir / "context.md", "no prompt here\n")
        rc = self.run_prepare()
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_nesting(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        write(self.input_dir / "nested" / "deep.md", "hidden\n")
        rc = self.run_prepare()
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_binary(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        (self.input_dir / "blob.bin").write_bytes(b"ok\x00\x01\x02binary")
        rc = self.run_prepare()
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_oversized_input(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        write(self.input_dir / "big.txt", "x" * 4096)
        rc = ms.main(
            [
                "prepare",
                "--input-dir",
                str(self.input_dir),
                "--workspace",
                str(self.workspace),
                "--max-bytes",
                "1024",
            ]
        )
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_rejects_input_inside_workspace(self) -> None:
        inside = self.workspace / "in"
        write(inside / "prompt.md", "task\n")
        rc = self.run_prepare(input_dir=str(inside))
        self.assertEqual(rc, ms.EXIT_BAD_INPUT)

    def test_prepare_clears_stale_prior_run_outputs(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        stale = findings()
        (self.workspace / "findings-1.json").write_text(json.dumps(stale), encoding="utf-8")
        (self.workspace / "results.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.run_prepare(), ms.EXIT_OK)
        self.assertFalse((self.workspace / "findings-1.json").exists())
        self.assertFalse((self.workspace / "results.json").exists())

    def test_prepare_handles_spaces_and_metacharacters(self) -> None:
        tricky = self.base / "in put; $(whoami) `id` & dir"
        write(tricky / "prompt.md", "task; rm -rf '$(never)'\n")
        rc = self.run_prepare(input_dir=str(tricky))
        self.assertEqual(rc, ms.EXIT_OK)
        receipt = json.loads((self.workspace / "run-receipt.json").read_text())
        self.assertEqual(receipt["input_dir"], str(tricky.resolve()))


class ByteBoundaryTests(unittest.TestCase):
    """Finding 3: bound before allocating; validate the complete byte sequence."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.input_dir = self.base / "in"
        self.workspace = self.base / "ws"
        self.workspace.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def prepare(self, max_bytes: int | None = None) -> int:
        argv = [
            "prepare",
            "--input-dir",
            str(self.input_dir),
            "--workspace",
            str(self.workspace),
        ]
        if max_bytes is not None:
            argv += ["--max-bytes", str(max_bytes)]
        return ms.main(argv)

    def test_nul_beyond_prefix_rejected(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        payload = b"a" * 9000 + b"\x00" + b"b" * 100
        (self.input_dir / "late.bin").write_bytes(payload)
        self.assertEqual(self.prepare(), ms.EXIT_BAD_INPUT)
        self.assertFalse((self.workspace / "input-snapshot").exists())

    def test_invalid_utf8_beyond_prefix_rejected(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        payload = b"a" * 9000 + b"\xff\xfe" + b"b" * 10
        (self.input_dir / "late.txt").write_bytes(payload)
        self.assertEqual(self.prepare(), ms.EXIT_BAD_INPUT)

    def test_multibyte_character_crossing_prefix_boundary_accepted(self) -> None:
        # 'é' is 2 bytes; place its first byte at offset 8190 so the character
        # straddles any 8192-byte prefix logic.
        head = b"a" * 8190
        body = "é之写入 content after the boundary.\n".encode("utf-8")
        write(self.input_dir / "prompt.md", "task\n")
        (self.input_dir / "crossing.md").write_bytes(head + body)
        self.assertEqual(self.prepare(), ms.EXIT_OK)
        snapshot = self.workspace / "input-snapshot" / "crossing.md"
        self.assertEqual(snapshot.read_bytes(), head + body)
        receipt = json.loads((self.workspace / "run-receipt.json").read_text())
        names = {f["name"]: f["bytes"] for f in receipt["files"]}
        self.assertEqual(names["crossing.md"], len(head + body))

    def test_oversized_rejected_before_read(self) -> None:
        write(self.input_dir / "prompt.md", "task\n")
        big = self.input_dir / "big.txt"
        with big.open("wb") as fh:
            fh.seek(200_000 - 1)
            fh.write(b"x")
        self.assertEqual(self.prepare(max_bytes=1024), ms.EXIT_BAD_INPUT)
        self.assertFalse((self.workspace / "input-snapshot").exists())


