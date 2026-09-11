"""Focused behavioral tests for the marianne-search helper.

Covers: valid results; causal rejection of missing/empty input, nesting,
binary/oversized inputs, input inside the workspace; malformed, empty,
placeholder, wrong-lane, and stale (prior-run) lane reports; no_web honesty;
deterministic collection; paths with spaces and shell metacharacters.

The helper is imported from its in-tree candidate path; no engine code and no
network I/O is involved.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
HELPER = (
    PLUGIN_ROOT
    / "marianne"
    / "skills"
    / "marianne-search"
    / "scripts"
    / "marianne_search.py"
)

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


class ValidateReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.receipt_path = write(
            self.base / "run-receipt.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "kind": "marianne-search-run-receipt",
                    "run_id": "11111111-1111-1111-1111-111111111111",
                    "input_sha256": "a" * 64,
                    "input_dir": "/tmp/in",
                }
            ),
        )
        self.report_path = self.base / "findings-1.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def validate(self, payload, lane: int = 1, receipt: bool = True) -> int:
        self.report_path.write_text(json.dumps(payload), encoding="utf-8")
        argv = ["validate-report", "--file", str(self.report_path), "--lane", str(lane)]
        if receipt:
            argv += ["--receipt", str(self.receipt_path)]
        return ms.main(argv)

    def test_valid_complete_report_passes(self) -> None:
        self.assertEqual(self.validate(findings()), ms.EXIT_OK)

    def test_malformed_json_rejected(self) -> None:
        self.report_path.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.validate({}), ms.EXIT_BAD_REPORT)

    def test_wrong_lane_rejected(self) -> None:
        self.assertEqual(self.validate(findings(lane=2), lane=1), ms.EXIT_BAD_REPORT)

    def test_stale_run_id_rejected(self) -> None:
        self.assertEqual(
            self.validate(findings(run_id="99999999-9999-9999-9999-999999999999")),
            ms.EXIT_BAD_REPORT,
        )

    def test_unknown_status_rejected(self) -> None:
        self.assertEqual(self.validate(findings(status="success")), ms.EXIT_BAD_REPORT)

    def test_empty_summary_rejected(self) -> None:
        self.assertEqual(self.validate(findings(summary="   ")), ms.EXIT_BAD_REPORT)

    def test_placeholder_finding_rejected(self) -> None:
        item = {
            "url": "https://example.com/cache",
            "title": "TODO",
            "accessed": "2026-09-11",
            "claims": ["TBD"],
            "integration": "TBD",
            "constraints": "n/a",
        }
        self.assertEqual(self.validate(findings(items=[item])), ms.EXIT_BAD_REPORT)

    def test_claimless_finding_rejected(self) -> None:
        item = {
            "url": "https://real.example.dev/docs",
            "title": "Docs",
            "accessed": "2026-09-11",
            "claims": [],
            "integration": "pip install",
            "constraints": "MIT",
        }
        self.assertEqual(self.validate(findings(items=[item])), ms.EXIT_BAD_REPORT)

    def test_bad_access_date_rejected(self) -> None:
        payload = findings()
        payload["findings"][0]["accessed"] = "recently"
        self.assertEqual(self.validate(payload), ms.EXIT_BAD_REPORT)

    def test_complete_without_queries_rejected(self) -> None:
        self.assertEqual(self.validate(findings(queries=[])), ms.EXIT_BAD_REPORT)

    def test_degraded_requires_reason(self) -> None:
        self.assertEqual(self.validate(findings(status="degraded")), ms.EXIT_BAD_REPORT)

    def test_valid_degraded_passes(self) -> None:
        self.assertEqual(
            self.validate(findings(status="degraded", degraded_reason="search ok, fetch blocked")),
            ms.EXIT_OK,
        )

    def test_no_web_with_claims_rejected(self) -> None:
        self.assertEqual(self.validate(findings(status="no_web")), ms.EXIT_BAD_REPORT)

    def test_no_web_honest_passes(self) -> None:
        payload = findings(
            status="no_web",
            queries=[],
            items=[],
            recommendation={"mode": "undetermined", "reasoning": "no web access this run"},
            tool_evidence={"search_tool": "websearch", "fetch_tool": "webfetch", "notes": "search tool denied by host permissions"},
        )
        self.assertEqual(self.validate(payload), ms.EXIT_OK)

    def test_missing_report_rejected(self) -> None:
        argv = [
            "validate-report",
            "--file",
            str(self.base / "absent.json"),
            "--lane",
            "1",
            "--receipt",
            str(self.receipt_path),
        ]
        self.assertEqual(ms.main(argv), ms.EXIT_BAD_REPORT)


class CollectTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def stage(self, reports: list[dict], run_id: str = "11111111-1111-1111-1111-111111111111") -> None:
        write(
            self.workspace / "run-receipt.json",
            json.dumps({"schema_version": 1, "kind": "marianne-search-run-receipt", "run_id": run_id, "input_dir": "/tmp/in", "input_sha256": "a" * 64}),
        )
        for index, report in enumerate(reports, start=1):
            write(self.workspace / f"findings-{index}.json", json.dumps(report))

    def collect(self, lanes: int = 1) -> int:
        return ms.main(["collect", "--workspace", str(self.workspace), "--lanes", str(lanes)])

    def test_collect_renders_complete_results(self) -> None:
        self.stage([findings()])
        self.assertEqual(self.collect(), ms.EXIT_OK)
        results = json.loads((self.workspace / "results.json").read_text())
        self.assertEqual(results["overall"], "complete")
        self.assertEqual(results["lane_count"], 1)
        self.assertEqual(results["run_id"], "11111111-1111-1111-1111-111111111111")
        markdown = (self.workspace / "results.md").read_text()
        self.assertIn("Example Cache Docs", markdown)
        self.assertIn("2026-09-11", markdown)

    def test_collect_is_deterministic(self) -> None:
        self.stage([findings()])
        self.assertEqual(self.collect(), ms.EXIT_OK)
        first = json.loads((self.workspace / "results.json").read_text())
        first_md = (self.workspace / "results.md").read_text()
        self.stage([findings()])
        self.assertEqual(self.collect(), ms.EXIT_OK)
        second = json.loads((self.workspace / "results.json").read_text())
        second_md = (self.workspace / "results.md").read_text()
        first.pop("collected_at")
        second.pop("collected_at")
        self.assertEqual(first, second)
        self.assertEqual(first_md, second_md)

    def test_collect_overall_degraded(self) -> None:
        self.stage(
            [
                findings(),
                findings(
                    lane=2,
                    status="degraded",
                    degraded_reason="page fetches blocked",
                    run_id="11111111-1111-1111-1111-111111111111",
                ),
            ]
        )
        self.assertEqual(self.collect(lanes=2), ms.EXIT_OK)
        results = json.loads((self.workspace / "results.json").read_text())
        self.assertEqual(results["overall"], "degraded")

    def test_collect_overall_no_web(self) -> None:
        self.stage(
            [
                findings(
                    status="no_web",
                    queries=[],
                    items=[],
                    gaps=[],
                    recommendation={"mode": "undetermined", "reasoning": "offline"},
                    tool_evidence={"notes": "websearch unavailable"},
                )
            ]
        )
        self.assertEqual(self.collect(), ms.EXIT_OK)
        results = json.loads((self.workspace / "results.json").read_text())
        self.assertEqual(results["overall"], "no_web")

    def test_collect_rejects_missing_lane_report(self) -> None:
        self.stage([findings()])
        self.assertEqual(self.collect(lanes=2), ms.EXIT_BAD_REPORT)
        self.assertFalse((self.workspace / "results.json").exists())

    def test_collect_rejects_stale_prior_run_report(self) -> None:
        self.stage([findings()], run_id="22222222-2222-2222-2222-222222222222")
        self.assertEqual(self.collect(), ms.EXIT_BAD_REPORT)
        self.assertFalse((self.workspace / "results.json").exists())

    def test_collect_rejects_placeholder_report(self) -> None:
        self.stage([findings(items=[{
            "url": "https://example.org/x",
            "title": "TBD",
            "accessed": "2026-09-11",
            "claims": ["placeholder"],
            "integration": "TODO",
            "constraints": "unknown",
        }])])
        self.assertEqual(self.collect(), ms.EXIT_BAD_REPORT)


class ZeroMatchTests(unittest.TestCase):
    """Finding 2: honest evidenced zero-match must be permitted."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.report_path = self.base / "findings-1.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def validate(self, payload) -> int:
        self.report_path.write_text(json.dumps(payload), encoding="utf-8")
        return ms.main(
            ["validate-report", "--file", str(self.report_path), "--lane", "1"]
        )

    def zero_match(self, status: str = "complete", **overrides) -> dict:
        payload = findings(
            status=status,
            items=[],
            queries=[
                {"query": "python cli cache ttl multiprocess", "tool": "websearch", "result_count": 0},
                {"query": "site:github.com python cli cache", "tool": "webfetch", "result_count": 0},
            ],
            gaps=["No maintained candidate found across queried sources."],
            recommendation={"mode": "undetermined", "reasoning": "Zero verified matches; nothing to recommend."},
        )
        payload.update(overrides)
        return payload

    def test_complete_zero_match_with_evidence_passes(self) -> None:
        self.assertEqual(self.validate(self.zero_match()), ms.EXIT_OK)

    def test_degraded_zero_match_with_evidence_passes(self) -> None:
        payload = self.zero_match(status="degraded", degraded_reason="search ok, fetches blocked")
        self.assertEqual(self.validate(payload), ms.EXIT_OK)

    def test_zero_match_claiming_recommendation_rejected(self) -> None:
        payload = self.zero_match(
            recommendation={"mode": "reuse", "reasoning": "fabricated confidence"}
        )
        self.assertEqual(self.validate(payload), ms.EXIT_BAD_REPORT)

    def test_zero_match_without_queries_rejected(self) -> None:
        self.assertEqual(self.validate(self.zero_match(queries=[])), ms.EXIT_BAD_REPORT)

    def test_zero_match_without_gaps_rejected(self) -> None:
        self.assertEqual(self.validate(self.zero_match(gaps=[])), ms.EXIT_BAD_REPORT)


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


try:  # template/tooling controls need the runtime dependency set only
    import jinja2
    import shlex

    import yaml as _yaml

    _TEMPLATE_TOOLS = True
except ImportError:  # pragma: no cover
    _TEMPLATE_TOOLS = False


@unittest.skipUnless(_TEMPLATE_TOOLS, "jinja2/yaml not importable")
class ShellSafetyTests(unittest.TestCase):
    """Finding 1: rendered shell and engine-formatted validation commands must
    neutralize hostile paths — proven by EXECUTION (markers), not bash -n."""

    SCORE = (
        PLUGIN_ROOT
        / "marianne"
        / "skills"
        / "marianne-search"
        / "scores"
        / "marianne-search.yaml"
    )

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        # Hostile workspace/input: apostrophes, spaces, command substitution,
        # backticks. Any unescaped interpolation would create marker files.
        self.workspace = self.base / "ws 'q $(touch M_WS) `id` & dir"
        self.input_dir = self.base / "in 'p $(touch M_IN); dir"
        self.control = self.base / "markers-control"
        self.workspace.mkdir()
        self.control.mkdir()
        self.input_dir.mkdir()
        write(self.input_dir / "prompt.md", "research task; benign content\n")
        self.assertTrue((self.base / "ws 'q $(touch M_WS) `id` & dir").exists())

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def markers_absent(self) -> bool:
        created = [p.name for p in self.control.iterdir()]
        return not created, f"markers created: {created}"

    def _render(self, score_path: Path, stage: int) -> str:
        cfg = _yaml.safe_load(score_path.read_text(encoding="utf-8"))
        env = jinja2.Environment(
            undefined=jinja2.StrictUndefined, keep_trailing_newline=True
        )
        template = env.from_string(cfg["prompt"]["template"])
        return template.render(
            workspace=str(self.workspace),
            score_dir=str(score_path.parent),
            stage=stage,
            input_dir=str(self.input_dir),
            max_input_bytes="262144",
            lane_count=cfg["prompt"]["variables"]["lane_count"],
        )

    def _run_bash(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            cwd=self.control,
            timeout=60,
        )

    def test_prepare_stage_executes_without_injection(self) -> None:
        script = self._render(self.SCORE, 1)
        result = self._run_bash(script)
        self.assertEqual(result.returncode, 0, result.stderr)
        ok, detail = self.markers_absent()
        self.assertTrue(ok, detail)
        receipt = json.loads((self.workspace / "run-receipt.json").read_text())
        self.assertEqual(receipt["input_dir"], str(self.input_dir))

    def test_collect_stage_executes_without_injection(self) -> None:
        # Stage the workspace as a completed one-lane run first.
        script = self._render(self.SCORE, 1)
        self.assertEqual(self._run_bash(script).returncode, 0)
        receipt = json.loads((self.workspace / "run-receipt.json").read_text())
        report = findings(run_id=receipt["run_id"])
        (self.workspace / "findings-1.json").write_text(json.dumps(report), encoding="utf-8")
        collect = self._render(self.SCORE, 3)
        result = self._run_bash(collect)
        self.assertEqual(result.returncode, 0, result.stderr)
        ok, detail = self.markers_absent()
        self.assertTrue(ok, detail)
        results = json.loads((self.workspace / "results.json").read_text())
        self.assertEqual(results["overall"], "complete")

    def test_engine_formatted_validation_command_does_not_inject(self) -> None:
        # Replicates the engine's exact command substitution
        # (execution/validation/engine.py: {key} -> shlex.quote(value)) and
        # executes the resulting command against a hostile workspace.
        cfg = _yaml.safe_load(self.SCORE.read_text(encoding="utf-8"))
        rule = next(
            v
            for v in cfg["validations"]
            if v.get("type") == "command_succeeds" and "--lane 1" in v.get("command", "")
        )
        expanded = rule["command"].replace("{workspace}", shlex.quote(str(self.workspace)))
        result = self._run_bash(expanded)
        self.assertNotEqual(result.returncode, 0)  # helper/report absent: fails causally
        self.assertIn("M_WS", result.stderr)  # hostile path stayed literal in the message
        ok, detail = self.markers_absent()
        self.assertTrue(ok, detail)


@unittest.skipUnless(_TEMPLATE_TOOLS, "jinja2/yaml not importable")
class TwoLaneRoutingTests(unittest.TestCase):
    """Finding 4: the two-lane instance must route every stage correctly."""

    TWO_LANE = (
        PLUGIN_ROOT
        / "marianne"
        / "skills"
        / "marianne-search"
        / "scores"
        / "marianne-search-two-lane.yaml"
    )

    def _render(self, stage: int) -> str:
        cfg = _yaml.safe_load(self.TWO_LANE.read_text(encoding="utf-8"))
        env = jinja2.Environment(
            undefined=jinja2.StrictUndefined, keep_trailing_newline=True
        )
        template = env.from_string(cfg["prompt"]["template"])
        return template.render(
            workspace="/tmp/ws", score_dir=str(self.TWO_LANE.parent),
            stage=stage, input_dir="/tmp/in",
            max_input_bytes="262144",
            lane_count=cfg["prompt"]["variables"]["lane_count"],
        )

    def test_stage_routing(self) -> None:
        self.assertIn("prepare", self._render(1))
        stage2 = self._render(2)
        self.assertIn("research lane 1", stage2)
        self.assertIn("findings-1.json", stage2)
        stage3 = self._render(3)
        self.assertIn("research lane 2", stage3)
        self.assertIn("findings-2.json", stage3)
        self.assertNotIn("findings-1.json", stage3)
        collect = self._render(4)
        self.assertIn("--lanes 2", collect)
        self.assertNotIn("findings-", collect)
        self.assertNotIn("research lane", collect)

    def test_sheet_structure_is_coordinated(self) -> None:
        cfg = _yaml.safe_load(self.TWO_LANE.read_text(encoding="utf-8"))
        self.assertEqual(cfg["sheet"]["total_items"], 4)
        self.assertEqual(cfg["prompt"]["variables"]["lane_count"], "2")
        self.assertEqual(cfg["sheet"]["dependencies"], {2: [1], 3: [1], 4: [2, 3]})
        self.assertEqual(
            cfg["sheet"]["per_sheet_fallbacks"], {1: [], 2: [], 3: [], 4: []}
        )
        self.assertEqual(sorted(cfg["sheet"]["cadenzas"]), [2, 3])
        for lane_sheet, lane in ((2, 1), (3, 2)):
            rules = [
                v
                for v in cfg["validations"]
                if v.get("condition") == f"sheet_num == {lane_sheet}"
            ]
            self.assertTrue(any(f"findings-{lane}.json" in str(v) for v in rules))
            self.assertTrue(any(f"--lane {lane}" in str(v) for v in rules))
        collect_rules = [
            v for v in cfg["validations"] if v.get("condition") == "sheet_num == 4"
        ]
        self.assertEqual(len(collect_rules), 4)


if __name__ == "__main__":
    unittest.main()
