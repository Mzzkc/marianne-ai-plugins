#!/usr/bin/env python3
"""Deterministic helper for the marianne-search score.

Subcommands:
  prepare         Validate a flat input directory, snapshot it byte-exactly
                  into the run workspace, and write a run receipt with a
                  fresh run ID and input digest.
  validate-report Structurally validate one lane's findings JSON.
  collect         Validate all declared lane reports and render deterministic
                  results.json / results.md summaries.

This is a collection helper, not a search backend and not a synthesis engine.
It never performs network I/O.
"""

from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECEIPT_KIND = "marianne-search-run-receipt"
FINDINGS_KIND = "marianne-search-findings"
RESULTS_KIND = "marianne-search-results"
SCHEMA_VERSION = 1
DEFAULT_MAX_INPUT_BYTES = 262_144
STATUSES = ("complete", "degraded", "no_web")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://\S+$")
PLACEHOLDER_VALUES = {"todo", "tbd", "placeholder", "n/a", "na", "none", "example", "redacted"}
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "127.0.0.1"}
STALE_OUTPUTS = ("results.json", "results.md")

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_BAD_REPORT = 3


class InputError(Exception):
    """Caller-supplied input is missing, malformed, or unsafe to stage."""


class ReportError(Exception):
    """A lane report is missing, malformed, stale, or placeholder."""


# ---------------------------------------------------------------- utilities


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportError(f"{path.name}: cannot parse JSON report ({exc})") from exc
    if not isinstance(payload, dict):
        raise ReportError(f"{path.name}: top-level JSON must be an object")
    return payload


def _stream_is_text(path: Path, chunk_size: int = 65_536) -> bool:
    """Validate the complete byte sequence without unbounded allocation.

    Rejects NUL bytes anywhere and invalid UTF-8 anywhere, including past
    any prefix boundary; a multibyte character crossing a chunk edge is
    accepted via an incremental decoder.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    with path.open("rb") as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            if b"\0" in block:
                return False
            try:
                decoder.decode(block)
            except UnicodeDecodeError:
                return False
    try:
        decoder.decode(b"", True)
    except UnicodeDecodeError:
        return False
    return True


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReportError(message)


def _nonempty_str(payload: dict[str, Any], key: str, label: str) -> str:
    value = payload.get(key)
    _require(isinstance(value, str) and value.strip(), f"{label}: field '{key}' must be a nonempty string")
    return value


# ------------------------------------------------------------------ prepare


def cmd_prepare(args: argparse.Namespace) -> int:
    if not args.input_dir or not args.input_dir.strip():
        raise InputError(
            "--input-dir is required: pass --var input_dir=/absolute/path/to/flat-input-dir"
        )
    input_dir = Path(args.input_dir).expanduser()
    workspace = Path(args.workspace).expanduser().resolve()
    max_bytes = int(args.max_bytes)

    if not input_dir.exists() or not input_dir.is_dir():
        raise InputError(f"input directory not found: {input_dir}")
    input_dir = input_dir.resolve()
    if workspace in input_dir.parents or input_dir == workspace:
        raise InputError(
            "input directory must live outside the run workspace "
            f"(got {input_dir} inside {workspace})"
        )
    if max_bytes <= 0:
        raise InputError(f"--max-bytes must be positive (got {max_bytes})")

    entries = sorted(input_dir.iterdir(), key=lambda p: p.name)
    prompt_seen = False
    total = 0
    for entry in entries:
        if entry.is_dir():
            raise InputError(
                f"unexpected subdirectory '{entry.name}': input must be flat; "
                "directory cadenzas are nonrecursive, so nested files would be silently unsearched"
            )
        if not entry.is_file():
            raise InputError(f"unsupported non-regular input entry: '{entry.name}'")
        # Bound BEFORE allocating: reject on declared size before any read.
        size = entry.stat().st_size
        if total + size > max_bytes:
            raise InputError(
                f"input exceeds --max-bytes={max_bytes} at '{entry.name}'; "
                "shrink the input or raise the bound deliberately"
            )
        if not _stream_is_text(entry):
            raise InputError(
                f"unsupported binary input '{entry.name}': v1 searches plain text inputs only"
            )
        if entry.name == "prompt.md":
            prompt_seen = True
            content = entry.read_bytes()
            if not content.strip():
                raise InputError("prompt.md is empty; write the research request first")
        total += size

    if not prompt_seen:
        raise InputError("input directory must contain a nonempty prompt.md")

    snapshot = workspace / "input-snapshot"
    if snapshot.exists():
        shutil.rmtree(snapshot)
    snapshot.mkdir(parents=True)
    files: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for entry in entries:
        data = entry.read_bytes()
        target = snapshot / entry.name
        target.write_bytes(data)
        file_hash = _sha256_bytes(data)
        digest.update(entry.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        files.append({"name": entry.name, "bytes": len(data), "sha256": file_hash})

    # Fresh run identity: stale lane reports from earlier runs can never
    # satisfy this run because their run_id will no longer match.
    for stale in list(workspace.glob("findings-*.json")) + list(workspace.glob("findings-*.md")):
        stale.unlink()
    for stale_name in STALE_OUTPUTS:
        stale_path = workspace / stale_name
        if stale_path.exists():
            stale_path.unlink()

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "run_id": str(uuid.uuid4()),
        "started_at": _utc_now(),
        "input_dir": str(input_dir),
        "input_sha256": digest.hexdigest(),
        "max_input_bytes": max_bytes,
        "files": files,
    }
    _write_json(workspace / "run-receipt.json", receipt)
    print(f"prepared {len(files)} input file(s); run_id={receipt['run_id']}")
    return EXIT_OK


# ---------------------------------------------------------------- validate


def _validate_findings(payload: dict[str, Any], label: str, receipt: dict[str, Any] | None, lane: int) -> None:
    _require(payload.get("schema_version") == SCHEMA_VERSION, f"{label}: unsupported schema_version")
    _require(payload.get("kind") == FINDINGS_KIND, f"{label}: kind must be {FINDINGS_KIND}")

    if receipt is not None:
        reported = payload.get("run_id")
        _require(
            reported == receipt.get("run_id"),
            f"{label}: run_id {reported!r} does not match this run's receipt "
            f"({receipt.get('run_id')!r}); report is stale or from another run",
        )
    else:
        _nonempty_str(payload, "run_id", label)

    reported_lane = payload.get("lane")
    _require(isinstance(reported_lane, int), f"{label}: 'lane' must be an integer")
    _require(reported_lane == lane, f"{label}: declared lane {reported_lane} != expected lane {lane}")

    status = payload.get("status")
    _require(status in STATUSES, f"{label}: status must be one of {STATUSES}, got {status!r}")
    _nonempty_str(payload, "summary", label)

    findings = payload.get("findings")
    _require(isinstance(findings, list), f"{label}: 'findings' must be a list")

    queries = payload.get("queries")
    _require(isinstance(queries, list), f"{label}: 'queries' must be a list")

    gaps = payload.get("gaps")
    _require(isinstance(gaps, list), f"{label}: 'gaps' must be a list")

    if status == "no_web":
        tool_evidence = payload.get("tool_evidence")
        _require(
            isinstance(tool_evidence, dict) and str(tool_evidence.get("notes", "")).strip(),
            f"{label}: no_web requires tool_evidence naming the unavailable/denied/failed tool",
        )
        _require(not findings, f"{label}: no_web must return no verified candidate claims (findings must be empty)")
    else:
        _require(bool(queries), f"{label}: complete/degraded must record the queries actually issued")
        for index, query in enumerate(queries):
            _require(
                isinstance(query, dict) and str(query.get("query", "")).strip(),
                f"{label}: queries[{index}] must carry a nonempty 'query' string",
            )
        if status == "degraded":
            _nonempty_str(payload, "degraded_reason", label)
        _require(bool(gaps), f"{label}: record material gaps explicitly (nonempty 'gaps')")

    recommendation = payload.get("recommendation")
    _require(isinstance(recommendation, dict), f"{label}: 'recommendation' object is required")
    mode = recommendation.get("mode")
    allowed_modes = ("reuse", "adapt", "build", "undetermined")
    _require(mode in allowed_modes, f"{label}: recommendation.mode must be one of {allowed_modes}")
    if status == "no_web":
        _require(mode == "undetermined", f"{label}: no_web cannot claim a reuse/adapt/build recommendation")
    else:
        if not findings:
            # Honest evidenced zero-match: coverage was recorded, the gap is
            # explicit, and no candidate is claimed — never fabricate one and
            # never mislabel this as no_web.
            _require(
                mode == "undetermined",
                f"{label}: zero-match {status} must use recommendation.mode 'undetermined', got {mode!r}",
            )
            _nonempty_str(recommendation, "reasoning", f"{label}.recommendation")
        else:
            _nonempty_str(recommendation, "reasoning", f"{label}.recommendation")

    for index, finding in enumerate(findings):
        item_label = f"{label}.findings[{index}]"
        _require(isinstance(finding, dict), f"{item_label} must be an object")
        url = _nonempty_str(finding, "url", item_label)
        _require(bool(URL_RE.match(url)), f"{item_label}: url must be an absolute http(s) URL")
        host = url.split("/", 3)[2].lower() if "://" in url else ""
        _require(host not in PLACEHOLDER_HOSTS, f"{item_label}: placeholder host '{host}' is not evidence")
        _nonempty_str(finding, "title", item_label)
        accessed = _nonempty_str(finding, "accessed", item_label)
        _require(bool(DATE_RE.match(accessed)), f"{item_label}: accessed must be YYYY-MM-DD (retrieval date)")
        claims = finding.get("claims")
        _require(
            isinstance(claims, list) and bool(claims),
            f"{item_label}: claims must be a nonempty list of supported claims",
        )
        for claim_index, claim in enumerate(claims):
            _require(
                isinstance(claim, str) and claim.strip().lower() not in PLACEHOLDER_VALUES,
                f"{item_label}.claims[{claim_index}] is empty or placeholder",
            )
        for field in ("integration", "constraints"):
            value = finding.get(field)
            _require(
                isinstance(value, str) and value.strip(),
                f"{item_label}: field '{field}' must state the integration path or an explicit unknown",
            )


def cmd_validate_report(args: argparse.Namespace) -> int:
    report_path = Path(args.file)
    if not report_path.is_file():
        raise ReportError(f"lane report not found: {report_path}")
    payload = _read_json(report_path)
    receipt = None
    if args.receipt:
        receipt_path = Path(args.receipt)
        if not receipt_path.is_file():
            raise ReportError(f"run receipt not found: {receipt_path}")
        receipt = _read_json(receipt_path)
        if receipt.get("kind") != RECEIPT_KIND:
            raise ReportError(f"{receipt_path.name}: not a {RECEIPT_KIND}")
    _validate_findings(payload, report_path.name, receipt, int(args.lane))
    print(f"{report_path.name}: valid ({payload.get('status')})")
    return EXIT_OK


# ------------------------------------------------------------------ collect


def cmd_collect(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    lanes = int(args.lanes)
    if lanes <= 0:
        raise InputError(f"--lanes must be positive (got {lanes})")
    receipt_path = workspace / "run-receipt.json"
    if not receipt_path.is_file():
        raise ReportError("run-receipt.json missing; run the prepare stage first")
    receipt = _read_json(receipt_path)
    if receipt.get("kind") != RECEIPT_KIND:
        raise ReportError("run-receipt.json: not a marianne-search-run-receipt")

    lanes_out: dict[str, Any] = {}
    statuses: list[str] = []
    for lane in range(1, lanes + 1):
        report_path = workspace / f"findings-{lane}.json"
        if not report_path.is_file():
            raise ReportError(
                f"findings-{lane}.json missing: lane {lane} did not deliver its declared report"
            )
        payload = _read_json(report_path)
        _validate_findings(payload, report_path.name, receipt, lane)
        lanes_out[str(lane)] = {
            "status": payload["status"],
            "summary": payload["summary"],
            "degraded_reason": payload.get("degraded_reason", ""),
            "tool_evidence": payload.get("tool_evidence", {}),
            "queries": payload["queries"],
            "findings": payload["findings"],
            "gaps": payload["gaps"],
            "recommendation": payload["recommendation"],
        }
        statuses.append(payload["status"])

    if "no_web" in statuses:
        overall = "no_web"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "complete"

    results = {
        "schema_version": SCHEMA_VERSION,
        "kind": RESULTS_KIND,
        "run_id": receipt["run_id"],
        "input_dir": receipt["input_dir"],
        "input_sha256": receipt["input_sha256"],
        "lane_count": lanes,
        "overall": overall,
        "lanes": lanes_out,
        "collected_at": _utc_now(),
    }
    _write_json(workspace / "results.json", results)
    (workspace / "results.md").write_text(_render_markdown(results), encoding="utf-8")
    print(f"collected {lanes} lane report(s); overall={overall}")
    return EXIT_OK


def _render_markdown(results: dict[str, Any]) -> str:
    lines = [
        "# Marianne Search Results",
        "",
        f"- Run: `{results['run_id']}`",
        f"- Input: `{results['input_dir']}` (sha256 `{results['input_sha256'][:16]}…`)",
        f"- Overall status: **{results['overall']}**",
        "",
        "> Collection of independent lane reports, not a consensus synthesis.",
        "> Search snippets are leads; cited pages are the evidence.",
        "",
    ]
    for lane in sorted(results["lanes"], key=int):
        data = results["lanes"][lane]
        lines.append(f"## Lane {lane} — {data['status']}")
        lines.append("")
        lines.append(data["summary"])
        lines.append("")
        if data["status"] == "no_web":
            evidence = data.get("tool_evidence") or {}
            lines.append(f"- Web unavailable: {evidence.get('notes', '(no detail recorded)')}")
            lines.append("- No verified candidate claims are reported.")
        elif data["status"] == "degraded":
            lines.append(f"- Degraded reason: {data.get('degraded_reason', '')}")
        if data["queries"]:
            lines.append("")
            lines.append("### Coverage (queries issued)")
            lines.append("")
            for query in data["queries"]:
                lines.append(f"- `{query.get('query', '')}`")
        if data["findings"]:
            lines.append("")
            lines.append("### Findings")
            lines.append("")
            for finding in data["findings"]:
                lines.append(f"- [{finding.get('title', '')}]({finding.get('url', '')}) (accessed {finding.get('accessed', '')})")
                for claim in finding.get("claims", []):
                    lines.append(f"  - {claim}")
                integration = finding.get("integration", "")
                constraints = finding.get("constraints", "")
                if integration:
                    lines.append(f"  - Integration: {integration}")
                if constraints:
                    lines.append(f"  - Constraints: {constraints}")
        if data["gaps"]:
            lines.append("")
            lines.append("### Gaps")
            lines.append("")
            for gap in data["gaps"]:
                lines.append(f"- {gap}")
        recommendation = data.get("recommendation") or {}
        if recommendation:
            lines.append("")
            lines.append(f"### Recommendation — {recommendation.get('mode', 'undetermined')}")
            lines.append("")
            lines.append(recommendation.get("reasoning", ""))
        lines.append("")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare", help="validate + snapshot inputs, write run receipt")
    prep.add_argument("--input-dir", required=True)
    prep.add_argument("--workspace", required=True)
    prep.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_INPUT_BYTES)

    check = sub.add_parser("validate-report", help="validate one lane findings JSON")
    check.add_argument("--file", required=True)
    check.add_argument("--lane", type=int, required=True)
    check.add_argument("--receipt", default="")

    collect = sub.add_parser("collect", help="validate all lanes and render results")
    collect.add_argument("--workspace", required=True)
    collect.add_argument("--lanes", type=int, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            return cmd_prepare(args)
        if args.command == "validate-report":
            return cmd_validate_report(args)
        return cmd_collect(args)
    except InputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except ReportError as exc:
        print(f"report error: {exc}", file=sys.stderr)
        return EXIT_BAD_REPORT


if __name__ == "__main__":
    sys.exit(main())
