from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

import yaml


REPO = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO / "marianne" / "skills" / "marianne-model-profile-refresh"
SCORE_ROOT = SKILL_ROOT / "score"
RUNTIME_FILES = {
    "model-profile-refresh.yaml",
    "request.md",
    "runbook.md",
    "scripts/refreshctl.py",
    "scripts/run_refresh.py",
    "technique/SKILL.md",
}
LOCKED_RUNTIME = {
    "model-profile-refresh.yaml": "ead0e48a3eddea65bb8e9c13606f5826a64c79855a35903046db67b96f4a0833",
    "request.md": "1aa18e78695a449a9a3bc80f68afab6e540a9f0527000744e65a41f993a9a84b",
    "runbook.md": "09975ba2d3e8b8306d2f52ff4d9ee79a42e3a156eb09505d9221a959604d2abe",
    "scripts/refreshctl.py": "2c8fe613625f2060e7d7b7e06ed56e43893c702404a7e4093a7d55ae94cb19fc",
    "scripts/run_refresh.py": "fd6637c774f22461b3a4e0b85d9f4caa8e308def35a9fb885abef5bf54f1690a",
    "technique/SKILL.md": "09b4d22ffb685544166958b75e6f89301b4edc9505d2f993959756fa85ecf7cc",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        entries[relative] = digest
    return entries


def load_refreshctl():
    path = SCORE_ROOT / "scripts" / "refreshctl.py"
    spec = importlib.util.spec_from_file_location("public_refreshctl", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def valid_manifest(tmp_path: Path, target: Path) -> dict:
    return {
        "schema_version": 1,
        "transaction_id": "txn-plugin-test",
        "request": "update Gemini profiles to 3.7 Flash",
        "mode": "specific",
        "allowed_roots": [str(tmp_path)],
        "facts": {
            "provider": "google",
            "model": "gemini-3.7-flash",
            "context_window": 1_048_576,
            "max_output_tokens": 65_536,
            "thinking_levels": ["low", "medium", "high"],
            "evidence_urls": [
                "https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash"
            ],
        },
        "targets": [
            {
                "path": str(target),
                "classification": "active",
                "explicitly_named": True,
            }
        ],
    }


def write_manifest(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "update-manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_runtime_is_the_exact_canonical_locked_allowlist() -> None:
    actual_files = {
        path.relative_to(SCORE_ROOT).as_posix()
        for path in SCORE_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    assert actual_files == RUNTIME_FILES
    assert {relative: sha256(SCORE_ROOT / relative) for relative in sorted(RUNTIME_FILES)} == LOCKED_RUNTIME


def test_skill_manifest_covers_every_release_file_and_no_cache_artifacts() -> None:
    manifest = parse_manifest(SKILL_ROOT / "MANIFEST.sha256")
    current = {
        path.relative_to(SKILL_ROOT).as_posix(): sha256(path)
        for path in sorted(SKILL_ROOT.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    assert manifest == current


def test_shipped_skill_tree_physically_contains_no_cache_artifacts() -> None:
    artifacts = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if path.name in {"__pycache__", ".pytest_cache"} or path.suffix == ".pyc"
    )
    assert artifacts == []


def test_version_and_plugin_manifests_are_0_4_0() -> None:
    version = (SKILL_ROOT / "VERSION").read_text(encoding="utf-8")
    assert "version: 0.4.0" in version
    assert (
        "canonical_release_lock_sha256: "
        "969da4e206777e413f954fbce077d2c68f205638dc3b623278f2482426b5e3f1"
    ) in version
    plugin = json.loads((REPO / "marianne/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((REPO / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert plugin["version"] == "0.4.0"
    entry = next(item for item in marketplace["plugins"] if item["name"] == "marianne")
    assert entry["version"] == "0.4.0"


def test_score_keeps_nine_movements_and_score_safe_technique() -> None:
    score = yaml.safe_load((SCORE_ROOT / "model-profile-refresh.yaml").read_text(encoding="utf-8"))
    assert [score["movements"][number]["name"] for number in range(1, 10)] == [
        "census",
        "research",
        "manifest-gate",
        "backup",
        "apply",
        "static-commissioning",
        "live-commissioning",
        "finalize-or-compensate",
        "receipt",
    ]
    assert "pause_before_chain" not in score
    assert score["techniques"]["marianne-model-profile-refresh"]["phases"] == [
        "2",
        "5",
        "research",
        "apply",
    ]
    assert "direct-agent mode" not in (
        SCORE_ROOT / "technique/SKILL.md"
    ).read_text(encoding="utf-8").lower()


def test_clean_home_install_copies_only_the_score_safe_projection(tmp_path: Path) -> None:
    refreshctl = load_refreshctl()
    result = refreshctl.install_technique(SCORE_ROOT / "technique/SKILL.md", tmp_path)
    installed = tmp_path / ".marianne/techniques/marianne-model-profile-refresh/SKILL.md"
    assert installed.read_bytes() == (SCORE_ROOT / "technique/SKILL.md").read_bytes()
    assert result == {"path": str(installed), "sha256": sha256(installed)}
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file()) == [
        ".marianne/techniques/marianne-model-profile-refresh/SKILL.md"
    ]


def test_noop_transaction_verifies_an_empty_change_set(tmp_path: Path) -> None:
    refreshctl = load_refreshctl()
    target = tmp_path / "profile.yaml"
    target.write_text("model: gemini-3.7-flash\n", encoding="utf-8")
    manifest = write_manifest(tmp_path, valid_manifest(tmp_path, target))
    index = refreshctl.create_backup(manifest, tmp_path / "backup")
    assert refreshctl.verify_changed_paths(manifest, Path(index["index_path"])) == []
    assert refreshctl.observed_changed_paths(manifest, Path(index["index_path"])) == ([], [])


def test_forced_failure_restores_exact_bytes_mode_and_prior_absence(tmp_path: Path) -> None:
    refreshctl = load_refreshctl()
    target = tmp_path / "profile.yaml"
    target.write_bytes(b"model: gemini-3.5-flash\n")
    target.chmod(0o640)
    future = tmp_path / "generated.yaml"
    data = valid_manifest(tmp_path, target)
    data["targets"].append(
        {"path": str(future), "classification": "active", "explicitly_named": True}
    )
    manifest = write_manifest(tmp_path, data)
    index = refreshctl.create_backup(manifest, tmp_path / "backup")

    target.write_bytes(b"model: broken\n")
    target.chmod(0o600)
    future.write_text("created: true\n", encoding="utf-8")

    assert refreshctl.restore_backup(Path(index["index_path"])) == []
    assert target.read_bytes() == b"model: gemini-3.5-flash\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert not future.exists()


def test_public_helper_rejects_noncanonical_later_target_before_rollback_can_delete_original(
    tmp_path: Path,
) -> None:
    refreshctl = load_refreshctl()
    project = tmp_path / "project"
    project.mkdir()
    original = project / "profile.yaml"
    original.write_bytes(b"original: true\n")
    data = valid_manifest(project, original)
    missing_parent = project / "newdir"
    alias = missing_parent / ".." / original.name
    data["targets"].append(
        {"path": str(alias), "classification": "active", "explicitly_named": True}
    )

    errors = refreshctl.validate_manifest(data)

    assert any(
        "targets[1].path must use canonical absolute spelling" in error
        for error in errors
    )
    assert original.read_bytes() == b"original: true\n"
    assert not missing_parent.exists()


def test_public_helper_exactly_backs_up_and_restores_canonical_symlink_target(
    tmp_path: Path,
) -> None:
    refreshctl = load_refreshctl()
    source = tmp_path / "source.yaml"
    source.write_bytes(b"source: true\n")
    link = tmp_path / "current.yaml"
    link.symlink_to(source.name)
    before = os.lstat(link)
    manifest = write_manifest(tmp_path, valid_manifest(tmp_path, link))

    assert refreshctl.validate_manifest(json.loads(manifest.read_text(encoding="utf-8"))) == []
    index = refreshctl.create_backup(manifest, tmp_path / "backup")
    protected = json.loads(
        (Path(index["index_path"]).parent / "recovery-index.json").read_text(
            encoding="utf-8"
        )
    )
    assert protected["entries"][0]["kind"] == "symlink"
    assert protected["entries"][0]["link_target"] == source.name

    replacement = tmp_path / "replacement.yaml"
    replacement.write_bytes(b"replacement: true\n")
    link.unlink()
    link.symlink_to(replacement.name)

    assert refreshctl.restore_backup(Path(index["index_path"])) == []
    after = os.lstat(link)
    assert link.readlink() == Path(source.name)
    assert (after.st_uid, after.st_gid, after.st_mtime_ns) == (
        before.st_uid,
        before.st_gid,
        before.st_mtime_ns,
    )


def test_runner_defaults_remain_home_relative(tmp_path: Path, monkeypatch) -> None:
    path = SCORE_ROOT / "scripts" / "run_refresh.py"
    spec = importlib.util.spec_from_file_location("public_refresh_runner", path)
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.setattr(runner.Path, "home", classmethod(lambda cls: tmp_path))
    args = runner.build_parser().parse_args([])
    assert args.workspace_root == tmp_path / ".marianne/workspaces/model-profile-refresh"
    assert args.backup_root.parent == tmp_path / ".marianne/backups/model-profile-refresh"
    assert os.fspath(tmp_path) in os.fspath(args.workspace_root)
