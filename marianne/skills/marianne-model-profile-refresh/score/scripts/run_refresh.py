#!/usr/bin/env python3
"""Relocatable entry point for the automatic model/profile refresh score."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import uuid

import yaml


def _default_backup_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path.home() / ".marianne" / "backups" / "model-profile-refresh" / stamp


def new_transaction_id() -> str:
    """Return an unguessable identifier suitable for path and contract binding."""
    return "txn-" + uuid.uuid4().hex


def _authority_roots(project_root: Path) -> list[Path]:
    """Return the caller-owned, bounded set of roots this run may mutate."""
    home = Path.home().resolve()
    candidates = [
        project_root,
        home / ".marianne",
        home / ".claude",
        home / ".codex",
        home / ".gemini",
        home / ".config" / "opencode",
        home / ".config" / "antigravity",
    ]
    return sorted({candidate.resolve() for candidate in candidates if candidate.is_dir()}, key=str)


def _write_authority(path: Path, transaction_id: str, project_root: Path) -> str:
    data = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "allowed_roots": [str(root) for root in _authority_roots(project_root)],
    }
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _materialize_runtime_score(source: Path, output: Path, workspace: Path) -> None:
    score = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(score, dict):
        raise ValueError(f"score must be a mapping: {source}")
    workspace.mkdir(parents=True, exist_ok=True)
    score["workspace"] = str(workspace)
    output.write_text(yaml.safe_dump(score, sort_keys=False), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request-path", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.home() / ".marianne" / "workspaces" / "model-profile-refresh",
    )
    parser.add_argument("--backup-root", type=Path, default=_default_backup_root())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script_dir = Path(__file__).resolve().parent
    bundle = script_dir.parent
    request_path = (args.request_path or bundle / "request.md").expanduser().resolve()
    project_root = args.project_root.expanduser().resolve()
    workspace_base = args.workspace_root.expanduser().resolve()
    backup_base = args.backup_root.expanduser().resolve()
    transaction_id = new_transaction_id()
    workspace_root = workspace_base / transaction_id
    backup_root = backup_base / transaction_id

    if not request_path.is_file():
        raise SystemExit(f"request file does not exist: {request_path}")
    if not project_root.is_dir():
        raise SystemExit(f"project root does not exist: {project_root}")
    workspace_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)

    authority_path = workspace_root / "authority-roots.json"
    authority_sha256 = _write_authority(authority_path, transaction_id, project_root)
    runtime_score = workspace_root / "model-profile-refresh.runtime.yaml"
    _materialize_runtime_score(
        bundle / "model-profile-refresh.yaml",
        runtime_score,
        workspace_root / "marianne-workspace",
    )

    install_cmd = [
        sys.executable,
        str(bundle / "scripts" / "refreshctl.py"),
        "install-technique",
        str(bundle / "technique" / "SKILL.md"),
    ]
    installed = subprocess.run(install_cmd, check=False)
    if installed.returncode != 0:
        return installed.returncode

    raw_variables = {
        "request_path": str(request_path),
        "bundle_root": str(bundle),
        "project_root": str(project_root),
        "workspace_root": str(workspace_root),
        "backup_root": str(backup_root),
        "authority_roots": str(authority_path),
        "authority_sha256": authority_sha256,
        "transaction_id": transaction_id,
    }
    variables = {
        **raw_variables,
        **{f"{name}_q": shlex.quote(value) for name, value in raw_variables.items()},
    }
    cmd = ["mzt", "run", str(runtime_score), "--fresh"]
    for name, value in variables.items():
        cmd.extend(["--var", f"{name}={value}"])
    completed = subprocess.run(cmd, check=False)

    # A conductor/instrument failure can occur before the score's ordered
    # finalize sheet. If mutation has begun, compensate here without changing
    # the exact mzt exit code observed by the caller.
    backup_index = backup_root / "backup" / "index.json"
    if completed.returncode != 0:
        restored = False
        attempted_restore = backup_index.is_file()
        if attempted_restore:
            restore = subprocess.run(
                [
                    sys.executable,
                    str(bundle / "scripts" / "refreshctl.py"),
                    "restore",
                    str(backup_index),
                ],
                check=False,
            )
            restored = restore.returncode == 0
        if not (workspace_root / "receipt.json").is_file():
            receipt_input = workspace_root / "receipt-input.json"
            receipt_input.write_text(
                json.dumps(
                    {
                        "live_state": "not_attempted",
                        "mzt_exit_code": completed.returncode,
                        "restored": restored,
                        "transaction_id": transaction_id,
                        "transaction_status": (
                            "rolled_back"
                            if restored
                            else "compensation_failed"
                            if attempted_restore
                            else "failed_before_backup"
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(bundle / "scripts" / "refreshctl.py"),
                    "receipt",
                    str(receipt_input),
                    str(workspace_root / "receipt.json"),
                    str(workspace_root / "receipt.md"),
                ],
                check=False,
            )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
