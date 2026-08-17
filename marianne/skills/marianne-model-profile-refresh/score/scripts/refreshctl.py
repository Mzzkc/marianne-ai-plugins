#!/usr/bin/env python3
"""Deterministic, bounded transaction primitives for model/profile refreshes."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import tomllib
from typing import Any, Iterable

import yaml


CLASSIFICATIONS = {"active", "generated", "pinned", "frozen", "retired", "unknown"}
MUTABLE_CLASSIFICATIONS = {"active", "generated"}
LIVE_STATES = {"live_smoked", "unsupported", "unauthenticated", "not_attempted"}
SECRET_MARKERS = ("secret", "token", "password", "credential", "cookie", "private_key", "apikey", "api_key")
PUBLIC_METADATA_KEYS = {"max_output_tokens"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
CREDENTIAL_VALUE_PATTERNS = (
    re.compile(r"^AIza[0-9A-Za-z_-]{20,}$"),
    re.compile(r"^(?:sk|pk)_[A-Za-z0-9_-]{16,}$"),
    re.compile(r"^(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{20,}$"),
    re.compile(r"^github_pat_[A-Za-z0-9_]{20,}$"),
    re.compile(r"^AKIA[0-9A-Z]{16}$"),
    re.compile(r"^[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}$"),
)


@dataclass(frozen=True)
class BackupEntry:
    path: str
    kind: str
    sha256: str | None = None
    blob: str | None = None
    link_target: str | None = None
    mode: int | None = None
    uid: int | None = None
    gid: int | None = None
    mtime_ns: int | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_secret_key(key: object) -> bool:
    normalized = str(key).lower().replace("-", "_")
    if normalized in PUBLIC_METADATA_KEYS:
        return False
    return any(marker in normalized for marker in SECRET_MARKERS)


def _is_secret_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    candidate = value.strip()
    if not candidate or SHA256_PATTERN.fullmatch(candidate):
        return False
    if candidate.startswith(("http://", "https://")):
        return False
    if "secret-sentinel" in candidate.lower() or candidate.startswith("Bearer "):
        return True
    if any(pattern.fullmatch(candidate) for pattern in CREDENTIAL_VALUE_PATTERNS):
        return True
    environment_secrets = {
        env_value
        for env_name, env_value in os.environ.items()
        if _is_secret_key(env_name) and len(env_value) >= 8
    }
    return any(secret in candidate for secret in environment_secrets)


def redact(value: Any) -> Any:
    """Return a structural copy without credential-shaped values or secret keys."""
    if isinstance(value, dict):
        return {
            "[REDACTED]" if _is_secret_key(key) or _is_secret_value(str(key)) else str(key):
            "[REDACTED]" if _is_secret_key(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if _is_secret_value(value):
        return "[REDACTED]"
    return value


def _has_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_is_secret_key(key) or _has_secret_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_has_secret_key(item) for item in value)
    return False


def _contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolved_roots(data: dict[str, Any], errors: list[str]) -> list[Path]:
    roots = data.get("allowed_roots")
    if not isinstance(roots, list) or not roots:
        errors.append("allowed_roots must be a non-empty list")
        return []
    resolved: list[Path] = []
    for raw_root in roots:
        if not isinstance(raw_root, str) or not Path(raw_root).is_absolute():
            errors.append("allowed_roots entries must be absolute paths")
            continue
        resolved_root = Path(raw_root).resolve(strict=False)
        if raw_root != os.path.abspath(raw_root):
            errors.append("allowed_roots entries must use canonical absolute spelling")
        resolved.append(resolved_root)
    return resolved


def validate_manifest(data: dict) -> list[str]:
    """Validate update authority before any mutation is allowed."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("transaction_id"), str) or not data["transaction_id"].strip():
        errors.append("transaction_id must be a non-empty string")
    if not isinstance(data.get("request"), str) or not data["request"].strip():
        errors.append("request must be a non-empty string")
    mode = data.get("mode")
    if mode not in {"specific", "broad"}:
        errors.append("mode must be specific or broad")
    roots = _resolved_roots(data, errors)
    facts = data.get("facts")
    if not isinstance(facts, dict):
        errors.append("facts must be an object")
        facts = {}
    if mode == "broad" and not facts.get("evidence_urls"):
        errors.append("broad mode requires evidence_urls")
    if facts.get("model") == "gemini-3.7-flash":
        if facts.get("context_window") != 1_048_576:
            errors.append("gemini-3.7-flash context_window must be 1048576")
        if facts.get("max_output_tokens") != 65_536:
            errors.append("gemini-3.7-flash max_output_tokens must be 65536")
        levels = facts.get("thinking_levels")
        if not isinstance(levels, list) or set(levels) != {"low", "medium", "high"}:
            errors.append("gemini-3.7-flash thinking_levels must be low, medium, high (minimal is unsupported)")
    if _has_secret_key(data.get("report", {})):
        errors.append("manifest report fields must not contain secret-looking keys")
    if redact(data) != data:
        errors.append("public manifest contains a field or value that requires redaction")
    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("targets must be a non-empty list")
        return errors
    seen: set[Path] = set()
    for position, target in enumerate(targets):
        prefix = f"targets[{position}]"
        if not isinstance(target, dict):
            errors.append(f"{prefix} must be an object")
            continue
        raw_path = target.get("path")
        if not isinstance(raw_path, str) or not Path(raw_path).is_absolute():
            errors.append(f"{prefix}.path must be an absolute path")
            continue
        declared_path = Path(raw_path).absolute()
        resolved_path = declared_path.resolve(strict=False)
        if raw_path != os.path.abspath(raw_path):
            errors.append(f"{prefix}.path must use canonical absolute spelling")
        if resolved_path in seen:
            errors.append("duplicate target path")
        seen.add(resolved_path)
        if roots and not any(_contained(resolved_path, root) for root in roots):
            errors.append(f"{prefix}.path is outside allowed_roots")
        classification = target.get("classification")
        if classification not in CLASSIFICATIONS:
            errors.append(f"{prefix}.classification is not recognized")
        elif classification not in MUTABLE_CLASSIFICATIONS and not (
            classification in {"pinned", "frozen"} and target.get("explicitly_named") is True
        ):
            errors.append(f"{prefix} may not mutate {classification} without explicitly_named: true")
    return errors


def validate_manifest_authority(
    data: dict[str, Any],
    authority_path: Path,
    expected_authority_sha256: str,
    expected_transaction_id: str,
) -> list[str]:
    """Bind an AI-authored manifest to immutable caller-supplied authority."""
    errors = validate_manifest(data)
    try:
        if sha256_file(authority_path) != expected_authority_sha256:
            return errors + ["caller authority digest does not match"]
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"caller authority is invalid: {exc}"]
    if authority.get("schema_version") != 1:
        errors.append("caller authority schema_version must be 1")
    if authority.get("transaction_id") != expected_transaction_id:
        errors.append("caller authority transaction does not match runtime transaction")
    if data.get("transaction_id") != expected_transaction_id:
        errors.append("manifest transaction does not match runtime transaction")
    raw_roots = authority.get("allowed_roots")
    if not isinstance(raw_roots, list) or not raw_roots:
        errors.append("caller authority allowed_roots must be a non-empty list")
        return errors
    caller_roots: list[Path] = []
    for raw_root in raw_roots:
        if not isinstance(raw_root, str) or not Path(raw_root).is_absolute():
            errors.append("caller authority roots must be absolute paths")
            continue
        caller_roots.append(Path(raw_root).resolve(strict=False))
    manifest_roots = data.get("allowed_roots", [])
    if isinstance(manifest_roots, list):
        for raw_root in manifest_roots:
            if not isinstance(raw_root, str) or not Path(raw_root).is_absolute():
                continue
            root = Path(raw_root).resolve(strict=False)
            if caller_roots and not any(_contained(root, caller) for caller in caller_roots):
                errors.append(f"manifest root is outside caller authority: {root}")
    return errors


def _metadata(path: Path) -> dict[str, int]:
    details = path.lstat()
    return {
        "mode": stat.S_IMODE(details.st_mode),
        "uid": details.st_uid,
        "gid": details.st_gid,
        "mtime_ns": details.st_mtime_ns,
    }


def _snapshot(roots: Iterable[Path], excluded: Iterable[Path]) -> dict[str, dict[str, str]]:
    excluded_paths = [path.resolve(strict=False) for path in excluded]
    snapshot: dict[str, dict[str, str]] = {}
    for root in roots:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() or root.is_symlink() else root.rglob("*")
        for candidate in candidates:
            resolved = candidate.resolve(strict=False)
            if any(resolved == excluded_path or _contained(resolved, excluded_path) for excluded_path in excluded_paths):
                continue
            if candidate.is_dir() and not candidate.is_symlink():
                continue
            if candidate.is_symlink():
                snapshot[str(candidate.absolute())] = {"kind": "symlink", "value": os.readlink(candidate)}
            elif candidate.is_file():
                snapshot[str(candidate.absolute())] = {"kind": "file", "value": sha256_file(candidate)}
    return snapshot


def _atomic_write_bytes(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _atomic_write_json(destination: Path, value: Any) -> None:
    _atomic_write_bytes(destination, json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _capture_entries(paths: Iterable[Path], blobs: Path) -> list[BackupEntry]:
    blobs.mkdir(parents=True, exist_ok=True)
    entries: list[BackupEntry] = []
    for path in paths:
        if not path.exists() and not path.is_symlink():
            entries.append(BackupEntry(path=str(path), kind="absent"))
            continue
        if path.is_dir() and not path.is_symlink():
            raise ValueError(f"directory targets are not supported: {path}")
        metadata = _metadata(path)
        if path.is_symlink():
            entries.append(BackupEntry(path=str(path), kind="symlink", link_target=os.readlink(path), **metadata))
            continue
        digest = sha256_file(path)
        blob = blobs / digest
        if not blob.exists():
            shutil.copyfile(path, blob)
        entries.append(BackupEntry(path=str(path), kind="file", sha256=digest, blob=f"blobs/{digest}", **metadata))
    return entries


def _accepted_scope(data: dict[str, Any]) -> dict[str, list[Any]]:
    return {
        "roots": sorted({str(Path(root).resolve(strict=False)) for root in data["allowed_roots"]}),
        "targets": [
            list(target)
            for target in sorted(
                {
                (
                    str(Path(target["path"]).resolve(strict=False)),
                    target["classification"],
                    target.get("explicitly_named") is True,
                )
                for target in data["targets"]
                }
            )
        ],
    }


def create_backup(
    manifest_path: Path,
    backup_dir: Path,
    *,
    authority_path: Path | None = None,
    authority_sha256: str | None = None,
    transaction_id: str | None = None,
) -> dict:
    manifest_bytes = manifest_path.read_bytes()
    data = json.loads(manifest_bytes.decode("utf-8"))
    if authority_path is not None and authority_sha256 is not None and transaction_id is not None:
        errors = validate_manifest_authority(data, authority_path, authority_sha256, transaction_id)
    else:
        errors = validate_manifest(data)
    if errors:
        raise ValueError("invalid manifest: " + "; ".join(errors))
    backup_dir = backup_dir.absolute()
    entries = _capture_entries((Path(target["path"]) for target in data["targets"]), backup_dir / "blobs")
    roots = [Path(root).resolve(strict=False) for root in data["allowed_roots"]]
    index_path = backup_dir / "index.json"
    recovery_path = backup_dir / "recovery-index.json"
    recovery_index = {
        "schema_version": 1,
        "transaction_id": data["transaction_id"],
        "manifest_path": str(manifest_path.absolute()),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "accepted_scope": _accepted_scope(data),
        "entries": [asdict(entry) for entry in entries],
        "allowed_roots": [str(root) for root in roots],
        "excluded_paths": [str(backup_dir.resolve(strict=False))],
        "scope_snapshot": _snapshot(roots, [backup_dir]),
    }
    _atomic_write_json(recovery_path, recovery_index)
    report_index = redact(recovery_index)
    report_index["index_path"] = str(index_path)
    report_index["recovery_index"] = "recovery-index.json"
    report_index = redact(report_index)
    _atomic_write_json(index_path, report_index)
    return report_index


def _apply_metadata(path: Path, entry: dict[str, Any], *, follow_symlinks: bool = True) -> None:
    if follow_symlinks:
        os.chmod(path, entry["mode"])
    details = _metadata(path)
    if details["uid"] != entry["uid"] or details["gid"] != entry["gid"]:
        if not hasattr(os, "chown"):
            raise PermissionError("could not restore ownership: chown is unavailable")
        try:
            os.chown(path, entry["uid"], entry["gid"], follow_symlinks=follow_symlinks)
        except (PermissionError, NotImplementedError, OSError) as exc:
            after = _metadata(path)
            if after["uid"] != entry["uid"] or after["gid"] != entry["gid"]:
                raise PermissionError(f"could not restore ownership: {exc}") from exc
        after = _metadata(path)
        if after["uid"] != entry["uid"] or after["gid"] != entry["gid"]:
            raise PermissionError("could not restore ownership exactly")
    try:
        os.utime(path, ns=(entry["mtime_ns"], entry["mtime_ns"]), follow_symlinks=follow_symlinks)
    except (NotImplementedError, OSError) as exc:
        if _metadata(path)["mtime_ns"] != entry["mtime_ns"]:
            raise OSError(f"could not restore mtime exactly: {exc}") from exc


def _preflight_restore(index_path: Path, entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if entry["kind"] != "file":
            continue
        blob = index_path.parent / entry["blob"]
        if not blob.is_file() or sha256_file(blob) != entry["sha256"]:
            errors.append("corrupt backup blob")
    return errors


def _remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        raise IsADirectoryError(f"refusing to replace directory target: {path}")


def _restore_entry(path: Path, entry: dict[str, Any], blob_root: Path) -> str | None:
    if entry["kind"] == "absent":
        _remove_existing(path)
    elif entry["kind"] == "file":
        blob = blob_root / entry["blob"]
        data = blob.read_bytes()
        restored_hash = hashlib.sha256(data).hexdigest()
        if restored_hash != entry["sha256"]:
            raise ValueError("backup blob digest changed during restore")
        _atomic_write_bytes(path, data)
        _apply_metadata(path, entry)
        return restored_hash
    elif entry["kind"] == "symlink":
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.restore-link.", dir=path.parent)
        os.close(fd)
        temporary = Path(temporary_name)
        temporary.unlink()
        os.symlink(entry["link_target"], temporary)
        os.replace(temporary, path)
        _apply_metadata(path, entry, follow_symlinks=False)
    else:
        raise ValueError("unknown backup entry kind")
    return None


def _restore_entries(entries: list[dict[str, Any]], blob_root: Path) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    restored_hashes: dict[str, str] = {}
    for entry in reversed(entries):
        path = Path(entry["path"])
        try:
            restored_hash = _restore_entry(path, entry, blob_root)
            if restored_hash is not None:
                restored_hashes[str(path)] = restored_hash
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"could not restore {path}: {exc}")
    return errors, restored_hashes


def _verify_entries(entries: list[dict[str, Any]], restored_hashes: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    restored_hashes = restored_hashes or {}
    for entry in entries:
        path = Path(entry["path"])
        try:
            kind = entry["kind"]
            if kind == "absent":
                if path.exists() or path.is_symlink():
                    errors.append("post-restore verification failed for prior absence")
            elif kind == "file":
                if path.is_symlink() or not path.is_file():
                    errors.append("post-restore verification failed for file hash")
                    continue
                try:
                    content_hash = sha256_file(path)
                except OSError:
                    content_hash = restored_hashes.get(str(path))
                if content_hash != entry["sha256"]:
                    errors.append("post-restore verification failed for file hash")
                    continue
                details = _metadata(path)
                if any(details[field] != entry[field] for field in ("uid", "gid")):
                    errors.append("post-restore verification failed for file ownership")
                if any(details[field] != entry[field] for field in ("mode", "mtime_ns")):
                    errors.append("post-restore verification failed for file metadata")
            elif kind == "symlink":
                if not path.is_symlink() or os.readlink(path) != entry["link_target"]:
                    errors.append("post-restore verification failed for symlink")
                    continue
                details = _metadata(path)
                if any(details[field] != entry[field] for field in ("uid", "gid", "mtime_ns")):
                    errors.append("post-restore verification failed for symlink metadata")
            else:
                errors.append("post-restore verification failed for unknown entry")
        except OSError:
            errors.append("post-restore verification I/O failure")
    return errors


def _load_recovery_index(index_path: Path) -> tuple[dict[str, Any], Path]:
    report_index = json.loads(index_path.read_text(encoding="utf-8"))
    recovery_name = report_index.get("recovery_index", "recovery-index.json")
    if not isinstance(recovery_name, str) or Path(recovery_name).name != recovery_name:
        raise ValueError("recovery index name is invalid")
    recovery_path = index_path.parent / recovery_name
    return json.loads(recovery_path.read_text(encoding="utf-8")), recovery_path


def restore_backup(index_path: Path) -> list[str]:
    try:
        index, recovery_path = _load_recovery_index(index_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"backup index is invalid: {exc}"]
    entries = index.get("entries")
    if not isinstance(entries, list):
        return ["backup index entries are invalid"]
    errors = _preflight_restore(recovery_path, entries)
    if errors:
        return errors
    attempt_dir = Path(tempfile.mkdtemp(prefix=".restore-attempt-", dir=recovery_path.parent))
    working_entries = _capture_entries((Path(entry["path"]) for entry in entries), attempt_dir / "blobs")
    errors, restored_hashes = _restore_entries(entries, recovery_path.parent)
    errors.extend(_verify_entries(entries, restored_hashes))
    if not errors:
        shutil.rmtree(attempt_dir)
        return []
    rollback_entries = [asdict(entry) for entry in working_entries]
    rollback_errors, rollback_hashes = _restore_entries(rollback_entries, attempt_dir)
    rollback_errors.extend(_verify_entries(rollback_entries, rollback_hashes))
    shutil.rmtree(attempt_dir)
    if rollback_errors:
        errors.extend(f"restore-attempt rollback failed: {error}" for error in rollback_errors)
    return errors


def observed_changed_paths(
    manifest_path: Path, before_index: Path
) -> tuple[list[str], list[str]]:
    manifest_bytes = manifest_path.read_bytes()
    data = json.loads(manifest_bytes.decode("utf-8"))
    errors = validate_manifest(data)
    if errors:
        return [], errors
    try:
        index, _ = _load_recovery_index(before_index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [], [f"backup index is invalid: {exc}"]
    if index.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
        return [], ["manifest digest does not match backup index"]
    if index.get("accepted_scope") != _accepted_scope(data):
        return [], ["manifest scope does not match backup index"]
    if index.get("transaction_id") != data.get("transaction_id"):
        return [], ["manifest transaction does not match backup index"]
    roots = [Path(root) for root in index["allowed_roots"]]
    current = _snapshot(roots, [Path(path) for path in index.get("excluded_paths", [])])
    before = index.get("scope_snapshot", {})
    changed = set(before).symmetric_difference(current)
    changed.update(path for path in set(before).intersection(current) if before[path] != current[path])
    declared = {str(Path(target["path"]).resolve(strict=False)) for target in data["targets"]}
    errors = [f"undisclosed changed path: {path}" for path in sorted(changed - declared)]
    return sorted(changed), errors


def verify_changed_paths(manifest_path: Path, before_index: Path) -> list[str]:
    _, errors = observed_changed_paths(manifest_path, before_index)
    return errors


def static_commission(
    manifest_path: Path, before_index: Path, ledger_path: Path
) -> dict[str, Any]:
    """Prove the AI ledger equals physical changes and parse every changed target."""
    observed, errors = observed_changed_paths(manifest_path, before_index)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if ledger.get("schema_version") != 1:
            errors.append("changed-paths schema_version must be 1")
        if ledger.get("transaction_id") != manifest.get("transaction_id"):
            errors.append("changed-paths transaction does not match manifest")
        raw_ledger = ledger.get("changed_paths")
        if not isinstance(raw_ledger, list) or any(not isinstance(item, str) for item in raw_ledger):
            errors.append("changed_paths must be an array of strings")
            raw_ledger = []
        ledger_paths = [str(Path(item).resolve(strict=False)) for item in raw_ledger]
        if any(raw != canonical for raw, canonical in zip(raw_ledger, ledger_paths)):
            errors.append("changed_paths entries must use canonical absolute spelling")
        if ledger_paths != sorted(set(ledger_paths)):
            errors.append("changed_paths must be sorted and unique")
        if ledger_paths != sorted(set(observed)):
            errors.append("AI changed-path ledger must be exactly equal to observed changes")
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        manifest = {}
        errors.append(f"changed-path ledger is invalid: {exc}")
    for raw_path in observed:
        path = Path(raw_path)
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix in {".yaml", ".yml"}:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix == ".toml":
                tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, yaml.YAMLError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"syntax validation failed for observed target {path}: {exc}")
    return {
        "schema_version": 1,
        "transaction_id": manifest.get("transaction_id"),
        "observed_changed_paths": observed,
        "static": {"passed": not errors, "errors": redact(errors)},
        "live": {"state": "not_attempted", "required": False, "detail": "pending live movement"},
    }


def write_receipt(data: dict[str, Any], json_path: Path, markdown_path: Path) -> dict[str, Any]:
    receipt = redact(data)
    live_state = receipt.get("live_state", "not_attempted")
    if live_state not in LIVE_STATES:
        raise ValueError(f"live_state must be one of {sorted(LIVE_STATES)}")
    receipt["live_state"] = live_state
    if receipt.get("restored"):
        receipt["transaction_status"] = "rolled_back"
    _atomic_write_json(json_path, receipt)
    lines = ["# Marianne model/profile refresh receipt", "", "```json", json.dumps(receipt, indent=2, sort_keys=True), "```", ""]
    _atomic_write_bytes(markdown_path, "\n".join(lines).encode("utf-8"))
    return receipt


def install_technique(skill_path: Path, home: Path | None = None) -> dict[str, str]:
    if skill_path.name != "SKILL.md" or not skill_path.is_file():
        raise ValueError("skill_path must name an existing SKILL.md")
    home = (home or Path.home()).absolute()
    destination = home / ".marianne" / "techniques" / "marianne-model-profile-refresh" / "SKILL.md"
    _atomic_write_bytes(destination, skill_path.read_bytes())
    return {"path": str(destination), "sha256": sha256_file(destination)}


def lock_bundle(root: Path, lock_path: Path, *, verify: bool = False) -> dict[str, Any]:
    root = root.resolve()
    files = {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.resolve() != lock_path.resolve()
    }
    result = {"schema_version": 1, "root": ".", "files": files}
    if verify:
        existing = json.loads(lock_path.read_text(encoding="utf-8"))
        if existing != result:
            raise ValueError("release lock does not match bundle")
    else:
        _atomic_write_json(lock_path, result)
    return result


def inventory(roots: Iterable[Path]) -> dict[str, Any]:
    paths = [path.absolute() for path in roots]
    return redact({"roots": [str(path) for path in paths], "entries": _snapshot(paths, [])})


def inventory_authority(authority_path: Path) -> dict[str, Any]:
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    roots = authority.get("allowed_roots")
    if authority.get("schema_version") != 1 or not isinstance(roots, list) or not roots:
        raise ValueError("authority roots document is invalid")
    return inventory(Path(root) for root in roots)


def _json_argument(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_parser = commands.add_parser("inventory")
    inventory_parser.add_argument("roots", nargs="+", type=Path)
    inventory_parser.add_argument("--output", type=Path)
    authority_inventory_parser = commands.add_parser("inventory-authority")
    authority_inventory_parser.add_argument("authority", type=Path)
    authority_inventory_parser.add_argument("output", type=Path)
    validate_parser = commands.add_parser("validate-manifest")
    validate_parser.add_argument("manifest", type=Path)
    validate_parser.add_argument("--authority-roots", type=Path)
    validate_parser.add_argument("--authority-sha256")
    validate_parser.add_argument("--transaction-id")
    backup_parser = commands.add_parser("backup")
    backup_parser.add_argument("manifest", type=Path)
    backup_parser.add_argument("backup_dir", type=Path)
    backup_parser.add_argument("--authority-roots", type=Path)
    backup_parser.add_argument("--authority-sha256")
    backup_parser.add_argument("--transaction-id")
    verify_parser = commands.add_parser("verify-changes")
    verify_parser.add_argument("manifest", type=Path)
    verify_parser.add_argument("index", type=Path)
    restore_parser = commands.add_parser("restore")
    restore_parser.add_argument("index", type=Path)
    receipt_parser = commands.add_parser("receipt")
    receipt_parser.add_argument("input", type=Path)
    receipt_parser.add_argument("json_path", type=Path)
    receipt_parser.add_argument("markdown_path", type=Path)
    static_parser = commands.add_parser("static-commission")
    static_parser.add_argument("manifest", type=Path)
    static_parser.add_argument("index", type=Path)
    static_parser.add_argument("ledger", type=Path)
    static_parser.add_argument("output", type=Path)
    technique_parser = commands.add_parser("install-technique")
    technique_parser.add_argument("skill", type=Path)
    technique_parser.add_argument("--home", type=Path)
    lock_parser = commands.add_parser("lock-bundle")
    lock_parser.add_argument("root", type=Path)
    lock_parser.add_argument("lock", type=Path)
    lock_parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "inventory":
        result = inventory(args.roots)
        if args.output:
            _atomic_write_json(args.output, result)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "inventory-authority":
        try:
            result = inventory_authority(args.authority)
            _atomic_write_json(args.output, result)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "validate-manifest":
        authority_options = (args.authority_roots, args.authority_sha256, args.transaction_id)
        if any(option is not None for option in authority_options) and not all(
            option is not None for option in authority_options
        ):
            errors = ["authority-roots, authority-sha256, and transaction-id must be supplied together"]
        elif all(option is not None for option in authority_options):
            errors = validate_manifest_authority(
                _json_argument(args.manifest),
                args.authority_roots,
                args.authority_sha256,
                args.transaction_id,
            )
        else:
            errors = validate_manifest(_json_argument(args.manifest))
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 1
    try:
        if args.command == "backup":
            authority_options = (args.authority_roots, args.authority_sha256, args.transaction_id)
            if any(option is not None for option in authority_options) and not all(
                option is not None for option in authority_options
            ):
                raise ValueError(
                    "authority-roots, authority-sha256, and transaction-id must be supplied together"
                )
            result = create_backup(
                args.manifest,
                args.backup_dir,
                authority_path=args.authority_roots,
                authority_sha256=args.authority_sha256,
                transaction_id=args.transaction_id,
            )
        elif args.command == "verify-changes":
            errors = verify_changed_paths(args.manifest, args.index)
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
            return 0 if not errors else 1
        elif args.command == "restore":
            errors = restore_backup(args.index)
            print(json.dumps({"restored": not errors, "errors": errors}, indent=2))
            return 0 if not errors else 1
        elif args.command == "receipt":
            result = write_receipt(_json_argument(args.input), args.json_path, args.markdown_path)
        elif args.command == "static-commission":
            result = static_commission(args.manifest, args.index, args.ledger)
            _atomic_write_json(args.output, result)
        elif args.command == "install-technique":
            result = install_technique(args.skill, args.home)
        else:
            result = lock_bundle(args.root, args.lock, verify=args.verify)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
