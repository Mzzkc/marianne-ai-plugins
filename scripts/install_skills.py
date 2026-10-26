#!/usr/bin/env python3
"""Install the shipped Marianne skills into every agent harness on this host.

The plugin tree under ``marianne/skills/`` is the source of truth. Each
harness (Claude Code, Codex, Gemini, ZCode, OpenCode, the shared ``.agents``
surface, the registered Claude plugin cache, and on Ronin the Windows-side
copies) keeps its own copy, and every copy lags the moment the source moves.
This tool makes the distribution a single, repeatable, verified step::

    python3 plugins/scripts/install_skills.py status   # what lags, per root
    python3 plugins/scripts/install_skills.py install  # bring every root current
    python3 plugins/scripts/install_skills.py verify   # prove every root matches

Rules the tool keeps, carried over from the 18 and 26 October scoped
distributions (SCORES/*/skill-distribution*/sync_skills.py, now retired):

- The source must be a clean checkout; the installed revision is whatever
  ``git rev-parse HEAD`` says, never a constant edited by hand.
- Only skill directories that carry a ``SKILL.md`` ship. Byte-identical
  copies, except two deliberate transformations: a portable installation
  note after each SKILL.md front matter (mapping ``${CLAUDE_PLUGIN_ROOT}``
  to the source checkout, or its UNC path for a Windows-side root), and a
  rebuilt ``MANIFEST.sha256`` for ``marianne-expert`` so its own verifier
  passes on the installed bytes. The plugin-cache root gets no note.
- ``marianne/docs`` is installed beside each root (``<harness>/docs``) because
  ``refresh_scope.py`` resolves the instrument catalog by package layout.
  Existing unrelated docs there are kept.
- Every target's exact preimage is archived to a tar before the first write,
  and the archive is byte-verified against the recorded digests. Unrelated
  skills in a root are never touched; a shipped skill's stale extras are.
- ``verify`` recomputes digests on disk; it never trusts a result file.

Harness roots are discovered on the host: a root is installed only if its
parent harness directory exists, so a harness that is not set up here is
reported, not created. Set ``MARIANNE_SKILL_ROOTS`` (colon-separated) to
override discovery. Set ``MARIANNE_SKILL_INSTALL_ALLOW_DIRTY=1`` only to
install an uncommitted working tree on purpose (the tests do); the recorded
revision is then the last commit, not what was installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "marianne"
SKILLS = PLUGIN_ROOT / "skills"
DOCS = PLUGIN_ROOT / "docs"
NOTE_BEGIN = "<!-- MARIANNE-INSTALLATION-NOTE-BEGIN -->"
NOTE_END = "<!-- MARIANNE-INSTALLATION-NOTE-END -->"
NOTE_RE = re.compile(
    re.escape(NOTE_BEGIN).encode() + rb"\n.*?" + re.escape(NOTE_END).encode() + rb"\n\n",
    re.S,
)
MANIFEST_SKILL = "marianne-expert"
EXCLUDED = {"__pycache__"}

# Harness roots relative to the home directory. Each entry is (harness dir,
# skills subdir); the root is installed only when the harness dir exists.
LINUX_ROOTS = [
    (".claude", "skills"),
    (".codex", "skills"),
    (".agents", "skills"),
    (".config/opencode", "skills"),
    (".gemini", "skills"),
    (".zcode", "skills"),
]
PLUGIN_CACHE = Path(".claude/plugins/cache/marianne-ai-plugins/marianne")
WINDOWS_ROOTS = [".codex", ".zcode", ".claude", ".agents", ".continue"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree(root: Path) -> dict[str, str]:
    """Relative path -> sha256 (or symlink target) for every file under root."""
    if not root.exists():
        return {}
    out: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDED for part in rel.parts) or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            out[rel.as_posix()] = "symlink:" + os.readlink(path)
        elif path.is_file():
            out[rel.as_posix()] = digest(path.read_bytes())
    return out


def source_revision(require_clean: bool = True) -> str:
    repo = PLUGIN_ROOT.parent
    rev = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if os.environ.get("MARIANNE_SKILL_INSTALL_ALLOW_DIRTY"):
        require_clean = False  # tests install a working tree mid-edit
    if require_clean:
        dirty = subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain", "--", "marianne"], text=True
        ).strip()
        dirty = "\n".join(line for line in dirty.splitlines() if "__pycache__" not in line)
        if dirty:
            raise SystemExit(f"source tree is not clean under marianne/:\n{dirty}")
    return rev


def shipped_skills() -> list[str]:
    return sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())


def windows_home() -> Path | None:
    """The Windows user profile reachable from this WSL, if any."""
    users = Path("/mnt/c/Users")
    if not users.is_dir():
        return None
    for candidate in sorted(users.iterdir()):
        if (candidate / ".claude").is_dir() or (candidate / ".codex").is_dir():
            return candidate
    return None


def discover_roots() -> list[tuple[Path, str]]:
    """(skills root, kind) for every harness present on this host."""
    override = os.environ.get("MARIANNE_SKILL_ROOTS")
    if override:
        return [(Path(p).expanduser(), "linux") for p in override.split(":") if p]
    home = Path.home()
    roots: list[tuple[Path, str]] = []
    for harness, sub in LINUX_ROOTS:
        if (home / harness).is_dir():
            roots.append((home / harness / sub, "linux"))
    cache = home / PLUGIN_CACHE
    if cache.is_dir():
        for version in sorted(cache.iterdir()):
            if (version / "skills").is_dir():
                roots.append((version / "skills", "plugin-cache"))
    win = windows_home()
    if win is not None:
        for harness in WINDOWS_ROOTS:
            if (win / harness).is_dir():
                roots.append((win / harness / "skills", "windows"))
    return roots


def note_block(kind: str) -> bytes:
    if kind == "windows":
        distro = os.environ.get("WSL_DISTRO_NAME", "Ubuntu")
        mapped = rf"\\wsl.localhost\{distro}" + str(PLUGIN_ROOT).replace("/", "\\")
    else:
        mapped = str(PLUGIN_ROOT)
    return (
        f"{NOTE_BEGIN}\n"
        "## Portable plugin reference mapping\n\n"
        "For this standalone installation, when `${CLAUDE_PLUGIN_ROOT}` is unset,\n"
        f"resolve it to `{mapped}`. This maps reference paths only.\n"
        "Bundled sibling skills and scripts are installed beside this file; plugin\n"
        "docs are also installed at the corresponding harness root for scripts that\n"
        "resolve them by package layout. Use the existing approved WSL route for\n"
        "Linux commands and Linux absolute paths when running from Windows.\n"
        "This installation grants no runtime, service or task authority.\n\n"
        f"{NOTE_END}\n\n"
    ).encode()


def with_note(skill_md: bytes, kind: str) -> bytes:
    end = skill_md.index(b"\n---\n", 4) + 5
    return skill_md[:end] + note_block(kind) + skill_md[end:]


def strip_note(skill_md: bytes) -> bytes:
    return NOTE_RE.sub(b"", skill_md, count=1)


def expected_tree(skill: str, kind: str) -> dict[str, str]:
    """What an installed copy of `skill` must contain for root kind `kind`."""
    src = SKILLS / skill
    out = tree(src)
    if kind != "plugin-cache":
        out["SKILL.md"] = digest(with_note((src / "SKILL.md").read_bytes(), kind))
    if skill == MANIFEST_SKILL:
        out.pop("MANIFEST.sha256", None)  # rebuilt per copy; verified by its own tool
    return out


def rsync(src: Path, dst: Path, delete: bool) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    cmd = ["rsync", "-a", "--checksum", "--no-owner", "--no-group",
           "--exclude=__pycache__", "--exclude=*.pyc"]
    if delete:
        cmd.append("--delete")
    subprocess.run(cmd + [f"{src}/", f"{dst}/"], check=True, capture_output=True)


def stage(skill: str, kind: str, into: Path) -> Path:
    staged = into / skill
    rsync(SKILLS / skill, staged, delete=True)
    if kind != "plugin-cache":
        md = staged / "SKILL.md"
        md.write_bytes(with_note(md.read_bytes(), kind))
    if skill == MANIFEST_SKILL:
        subprocess.run(
            [sys.executable, str(staged / "scripts/release_manifest.py"), "build", str(staged)],
            check=True, capture_output=True,
        )
    return staged


def root_status(root: Path, kind: str) -> dict[str, object]:
    stale = []
    missing = []
    for skill in shipped_skills():
        target = root / skill
        if not target.exists():
            missing.append(skill)
            continue
        actual = tree(target)
        if skill == MANIFEST_SKILL:
            actual.pop("MANIFEST.sha256", None)
        if actual != expected_tree(skill, kind):
            stale.append(skill)
    docs_root = root.parent / "docs"
    docs_stale = any(
        digest((docs_root / rel).read_bytes()) != sha if (docs_root / rel).is_file() else True
        for rel, sha in tree(DOCS).items()
    )
    return {"root": str(root), "kind": kind, "stale": stale, "missing": missing,
            "docs_stale": docs_stale, "current": not (stale or missing or docs_stale)}


def cmd_status(args: argparse.Namespace) -> int:
    rev = source_revision(require_clean=False)
    report = [root_status(root, kind) for root, kind in discover_roots()]
    out = {"host": socket.gethostname(), "revision": rev, "roots": report,
           "all_current": all(r["current"] for r in report)}
    print(json.dumps(out, indent=2) if args.json else _format_status(out))
    return 0 if out["all_current"] else 1


def _format_status(out: dict[str, Any]) -> str:
    lines = [f"source {out['revision'][:12]} on {out['host']}"]
    for r in out["roots"]:
        if r["current"]:
            lines.append(f"  current  {r['root']}")
        else:
            what = []
            if r["missing"]:
                what.append("missing " + ",".join(r["missing"]))
            if r["stale"]:
                what.append("stale " + ",".join(r["stale"]))
            if r["docs_stale"]:
                what.append("docs stale")
            lines.append(f"  LAGS     {r['root']}: {'; '.join(what)}")
    return "\n".join(lines)


def cmd_install(args: argparse.Namespace) -> int:
    rev = source_revision()
    roots = discover_roots()
    skills = shipped_skills()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    evidence = Path(args.evidence_dir).expanduser() / f"{socket.gethostname()}-{stamp}"
    evidence.mkdir(parents=True, exist_ok=False)
    staging = evidence / "staged"
    entries: list[dict[str, Any]] = []
    for root, kind in roots:
        for skill in skills:
            staged = stage(skill, kind, staging / kind)
            entries.append({"target": str(root / skill), "stage": str(staged), "kind": "skill",
                            "before": tree(root / skill), "after": tree(staged)})
        docs_target = root.parent / "docs"
        before = tree(docs_target)
        entries.append({"target": str(docs_target), "stage": str(DOCS), "kind": "docs",
                        "before": before, "after": {**before, **tree(DOCS)}})
    changed = [e for e in entries if e["before"] != e["after"]]
    plan = {"host": socket.gethostname(), "revision": rev, "entries": entries}
    (evidence / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    if args.dry_run:
        print(json.dumps({"status": "planned", "changed_targets": len(changed),
                          "evidence": str(evidence)}))
        return 0
    # Archive every preimage before the first write, then prove the archive.
    archive = evidence / "preimages.tar"
    with tarfile.open(archive, "w") as tf:
        for i, e in enumerate(entries):
            if Path(e["target"]).exists():
                tf.add(e["target"], arcname=f"{i:03d}", recursive=True)
    with tarfile.open(archive) as tf:
        for i, e in enumerate(entries):
            for rel, expected in e["before"].items():
                member = tf.getmember(f"{i:03d}/{rel}")
                if member.issym():
                    actual = "symlink:" + member.linkname
                else:
                    handle = tf.extractfile(member)
                    actual = digest(handle.read()) if handle is not None else ""
                if actual != expected:
                    raise SystemExit(f"preimage archive mismatch: {e['target']}/{rel}")
    for e in entries:
        target = Path(e["target"])
        if tree(target) != e["before"]:
            raise SystemExit(f"target changed since planning: {target}")
        if e["before"] == e["after"]:
            continue
        rsync(Path(e["stage"]), target, delete=e["kind"] == "skill")
        if tree(target) != e["after"]:
            raise SystemExit(f"post-install tree mismatch: {target}")
    result = {"status": "installed", "host": socket.gethostname(), "revision": rev,
              "roots": len(roots), "skill_targets": len(roots) * len(skills),
              "changed_targets": len(changed), "backup": str(archive),
              "backup_sha256": digest(archive.read_bytes())}
    (evidence / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return cmd_verify(args)


def cmd_verify(_args: argparse.Namespace) -> int:
    failures: list[str] = []
    roots = discover_roots()
    for root, kind in roots:
        for skill in shipped_skills():
            target = root / skill
            actual = tree(target)
            if skill == MANIFEST_SKILL:
                actual.pop("MANIFEST.sha256", None)
                proc = subprocess.run(
                    [sys.executable, str(target / "scripts/release_manifest.py"),
                     "verify", str(target)],
                    capture_output=True, text=True,
                )
                if proc.returncode != 0 or "mismatch" in proc.stdout + proc.stderr:
                    failures.append(f"{target}: expert manifest does not verify")
            expected = expected_tree(skill, kind)
            if actual != expected:
                extra = sorted(set(actual) - set(expected))
                gone = sorted(set(expected) - set(actual))
                diff = sorted(k for k in actual if k in expected and actual[k] != expected[k])
                failures.append(
                    f"{target}: extra={extra[:3]} missing={gone[:3]} differ={diff[:3]}"
                )
        for rel, sha in tree(DOCS).items():
            path = root.parent / "docs" / rel
            if not path.is_file() or digest(path.read_bytes()) != sha:
                failures.append(f"{root.parent / 'docs' / rel}: docs differ from source")
    out = {
        "host": socket.gethostname(),
        "revision": source_revision(require_clean=False),
        "roots": [str(r) for r, _ in roots],
        "failures": failures,
        "status": "verified" if not failures else "FAILED",
    }
    print(json.dumps(out, indent=2 if failures else None))
    return 0 if not failures else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("status", help="report which harness roots lag the source")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)
    i = sub.add_parser("install",
                       help="install every shipped skill into every harness root, then verify")
    i.add_argument("--dry-run", action="store_true",
                   help="plan and write evidence; write nothing to any root")
    i.add_argument("--evidence-dir", default="~/.marianne/skill-installs",
                   help="where plan, preimage archive and result land")
    i.set_defaults(func=cmd_install)
    v = sub.add_parser("verify", help="recompute every installed copy against the source")
    v.set_defaults(func=cmd_verify)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
