"""Hash governed configuration, excluding code-defined runtime surfaces.

Unknown files remain governed. Client exclusions are anchored to this user's
actual home/XDG locations, never inferred from a repository directory's name.
Plugin caches contain installed source and therefore remain governed. This is
observation policy, not mutation authority or a worker-configurable waiver.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Iterable

policy_version = "governed-config-v2"
POLICY_VERSION = policy_version

# Generated development artifacts, at any depth. No generic logs/cache or file
# extension exclusions: a repository logs/ or SQLite fixture is real source.
_GENERATED = frozenset({".git", ".venv", "venv", "__pycache__", ".pytest_cache",
                        ".mypy_cache", ".ruff_cache", ".tox", ".nox", "node_modules"})
_RUNTIME = {
    "claude": {"paste-cache", "session-data", "session-env", "sessions", "jobs",
               "tasks", "file-history", "shell-snapshots", "debug", "projects",
               "metrics", "cache", "backups", "daemon", "history.jsonl",
               "daemon.status.json", "daemon.lock", "stats-cache.json",
               "mcp-needs-auth-cache.json", "mcp-health-cache.json", "__store.db",
               "__store.db-wal", "__store.db-shm", ".last-update-result.json",
               ".last-cleanup"},
    "codex": {"sessions", "log", "cache", "tmp", ".tmp", "attachments",
              "generated_images", "shell_snapshots", "thread-writer-locks",
              "history.jsonl", "session_index.jsonl", "models_cache.json",
              "version.json", "installation_id"},
    "gemini": {"history", "tmp", "state.json", "installation_id"},
    "marianne": {"logs", "interactive-logs", "dashboard-submissions", "snapshots"},
    "opencode-data": {"storage", "tool-output", "snapshot", "log", "opencode.db",
                      "opencode.db-wal", "opencode.db-shm"},
    "opencode-config": set(),
}
_AGY_RUNTIME = {"brain", "cache", "crashes", "knowledge", "implicit", "log",
                "scratch", "conversations", "annotations", "presence", "cli.log",
                "history.jsonl", "last_check.timestamp", "jetski_state.pbtxt",
                "jetbox_summaries_proto.pb", "conversation_summaries.db",
                "conversation_summaries.db-wal", "conversation_summaries.db-shm",
                "installation_id"}


def _absolute(path: Path) -> Path:
    # Normalize lexical spelling without following a symlink.
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _client_roots() -> dict[Path, str]:
    home = _absolute(Path.home())
    config = _absolute(Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")))
    data = _absolute(Path(os.environ.get("XDG_DATA_HOME", home / ".local/share")))
    return {home / ".claude": "claude", home / ".codex": "codex",
            home / ".gemini": "gemini", home / ".marianne": "marianne",
            config / "opencode": "opencode-config", data / "opencode": "opencode-data"}


def _ignored(path: Path, clients: dict[Path, str]) -> bool:
    if any(part in _GENERATED for part in path.parts):
        return True
    for root, client in clients.items():
        try:
            parts = path.relative_to(root).parts
        except ValueError:
            continue
        if not parts:
            return False
        first = parts[0]
        if first in _RUNTIME[client]:
            return True
        if client == "claude" and re.fullmatch(r"security_warnings_state_[0-9a-f-]+\.json", first):
            return True
        if client == "claude" and len(parts) == 2 and first == "security" and (
            parts[1] == "log.txt" or re.fullmatch(
                r"security_warnings_state_[0-9a-f-]+\.(?:json|lock)", parts[1]
            )
        ):
            return True
        if client == "codex" and re.fullmatch(r"(?:state|logs|memories|goals|queue|thread_history)_\d+\.sqlite(?:-wal|-shm)?", first):
            return True
        if client == "marianne" and (
            re.fullmatch(r"(?:conductor\.log|monitor\.jsonl)(?:\.\d+(?:\.gz)?)?", first)
            or re.fullmatch(r"(?:daemon-state(?:-[\w-]+)?|clone-[\w-]+-state|marianne(?:-state)?|monitor|global-learning|registry|state|conductor)\.db(?:-wal|-shm|\.bak)?", first)
            or re.fullmatch(r"completion_[0-9a-f-]+", first)
        ):
            return True
        if client == "gemini" and len(parts) > 1 and first == "antigravity-cli" and parts[1] in _AGY_RUNTIME:
            return True
        return False
    return False


def snapshot(roots: Iterable[Path], excluded: Iterable[Path], *,
             required_paths: Iterable[Path] = ()) -> dict[str, dict[str, str]]:
    """Return absolute lexical path -> kind/hash or literal symlink target.

    Never follow symlinks, including intermediate root components. Permission,
    concurrent governed mutation and unsupported special-file errors fail closed;
    absence is represented by no entry so additions/deletions compare normally.
    Only hashes and link text are returned; file bodies never leave this module.
    Admission-owned required_paths override exclusions for exact targets and the
    ancestors needed to reach them, never for siblings or symlink traversal.
    """
    roots = [_absolute(Path(p)) for p in roots]
    required = {_absolute(Path(p)) for p in required_paths}
    if any(not any(p == root or root in p.parents for root in roots) for p in required):
        raise ValueError("required observation path outside supplied authority roots")
    exclusions = [_absolute(Path(p)) for p in excluded]
    clients = _client_roots()
    result: dict[str, dict[str, str]] = {}

    def skip(path: Path) -> bool:
        # Admission-owned exact targets override observation exclusions. Ancestors
        # permit traversal only; their ignored siblings remain ignored.
        if path in required or any(path in p.parents for p in required):
            return False
        return any(path == x or x in path.parents for x in exclusions) or _ignored(path, clients)

    def visit(parent_fd: int, name: str, path: Path) -> None:
        if skip(path):
            return
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            result[str(path)] = {"kind": "symlink", "value": os.readlink(name, dir_fd=parent_fd)}
            return
        if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
            raise ValueError(f"unsupported governed file type: {path}")
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if stat.S_ISDIR(info.st_mode):
            flags |= os.O_DIRECTORY
        fd = os.open(name, flags, dir_fd=parent_fd)
        try:
            opened = os.fstat(fd)
            if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError(f"governed path changed during observation: {path}")
            if stat.S_ISDIR(opened.st_mode):
                for child in sorted(os.listdir(fd)):
                    visit(fd, child, path / child)
            else:
                digest = hashlib.sha256()
                # Only the native marketplace refresh timestamp is runtime data.
                # Keep all sources, locations, flags and unknown fields governed.
                semantic_marketplace = (
                    path not in required
                    and path == _absolute(Path.home()) / ".claude/plugins/known_marketplaces.json"
                )
                body = bytearray()
                while chunk := os.read(fd, 1024 * 1024):
                    digest.update(chunk)
                    if semantic_marketplace:
                        body.extend(chunk)
                if semantic_marketplace:
                    try:
                        data = json.loads(body)
                        if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
                            for entry in data.values():
                                entry.pop("lastUpdated", None)
                            digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())
                    except (ValueError, UnicodeError):
                        pass  # Malformed content remains governed by its raw hash.
                final = os.fstat(fd)
                if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (final.st_size, final.st_mtime_ns, final.st_ctime_ns):
                    raise ValueError(f"governed file changed during observation: {path}")
                result[str(path)] = {"kind": "file", "value": digest.hexdigest()}
        finally:
            os.close(fd)

    for raw in roots:
        root = _absolute(Path(raw))
        if skip(root):
            continue
        fd = os.open(root.anchor, os.O_RDONLY | os.O_DIRECTORY)
        try:
            # Open ancestors without following links, avoiding outside-authority
            # reads even if a directory is replaced during the walk.
            for part in root.parts[1:-1]:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = next_fd
            try:
                visit(fd, root.name or ".", root)
            except FileNotFoundError:
                # Only a missing root is normal; a disappearing descendant is a
                # concurrent governed change and must not silently disappear.
                try:
                    os.stat(root.name or ".", dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise
        except FileNotFoundError:
            # An absent ancestor also means the requested root is absent.
            if root.exists():
                raise
        finally:
            os.close(fd)
    return dict(sorted(result.items()))
