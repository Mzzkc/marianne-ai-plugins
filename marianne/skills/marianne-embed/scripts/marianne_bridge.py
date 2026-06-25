#!/usr/bin/env python3
"""JSON bridge for embedding Marianne behind another app or agent.

Protocol:
  python marianne_bridge.py <command> < payload.json

Output is always JSON on stdout. Marianne's import/runtime logs are redirected
to stderr so host applications can parse stdout without log filtering.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


@contextlib.contextmanager
def redirect_stdout_to_stderr():
    """Redirect Python and fd-level stdout to stderr inside the block."""
    sys.stdout.flush()
    saved_stdout = os.dup(1)
    try:
        os.dup2(2, 1)
        with contextlib.redirect_stdout(sys.stderr):
            yield
    finally:
        sys.stdout.flush()
        os.dup2(saved_stdout, 1)
        os.close(saved_stdout)


def configure_import_path(marianne_root: str | None) -> None:
    root_value = marianne_root or os.environ.get("MARIANNE_ROOT")
    if not root_value:
        return
    root = Path(root_value).expanduser().resolve()
    src = root / "src"
    if (src / "marianne").is_dir():
        sys.path.insert(0, str(src))
    elif (root / "marianne").is_dir():
        sys.path.insert(0, str(root))


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("payload must be a JSON object")
    return value


def as_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): as_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [as_jsonable(v) for v in value]
    return value


def clean_runtime_variables(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for key, raw in value.items():
        key = str(key)
        if not key.replace("_", "a").isalnum() or not (key[0].isalpha() or key[0] == "_"):
            continue
        if raw is None:
            continue
        out[key] = str(raw)
    return out


def make_client(payload: dict[str, Any]):
    from marianne.daemon.detect import _resolve_socket_path
    from marianne.daemon.ipc.client import DaemonClient

    socket_path = payload.get("socket_path")
    timeout = float(payload.get("timeout", 30))
    return DaemonClient(_resolve_socket_path(socket_path), timeout=timeout)


async def daemon_status(payload: dict[str, Any]) -> dict[str, Any]:
    from marianne.daemon.exceptions import DaemonNotRunningError

    client = make_client(payload)
    try:
        status = await client.status()
        return {"ok": True, "connected": True, **as_jsonable(status)}
    except DaemonNotRunningError as exc:
        return {"ok": True, "connected": False, "message": str(exc)}


async def list_jobs(payload: dict[str, Any]) -> dict[str, Any]:
    jobs = await make_client(payload).list_jobs()
    limit = int(payload.get("limit") or 100)
    return {"ok": True, "jobs": jobs[:limit], "total": len(jobs)}


async def job_status(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = str(payload["job_id"])
    workspace = str(payload.get("workspace") or "")
    result = await make_client(payload).get_job_status(job_id, workspace)
    return {"ok": True, "job": as_jsonable(result)}


async def submit_job(payload: dict[str, Any]) -> dict[str, Any]:
    from marianne.daemon.types import JobRequest

    config_path = Path(str(payload["config_path"])).expanduser().resolve()
    workspace = payload.get("workspace")
    client_cwd = payload.get("client_cwd")
    request = JobRequest(
        config_path=config_path,
        workspace=Path(str(workspace)).expanduser().resolve() if workspace else None,
        fresh=bool(payload.get("fresh", False)),
        dry_run=bool(payload.get("dry_run", False)),
        self_healing=bool(payload.get("self_healing", False)),
        self_healing_auto_confirm=bool(payload.get("self_healing_auto_confirm", False)),
        escalation=bool(payload.get("escalation", False)),
        start_sheet=int(payload["start_sheet"]) if payload.get("start_sheet") else None,
        chain_depth=int(payload["chain_depth"]) if payload.get("chain_depth") else None,
        client_cwd=Path(str(client_cwd)).expanduser().resolve() if client_cwd else None,
        runtime_variables=clean_runtime_variables(payload.get("runtime_variables") or {}),
    )
    response = await make_client(payload).submit_job(request)
    data = as_jsonable(response)
    accepted = data.get("status") in {"accepted", "pending"}
    result = {"ok": accepted, "submit": data}
    if not accepted:
        result["error"] = data.get("message") or f"submit status={data.get('status')}"
    return result


async def action_job(payload: dict[str, Any], action: str) -> dict[str, Any]:
    client = make_client(payload)
    job_id = str(payload["job_id"])
    workspace = str(payload.get("workspace") or "")
    if action == "pause":
        result = await client.pause_job(job_id, workspace)
    elif action == "resume":
        result = await client.resume_job(job_id, workspace)
    elif action == "cancel":
        result = await client.cancel_job(job_id, workspace)
    else:
        raise ValueError(f"unknown job action: {action}")
    return {"ok": True, "action": action, "job_id": job_id, "result": as_jsonable(result)}


def validate_score(payload: dict[str, Any]) -> dict[str, Any]:
    from pydantic import ValidationError

    from marianne.core.config import JobConfig

    if payload.get("content") is not None:
        content = str(payload["content"])
        filename = str(payload.get("filename") or "score.yaml")
    else:
        path = Path(str(payload["path"])).expanduser().resolve()
        content = path.read_text()
        filename = path.name

    try:
        config = JobConfig.from_yaml_string(content)
    except ValidationError as exc:
        return {
            "ok": True,
            "valid": False,
            "issues": [{"severity": "ERROR", "check_id": "SCHEMA", "message": str(exc)}],
            "counts": {"ERROR": 1, "WARNING": 0, "INFO": 0},
        }
    except Exception as exc:
        return {
            "ok": True,
            "valid": False,
            "issues": [{"severity": "ERROR", "check_id": "LOAD", "message": str(exc)}],
            "counts": {"ERROR": 1, "WARNING": 0, "INFO": 0},
        }

    issues: list[dict[str, Any]] = []
    try:
        from marianne.dashboard.routes.scores import run_extended_validation

        workspace_path = payload.get("workspace_path")
        issues = [
            as_jsonable(issue)
            for issue in run_extended_validation(
                config,
                content,
                filename,
                str(workspace_path) if workspace_path else None,
            )
        ]
    except Exception as exc:
        issues.append({
            "severity": "INFO",
            "check_id": "EXTENDED_VALIDATION_UNAVAILABLE",
            "message": str(exc),
        })

    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for issue in issues:
        severity = str(issue.get("severity", "INFO")).upper()
        if severity in counts:
            counts[severity] += 1

    return {
        "ok": True,
        "valid": counts["ERROR"] == 0,
        "issues": issues,
        "counts": counts,
        "config_summary": {
            "name": config.name,
            "workspace": str(config.workspace),
            "total_sheets": config.sheet.total_sheets,
            "instrument": config.effective_instrument_name,
            "validation_count": len(config.validations),
        },
    }


def start_conductor(payload: dict[str, Any]) -> dict[str, Any]:
    mzt_bin = payload.get("mzt_bin") or os.environ.get("MZT_BIN") or "mzt"
    args = [str(mzt_bin), "start"]
    if payload.get("foreground"):
        args.append("--foreground")
    if payload.get("profile"):
        args.extend(["--profile", str(payload["profile"])])
    timeout = float(payload.get("timeout", 30))
    completed = subprocess.run(
        args,
        cwd=str(payload.get("cwd") or os.getcwd()),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


async def dispatch(command: str, payload: dict[str, Any]) -> dict[str, Any]:
    if command == "daemon_status":
        return await daemon_status(payload)
    if command == "list_jobs":
        return await list_jobs(payload)
    if command == "job_status":
        return await job_status(payload)
    if command == "submit_job":
        return await submit_job(payload)
    if command in {"pause", "resume", "cancel"}:
        return await action_job(payload, command)
    if command == "validate_score":
        return validate_score(payload)
    if command == "start_conductor":
        return start_conductor(payload)
    raise ValueError(f"unknown command: {command}")


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--marianne-root")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    configure_import_path(args.marianne_root)
    payload = read_payload()

    with redirect_stdout_to_stderr():
        result = await dispatch(args.command, payload)

    print(json.dumps(result, indent=2 if args.pretty else None, default=str))
    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }))
        raise SystemExit(1)
