#!/usr/bin/env python3
"""Require every shipped provider; associate routes without model-name guesses."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any
import yaml


def _read(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def _unresolved_id(path: Path, instrument: str, model: str) -> str:
    value = json.dumps([str(path.resolve()), instrument, model], separators=(",", ":"))
    return "route-" + hashlib.sha256(value.encode()).hexdigest()[:20]


def _installed_catalog_path() -> Path:
    """Resolve this skill's own plugin bundle, independent of caller cwd."""
    return Path(__file__).resolve().parents[4] / "docs/ref/instrument-catalog.yaml"


def _installed_builtin_dir() -> Path | None:
    try:
        spec = importlib.util.find_spec("marianne")
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.submodule_search_locations:
        return None
    for location in spec.submodule_search_locations:
        candidate = Path(location) / "instruments/builtins"
        if candidate.is_dir():
            return candidate
    return None


def _local_provider_metadata(project_root: Path, roots: list[Path]) -> tuple[set[str], dict[str, str]]:
    providers: set[str] = set()
    models: dict[str, str] = {}
    def add(provider: Any, names: Any, source: Path) -> None:
        if not isinstance(provider, str) or not provider.strip() or not isinstance(names, list):
            raise ValueError(f"invalid provider metadata: {source}")
        providers.add(provider)
        for name in names:
            if not isinstance(name, str) or not name:
                raise ValueError(f"invalid provider model identity: {source}")
            if name in models and models[name] != provider:
                raise ValueError(f"conflicting local model provider: {name}")
            models[name] = provider
    marianne_roots = {project_root / ".marianne", *(root for root in roots if root.name == ".marianne")}
    for directory in sorted(marianne_roots):
        path = directory / "model-providers.yaml"
        if not path.is_file():
            continue
        data = _read(path)
        if data.get("schema_version") != 1 or not isinstance(data.get("providers"), dict):
            raise ValueError(f"invalid model-providers schema: {path}")
        for provider, row in data["providers"].items():
            if not isinstance(row, dict) or "models" not in row:
                raise ValueError(f"invalid provider models mapping: {path}")
            add(provider, row["models"], path)
    # Native service keys identify configured providers; no broker-to-vendor guess.
    opencode_roots = {project_root, *(root for root in roots if root.name == "opencode")}
    for directory in sorted(opencode_roots):
        path = directory / "opencode.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("provider", {}), dict):
            raise ValueError(f"invalid OpenCode provider configuration: {path}")
        for provider, row in data.get("provider", {}).items():
            if not isinstance(row, dict) or not isinstance(row.get("models", {}), dict):
                raise ValueError(f"invalid OpenCode provider models: {path}")
            add(provider, [f"{provider}/{name}" for name in row.get("models", {})], path)
    return providers, models


def build_scope(project_root: Path, roots: list[Path], providers: list[str] | None = None) -> dict:
    project_root = project_root.resolve()
    catalogs = [project_root / "plugins/marianne/docs/ref/instrument-catalog.yaml",
                project_root / "marianne/docs/ref/instrument-catalog.yaml",
                _installed_catalog_path()]
    catalog_path = next((p for p in catalogs if p.is_file()), None)
    if catalog_path is None:
        raise ValueError("active instrument catalog is required to establish refresh coverage")
    catalog = _read(catalog_path)
    musicians = catalog.get("musicians", {})
    instruments = catalog.get("instruments", {})
    if not isinstance(musicians, dict) or not isinstance(instruments, dict):
        raise ValueError("catalog musicians/instruments must be mappings")
    model_provider: dict[str, str] = {}
    for name, row in musicians.items():
        if not isinstance(row, dict) or not isinstance(row.get("provider"), str):
            continue
        provider = row["provider"].strip()
        if not provider:
            continue
        # Aliases are joined only when the catalog declares them explicitly.
        aliases = row.get("aliases", [])
        for alias in [name] + (aliases if isinstance(aliases, list) else []):
            if not isinstance(alias, str):
                continue
            if alias in model_provider and model_provider[alias] != provider:
                raise ValueError(f"conflicting catalog provider for model alias: {alias}")
            model_provider[alias] = provider
    local_providers, local_models = _local_provider_metadata(project_root, roots)
    for model, provider in local_models.items():
        if model in model_provider and model_provider[model] != provider:
            raise ValueError(f"local metadata conflicts with catalog provider: {model}")
        model_provider[model] = provider
    builtin_dir = project_root / "src/marianne/instruments/builtins"
    if not builtin_dir.is_dir():
        builtin_dir = _installed_builtin_dir() or builtin_dir
    profile_dirs = [builtin_dir, project_root / ".marianne/instruments"]
    profile_dirs += [root / "instruments" for root in roots if root.name == ".marianne"]
    # Catalog-only providers remain mandatory even without a locally usable route.
    grouped: dict[str, list[dict]] = {provider: [] for provider in set(model_provider.values()) | local_providers}
    for path in sorted(set(builtin_dir.glob("*.yaml")) | set(builtin_dir.glob("*.yml"))):
        declared = _read(path).get("provider")
        if isinstance(declared, str) and declared.strip():
            grouped.setdefault(declared.strip(), [])
    unresolved: list[dict] = []
    skipped: list[dict] = []
    visited: set[Path] = set()
    unresolved_pairs: set[tuple[str, str]] = set()
    for directory in profile_dirs:
        for path in sorted(set(directory.glob("*.yaml")) | set(directory.glob("*.yml"))):
            if path.resolve() in visited:
                continue
            visited.add(path.resolve())
            profile = _read(path)
            instrument = profile.get("name", path.stem)
            if not isinstance(instrument, str):
                raise ValueError(f"profile name must be a string: {path}")
            # Recognized installed instrument definitions have standing active scope.
            # Task aliases, including inherited ones, do not acquire it from model names.
            default_classification = "active" if directory == builtin_dir or instrument in instruments else "unknown"
            classification = profile.get("classification", default_classification)
            if classification not in {"active", "generated"}:
                skipped.append({"path": str(path), "classification": classification})
            # Classification governs edits, not whether a locally used provider
            # gets researched. Read metadata without authorizing profile mutation.
            route = instruments.get(instrument, {})
            route_models = route.get("runs_models", []) if isinstance(route, dict) else []
            if not isinstance(route_models, list):
                raise ValueError(f"catalog runs_models must be a list: {instrument}")
            names: set[str] = set()
            for name in route_models:
                if not isinstance(name, str):
                    continue
                # Catalog prose describing open broker capability is not a model route.
                if name.lower().startswith("any "):
                    skipped.append({"path": str(path), "instrument": instrument,
                                    "model": name, "classification": "generic-route-placeholder"})
                else:
                    names.add(name)
            rows = profile.get("models", [])
            if not isinstance(rows, list):
                raise ValueError(f"profile models must be a list: {path}")
            names.update(row["name"] for row in rows if isinstance(row, dict) and isinstance(row.get("name"), str))
            if isinstance(profile.get("default_model"), str):
                names.add(profile["default_model"])
            explicit_provider = profile.get("provider")
            row_providers = {row["name"]: row["provider"].strip() for row in rows
                             if isinstance(row, dict) and isinstance(row.get("name"), str)
                             and isinstance(row.get("provider"), str) and row["provider"].strip()}
            for declared in [explicit_provider, *row_providers.values()]:
                if isinstance(declared, str) and declared.strip():
                    grouped.setdefault(declared.strip(), [])
            known = {model_provider[n] for n in names if n in model_provider}
            for name in sorted(names):
                provider = model_provider.get(name) or row_providers.get(name)
                if not provider and isinstance(explicit_provider, str) and explicit_provider.strip():
                    provider = explicit_provider.strip()
                association = {"instrument": instrument, "model": name,
                               "path": str(path), "classification": classification}
                if provider in grouped:
                    grouped[provider].append(association)
                else:
                    # Repeated task aliases for one unresolved model do not create
                    # hundreds of identical research questions. Preserve all source paths.
                    key = ("local" if directory != builtin_dir else instrument, name)
                    if key in unresolved_pairs:
                        prior = next(row for row in unresolved if row.get("dedup_key") == list(key))
                        prior["source_paths"].append(str(path))
                        continue
                    unresolved_pairs.add(key)
                    unresolved.append({**association, "id": _unresolved_id(path, instrument, name),
                                       "candidate_providers": sorted(known),
                                       "source_paths": [str(path)], "dedup_key": list(key)})
    if not grouped:
        raise ValueError("no shipped providers found in catalog or builtin declarations")
    if providers is not None and set(providers) != set(grouped):
        raise ValueError("refresh coverage must include all shipped providers and locally declared providers")
    return {"mode": "broad", "admission_version": 3, "catalog": str(catalog_path),
            "providers": [{"id": key, "routes": grouped[key]} for key in sorted(grouped)],
            "unresolved": unresolved, "skipped": skipped}
