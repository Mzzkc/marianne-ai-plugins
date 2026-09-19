#!/usr/bin/env python3
"""Relocatable entry point for the automatic model/profile refresh score."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refresh_scope import build_scope


def _ensure_private_directory(path: Path) -> None:
    """Create a private directory chain without chmodding existing parents."""
    path = path.absolute()
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        if current.parent == current:
            break
        current = current.parent
    if current.exists() and (not current.is_dir() or current.is_symlink()):
        raise ValueError(f"private directory ancestor is not a real directory: {current}")
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)
        directory.chmod(0o700)
    path.chmod(0o700)


def _write_private_text(path: Path, value: str) -> None:
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


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


def _write_authority(path: Path, transaction_id: str, project_root: Path, providers: list[str] | None = None, runtime_paths: list[Path] | None = None) -> str:
    data = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "allowed_roots": [str(root) for root in _authority_roots(project_root)],
        "refresh_scope": build_scope(project_root, _authority_roots(project_root), providers),
        "runtime_paths": [str(path.resolve()) for path in (runtime_paths or [])],
    }
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    _write_private_text(path, payload)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _materialize_runtime_score(source: Path, output: Path, workspace: Path) -> None:
    score = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(score, dict):
        raise ValueError(f"score must be a mapping: {source}")
    _ensure_private_directory(workspace)
    score["workspace"] = str(workspace)
    _write_private_text(output, yaml.safe_dump(score, sort_keys=False))


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
    parser.add_argument("--wait-timeout", type=float, default=3600,
                        help="Maximum seconds to observe; timeout preserves the job and technique")
    parser.add_argument("--poll-interval", type=float, default=5)
    parser.add_argument("--resume-workspace", type=Path,
                        help="Resume observation/cleanup of an existing transaction; never resubmits")
    return parser


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def _run_json(cmd: list[str], timeout: float) -> tuple[int, dict]:
    result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=timeout)
    try:
        data = json.loads(result.stdout)
    except (ValueError, TypeError):
        data = {}
    return result.returncode, data if isinstance(data, dict) else {}


def _observe(state: dict, timeout: float, interval: float) -> dict | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            code, status = _run_json(
                ["mzt", "status", state["job_id"], "--json"],
                min(30, max(0.01, deadline - time.monotonic())),
            )
        except (OSError, subprocess.TimeoutExpired):
            code, status = 1, {}
        if code == 0 and status.get("job_id") == state["job_id"]:
            phase = status.get("status")
            sheets = status.get("sheets")
            # A failed job may still have an executing sibling. Never restore
            # beneath it. The detailed status contract supplies a sheets map.
            # Native cancellation publishes CANCELLED before async teardown and
            # normalizes active sheet states to cancelled. It is not quiescence
            # evidence; retain the transaction for explicit settled recovery.
            if phase == "cancelled":
                return None
            if phase in {"completed", "failed"} and isinstance(sheets, dict):
                active = any(item.get("status") in {"dispatched", "in_progress", "running"}
                             for item in sheets.values())
                if not active:
                    return status
            if phase in {"paused", "paused_at_chain"}:
                return None
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
    return None


def _finish(state: dict, workspace: Path, runtime: dict) -> int:
    """Read transaction truth; compensate once only after a quiescent terminal job."""
    bundle = Path(state["bundle_root"])
    transaction_id = state["transaction_id"]
    helper = [sys.executable, str(bundle / "scripts" / "refreshctl.py")]
    bound = ["--authority-roots", state["authority_path"],
             "--authority-sha256", state["authority_sha256"],
             "--transaction-id", transaction_id]
    receipt_path = workspace / "receipt.json"
    transaction = None
    for path in (receipt_path, workspace / "transaction.json"):
        if path.is_file():
            try:
                candidate = _read_json(path)
            except (ValueError, OSError):
                continue
            if candidate.get("transaction_id") == transaction_id and candidate.get("transaction_status") in {
                "success", "partial", "rolled_back", "compensation_failed", "failed_before_backup", "incomplete"
            }:
                transaction = candidate
                break
    if transaction is None:
        backup_state = Path(state["backup_root"]) / "backup" / "transaction-state.json"
        marker = workspace / "runner-compensation.json"
        restored = False
        attempted = backup_state.is_file()
        # The marker is written before invoking restore: interruption must not
        # silently launch a second restore over a potentially changed subject.
        if attempted:
            try:
                fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                restored = _read_json(marker).get("state") == "restored"
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump({"transaction_id": transaction_id, "state": "started"}, handle)
                    handle.flush()
                    os.fsync(handle.fileno())
                result = subprocess.run(helper + ["restore", str(backup_state), "--manifest",
                                        str(workspace / "update-manifest.json")] + bound, check=False)
                restored = result.returncode == 0
                _write_private_text(marker, json.dumps({"transaction_id": transaction_id,
                                                       "state": "restored" if restored else "failed"}))
        transaction = {"transaction_id": transaction_id, "live_state": "not_attempted",
                       "restored": restored, "runtime_status": runtime["status"],
                       "transaction_status": "rolled_back" if restored else
                       "compensation_failed" if attempted else "failed_before_backup"}
    # Recover delivery after a finalizer succeeded but its receipt sheet failed.
    if not receipt_path.is_file():
        receipt_input = workspace / "receipt-input.json"
        _write_private_text(receipt_input, json.dumps(transaction, indent=2) + "\n")
        subprocess.run(helper + ["receipt", str(receipt_input), str(receipt_path),
                                str(workspace / "receipt.md")], check=False)
    try:
        receipt = _read_json(receipt_path)
    except (OSError, ValueError):
        receipt = {}
    if (runtime.get("status") == "completed" and receipt.get("transaction_id") == transaction_id
            and receipt.get("transaction_status") == "partial"):
        return 3
    return 0 if (runtime["status"] == "completed"
                 and receipt.get("transaction_id") == transaction_id
                 and receipt.get("transaction_status") == "success") else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if any(not math.isfinite(value) or value <= 0 for value in (args.wait_timeout, args.poll_interval)):
        raise SystemExit("wait timeout and poll interval must be finite and positive")
    bundle = Path(__file__).resolve().parent.parent
    if args.resume_workspace:
        workspace_root = args.resume_workspace.expanduser().resolve()
        state = _read_json(workspace_root / "runner-state.json")
        if not state.get("job_id"):
            raise SystemExit("submission outcome unknown; reconcile the job before setting job_id in runner-state.json")
    else:
        request_path = (args.request_path or bundle / "request.md").expanduser().resolve()
        project_root = args.project_root.expanduser().resolve()
        transaction_id = new_transaction_id()
        workspace_root = args.workspace_root.expanduser().resolve() / transaction_id
        backup_root = args.backup_root.expanduser().resolve() / transaction_id
        if not request_path.is_file() or not project_root.is_dir():
            raise SystemExit("request file and project directory must exist")
        _ensure_private_directory(workspace_root)
        _ensure_private_directory(backup_root)
        authority_path = workspace_root / "authority-roots.json"
        authority_sha256 = _write_authority(authority_path, transaction_id, project_root, runtime_paths=[workspace_root, backup_root])
        runtime_score = workspace_root / f"model-profile-refresh-{transaction_id}.yaml"
        _materialize_runtime_score(bundle / "model-profile-refresh.yaml", runtime_score,
                                   workspace_root / "marianne-workspace")
        recovery = backup_root / "technique-recovery"
        state = {"transaction_id": transaction_id, "bundle_root": str(bundle),
                 "backup_root": str(backup_root), "authority_path": str(authority_path),
                 "authority_sha256": authority_sha256,
                 "technique_state": str(recovery / "technique-state.json"), "job_id": None}
        _write_private_text(workspace_root / "runner-state.json", json.dumps(state, indent=2) + "\n")
        installed = subprocess.run([sys.executable, str(bundle / "scripts" / "refreshctl.py"),
                                   "install-temporary-technique", str(bundle / "technique" / "SKILL.md"),
                                   str(recovery), "--transaction-id", transaction_id], check=False)
        if installed.returncode:
            return _restore_technique(state, installed.returncode)
        raw_variables = {"request_path": str(request_path), "bundle_root": str(bundle),
                         "project_root": str(project_root), "refresh_artifact_root": str(workspace_root),
                         "backup_root": str(backup_root), "authority_roots": str(authority_path),
                         "authority_sha256": authority_sha256, "transaction_id": transaction_id}
        variables = {**raw_variables, **{f"{name}_q": shlex.quote(value)
                                        for name, value in raw_variables.items()}}
        # Persist bindings in the exact submitted YAML as well as CLI variables.
        # Native resume may reload the score without the submitting process.
        bound_score = yaml.safe_load(runtime_score.read_text(encoding="utf-8"))
        bound_score["prompt"]["variables"].update(variables)
        _write_private_text(runtime_score, yaml.safe_dump(bound_score, sort_keys=False))
        cmd = ["mzt", "run", str(runtime_score), "--fresh", "--json"]
        for name, value in variables.items():
            cmd.extend(["--var", f"{name}={value}"])
        try:
            code, submitted = _run_json(cmd, 60)
            reported_id = submitted.get("job_id")
            submission_status = submitted.get("status")
            state["submission"] = {"exit_code": code, "status": submission_status,
                                   "reported_job_id": reported_id}
            if code == 0 and submission_status in {"accepted", "pending"} and isinstance(reported_id, str) and reported_id.strip():
                state["job_id"] = reported_id
            elif submission_status == "rejected":
                # Native rejection may return another existing job's ID. Never
                # adopt or observe it as this transaction's accepted execution.
                _write_private_text(workspace_root / "runner-state.json", json.dumps(state, indent=2) + "\n")
                return _restore_technique(state, code or 1)
            # Malformed/contradictory responses remain unresolved: a timeout or
            # transport failure can occur after server acceptance.
        except FileNotFoundError:
            return _restore_technique(state, 127)
        except (OSError, subprocess.TimeoutExpired, KeyboardInterrupt):
            pass  # Acceptance may have happened; preserve until reconciled.
        _write_private_text(workspace_root / "runner-state.json", json.dumps(state, indent=2) + "\n")
    try:
        terminal = _observe(state, args.wait_timeout, args.poll_interval) if state.get("job_id") else None
    except KeyboardInterrupt:
        terminal = None
    if terminal is None:
        print(f"Refresh is unresolved; job={state.get('job_id')!r}. Technique and backup retained. "
              f"Resume with --resume-workspace {shlex.quote(str(workspace_root))}", file=sys.stderr)
        return 2
    try:
        result = _finish(state, workspace_root, terminal)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Refresh finalization failed: {exc}; recovery state: {workspace_root}", file=sys.stderr)
        result = 1
    return _restore_technique(state, result)


def _restore_technique(state: dict, result: int) -> int:
    technique_state = Path(state["technique_state"])
    if technique_state.is_file():
        restored = subprocess.run([sys.executable, str(Path(state["bundle_root"]) / "scripts" / "refreshctl.py"),
                                   "restore-temporary-technique", str(technique_state),
                                   "--transaction-id", state["transaction_id"]], check=False)
        if restored.returncode and result == 0:
            return restored.returncode
    return result


if __name__ == "__main__":
    raise SystemExit(main())
