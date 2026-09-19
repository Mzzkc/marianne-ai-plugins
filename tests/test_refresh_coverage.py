from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1] / "marianne/skills/marianne-model-profile-refresh/score/scripts"
sys.path.insert(0, str(ROOT))
import refresh_scope
spec = importlib.util.spec_from_file_location("coverage_refreshctl", ROOT / "refreshctl.py")
ctl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ctl
spec.loader.exec_module(ctl)


def scope_fixture(tmp_path):
    catalog = tmp_path / "plugins/marianne/docs/ref/instrument-catalog.yaml"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(yaml.safe_dump({"instruments": {"broker": {"runs_models": ["old-a", "old-b"]}}, "musicians": {"old-a": {"provider": "vendor-a"}, "old-b": {"provider": "vendor-b"}, "unrelated": {"provider": "vendor-c"}}}))
    profiles = tmp_path / "src/marianne/instruments/builtins"
    profiles.mkdir(parents=True)
    (profiles / "broker.yaml").write_text(yaml.safe_dump({"name": "broker", "models": [{"name": "old-a"}, {"name": "old-b"}]}))
    return refresh_scope.build_scope(tmp_path, [tmp_path])


def manifest(tmp_path):
    return {"schema_version": 2, "transaction_id": "trial", "request": "Refresh all shipped providers", "mode": "broad", "allowed_roots": [str(tmp_path)], "provider_results": [{"provider": provider, "status": "no_change", "evidence_urls": ["https://" + provider + ".example/models"], "reason": "Current installed releases match official catalog", "facts": []} for provider in ("vendor-a", "vendor-b", "vendor-c")], "targets": []}


def authority(tmp_path, scope):
    p = tmp_path / "authority.json"
    p.write_text(json.dumps({"schema_version": 1, "transaction_id": "trial", "allowed_roots": [str(tmp_path)], "refresh_scope": scope}))
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


def test_scope_includes_broker_and_catalog_only_shipped_providers(tmp_path):
    scope = scope_fixture(tmp_path)
    assert {p["id"] for p in scope["providers"]} == {"vendor-a", "vendor-b", "vendor-c"}
    assert next(p for p in scope["providers"] if p["id"] == "vendor-c")["routes"] == []


def test_broad_subset_cannot_pass_and_no_change_counts(tmp_path):
    scope = scope_fixture(tmp_path)
    p, digest = authority(tmp_path, scope)
    m = manifest(tmp_path)
    assert ctl.validate_manifest_authority(m, p, digest, "trial") == []
    m["provider_results"].pop()
    assert any("coverage" in e for e in ctl.validate_manifest_authority(m, p, digest, "trial"))


def test_blocked_result_and_v1_cannot_bypass_new_scope(tmp_path):
    scope = scope_fixture(tmp_path)
    p, digest = authority(tmp_path, scope)
    m = manifest(tmp_path)
    m["provider_results"][0]["status"] = "blocked"
    assert any("blocked" in e for e in ctl.validate_manifest_authority(m, p, digest, "trial"))
    m["schema_version"] = 1
    m["facts"] = {"evidence_urls": ["https://vendor-a.example/models"]}
    assert any("version 2" in e for e in ctl.validate_manifest_authority(m, p, digest, "trial"))


def test_specific_selector_cannot_reduce_shipped_coverage(tmp_path):
    scope_fixture(tmp_path)
    import pytest
    with pytest.raises(ValueError, match="all shipped providers"):
        refresh_scope.build_scope(tmp_path, [tmp_path], ["vendor-a"])


def test_configured_claim_missing_from_profile_fails_even_when_bytes_parse(tmp_path):
    f = tmp_path / "instrument.yaml"
    f.write_text("models: []\n")
    m = manifest(tmp_path)
    row = m["provider_results"][0]
    row.update(status="changes", facts=[{"id": "release-a", "model": "new-a", "evidence_urls": row["evidence_urls"]}])
    m["targets"] = [{"path": str(f), "classification": "active", "disposition": "change", "fact_ids": ["release-a"], "checks": [{"pointer": "/models/@name=new-a/context_window", "equals": 1000}]}]
    assert ctl.validate_manifest(m) == []
    mp = tmp_path / "manifest.json"
    mp.write_text(json.dumps(m))
    ctl.create_backup(mp, tmp_path / "backup")
    f.write_text("models: []\n# edited but model is still absent\n")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"schema_version": 1, "transaction_id": "trial", "changed_paths": [str(f)]}))
    result = ctl.static_commission(mp, tmp_path / "backup/transaction-state.json", ledger)
    assert not result["static"]["passed"]
    assert any("configured" in e for e in result["static"]["errors"])


def test_duplicate_providers_and_unknown_fact_references_rejected(tmp_path):
    m = manifest(tmp_path)
    m["provider_results"].append(m["provider_results"][0])
    assert any("duplicate" in e for e in ctl.validate_manifest(m))
    m = manifest(tmp_path)
    m["targets"] = [{"path": str(tmp_path / "x.yaml"), "classification": "active", "disposition": "change", "fact_ids": ["invented"], "checks": [{"contains": "new-a"}]}]
    assert any("fact" in e for e in ctl.validate_manifest(m))


def test_v2_rejects_symlink_alias_to_unbacked_referent(tmp_path):
    target = tmp_path / "profile.yaml"
    target.write_text("models: []\n")
    alias = tmp_path / "alias.yaml"
    alias.symlink_to(target)
    data = manifest(tmp_path)
    data["provider_results"][0].update(status="changes", facts=[{
        "id": "release-a", "model": "new-a",
        "evidence_urls": ["https://vendor-a.example/models"]}])
    data["targets"] = [{"path": str(alias), "classification": "active",
        "disposition": "change", "fact_ids": ["release-a"],
        "checks": [{"contains": "new-a"}]}]
    assert any("symlink aliases" in error for error in ctl.validate_manifest(data))
