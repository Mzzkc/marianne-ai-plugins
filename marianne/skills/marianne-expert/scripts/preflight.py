#!/usr/bin/env python3
"""Report Marianne Expert session access without inferring authorization."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Any


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_state(repo: Path) -> dict[str, Any] | None:
    root_result = _run(["git", "rev-parse", "--show-toplevel"], repo)
    if root_result.returncode != 0:
        return None
    root = Path(root_result.stdout.strip()).resolve()
    head = _run(["git", "rev-parse", "HEAD"], root)
    branch = _run(["git", "branch", "--show-current"], root)
    status = _run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"], root
    )
    dirty: list[dict[str, Any]] = []
    for line in status.stdout.splitlines():
        if len(line) < 4:
            continue
        raw_path = line[3:]
        path_text = raw_path.split(" -> ", 1)[-1].strip('"')
        path = root / path_text
        dirty.append(
            {
                "status": line[:2],
                "path": path_text,
                "sha256": _sha256(path),
            }
        )
    return {
        "root": str(root),
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "branch": branch.stdout.strip() if branch.returncode == 0 else None,
        "dirty": sorted(dirty, key=lambda entry: entry["path"]),
    }


def _conductor_available(mzt: str | None) -> bool:
    if not mzt:
        return False
    result = _run([mzt, "conductor-status"])
    return result.returncode == 0 and "running" in result.stdout.lower()


def _online_available(url: str) -> bool:
    try:
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=5) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def collect_capabilities(
    repo: Path | None,
    write_authorized: bool,
    probe_online: bool,
    runtime_context: str = "direct",
    official_url: str = "https://github.com/Mzzkc/marianne-ai-compose",
) -> dict[str, Any]:
    source_state = _git_state(repo.resolve()) if repo is not None else None
    mzt = shutil.which("mzt")
    skill_root = Path(__file__).resolve().parents[1]
    online: bool | None = _online_available(official_url) if probe_online else None
    return {
        "schema_version": 1,
        "capabilities": {
            "pinned_kit": (skill_root / "evidence" / "claims.jsonl").is_file(),
            "current_source_read": source_state is not None,
            "current_source_write_authorized": bool(write_authorized),
            "marianne_cli": mzt is not None,
            "conductor_ipc": _conductor_available(mzt),
            "marianne_harness": runtime_context == "marianne-score",
            "online_primary_sources": online,
        },
        "runtime_context": runtime_context,
        "source_state": source_state,
        "feature_status_source": str(
            skill_root / "evidence" / "implementation-status.json"
        ),
        "authorization_source": "explicit_cli_flag" if write_authorized else "not_granted",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--source-write-authorized", action="store_true")
    parser.add_argument("--probe-online", action="store_true")
    parser.add_argument(
        "--runtime-context", choices=("direct", "marianne-score"), default="direct"
    )
    parser.add_argument(
        "--official-url", default="https://github.com/Mzzkc/marianne-ai-compose"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = collect_capabilities(
        args.repo,
        args.source_write_authorized,
        args.probe_online,
        args.runtime_context,
        args.official_url,
    )
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
