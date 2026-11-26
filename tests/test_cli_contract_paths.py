"""The expert CLI contract must not name a command path that does not exist.

Why this gate exists (issue #559 review, finding Q1): a commit whose purpose was
removing stale command claims added a ``conductor`` row teaching
``conductor start|stop|restart|reload|status``. Only ``reload`` is real; the
other four are top-level commands. The score-language gate (L14) could not see
it, because L14 checks top-level names only: ``conductor`` was named, so the row
passed however wrong its subcommands were.

This is the narrow, contract-aware form of the reverse direction (skill -> CLI):

* Only backticked spans of the *contract* are read, because the contract is a
  catalogue: a backticked ``<group> <sub>`` is a claim that the path exists.
  Prose is never judged, so "wait for the conductor to settle" is not a path.
* A span is judged only when ``<group>`` is a real command group. The shipped
  skills carry ``mzt maestro`` and ``mzt is`` as adversarial eval bait; those
  begin with a word that is not a group, so they are untouched by construction.
* It checks that named subcommands are real, not that every real subcommand is
  named. ``config show|check`` under-describes a five-subcommand group; that is
  a completeness question for a follow-up, not a false claim.

The Typer registry is the source of truth: the same ``app`` the ``mzt`` entry
point serves.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import typer

from marianne.cli import app

CONTRACT = (
    Path(__file__).resolve().parents[1]
    / "marianne"
    / "skills"
    / "marianne-expert"
    / "contracts"
    / "cli-commands.md"
)

_BACKTICK = chr(96)  # a literal backtick: kept out of the regex source on purpose
_SPAN = re.compile(_BACKTICK + r"([^" + _BACKTICK + r"\n]+)" + _BACKTICK)
# ``<group> <slot>``; the slot may be a pipe list (``start|stop``).
_PATH = re.compile(r"^([a-z][a-z0-9-]*)[ \t]+([a-z][a-z0-9|]*)(?:[ \t]+([a-z][a-z0-9-]*))?$")

# A registry node: the leaf command names directly under a group, and its
# nested command groups by name.
Node = tuple[set[str], dict[str, "Node"]]


def _command_name(command: Any) -> str:
    """A Typer command's CLI name: its explicit name, else its callback's."""
    explicit: str | None = getattr(command, "name", None)
    if explicit:
        return explicit
    callback: Any = getattr(command, "callback", None)
    return (getattr(callback, "__name__", "") or "").replace("_", "-")


def _registry(cli: typer.Typer) -> Node:
    """Leaf command names and, per group, its own registry node.

    ``typer_instance`` is ``None`` for a group that registers no commands; that
    is an empty group, not an error, and is recorded as one.
    """
    leaves = {_command_name(info) for info in cli.registered_commands}
    groups: dict[str, Node] = {}
    for sub in cli.registered_groups:
        name = sub.name or _command_name(sub.typer_instance.info if sub.typer_instance else sub)
        inner: Node = (set(), {}) if sub.typer_instance is None else _registry(sub.typer_instance)
        groups[name] = inner
    return leaves, groups


TOP_LEAVES, GROUPS = _registry(app)


def _leaves_under(node: Node) -> set[str]:
    """Every leaf reachable from a registry node, at any nesting depth.

    Pure: builds a new set rather than growing the node's own, so the registry
    is never changed by a lookup (an in-place ``|=`` here would make the result
    depend on which tests ran first).
    """
    leaves, nested = node
    found = set(leaves)
    for inner in nested.values():
        found |= _leaves_under(inner)
    return found


def _subcommands(group: str) -> set[str]:
    return _leaves_under(GROUPS[group])


def _resolve(group: str, rest: list[str]) -> bool:
    """True when ``group rest...`` is a real leaf or a prefix of one.

    The walk descends through nested groups, so ``instruments catalog`` (a
    group), ``instruments catalog check`` (its leaf) and ``config show`` all
    resolve, while ``conductor start`` and ``instruments catalog bogus`` do not.
    """
    node = GROUPS[group]
    for token in rest:
        leaves, nested = node
        if token in leaves:
            return True  # a leaf; anything after it is an argument, not a command
        if token in nested:
            node = nested[token]
            continue
        return False
    return True  # ran out of tokens inside a real group: a valid prefix


def _false_paths(contract: str) -> list[str]:
    false: list[str] = []
    for line in contract.splitlines():
        for span in _SPAN.findall(line):
            match = _PATH.match(span.strip())
            if not match:
                continue
            group, slot = match.group(1), match.group(2)
            if group not in GROUPS:
                continue  # prose, an option, or eval bait: not a command path
            tail = [match.group(3)] if match.group(3) else []
            for sub in slot.split("|"):
                if sub and not sub.startswith("<") and not _resolve(group, [sub, *tail]):
                    false.append(" ".join([group, sub, *tail]))
    return sorted(set(false))


def test_the_contract_names_only_real_subcommands() -> None:
    """Fires on the Q1 defect class; silent on a contract whose paths exist."""
    assert _false_paths(CONTRACT.read_text(encoding="utf-8")) == []


def test_the_gate_would_have_caught_the_q1_defect() -> None:
    """Prove the gate is not vacuous: the row that shipped in 55ccf6e must fail.

    Without this, an over-narrow pattern could pass on the fixed contract for
    the wrong reason -- and never notice the defect returning.
    """
    shipped = (
        "*   **`conductor`**\n"
        "    *   *Purpose:* Daemon lifecycle sub-app: "
        "`conductor start|stop|restart|reload|status` and related management commands.\n"
    )
    assert _false_paths(shipped) == [
        "conductor restart",
        "conductor start",
        "conductor status",
        "conductor stop",
    ]


def test_real_nested_and_flat_subcommands_are_accepted() -> None:
    """The positive half: every real path passes, including one nested a level
    deeper (``instruments catalog check``), so the gate is not over-tight."""
    lines = [
        "`conductor reload`",
        "`agents list` and `agents run`",
        "`config check` `config init` `config path` `config set` `config show`",
        "`instruments catalog check` `instruments classes tiers`",
        "`telemetry status|consent|export|flush`",
    ]
    assert _false_paths("\n".join(lines)) == []


def test_prose_is_never_read_as_a_command_path() -> None:
    """Ordinary English after a group's name is not a claim about the CLI."""
    assert _false_paths("Wait for the conductor to settle before `mzt run`.\n") == []


def test_eval_bait_is_untouched_by_construction() -> None:
    """The adversarial fixtures name a top-level command that does not exist.
    Its first token is not a group, so the gate never judges the second."""
    assert _false_paths("Eval bait: `mzt maestro` and `mzt is` are not commands.\n") == []


def test_a_group_barely_mentioned_is_not_a_path() -> None:
    """A span that is only a group name, or a real top-level leaf, claims nothing."""
    assert _false_paths("`conductor` `agents` `run` `conductor-status`\n") == []


def test_the_registry_walk_sees_the_real_cli() -> None:
    """Guard the fixture the other cases rest on. If the walk returned an empty
    or partial registry, every span would be skipped as 'not a group' and the
    gate would pass vacuously. The numbers are cross-checked against the
    score-language gate's own command walk in the main repository."""
    assert _subcommands("conductor") == {"reload"}
    assert _subcommands("config") == {"check", "init", "path", "set", "show"}
    assert _subcommands("mail") == {"read", "send"}
    # `instruments` nests its groups one level deeper than every other group.
    # A flat walk would lose these six leaves. (Measured from the registry, and
    # each one confirmed by `uv run mzt <path> --help` exiting 0.)
    assert {name: sorted(inner[0]) for name, inner in GROUPS["instruments"][1].items()} == {
        "catalog": ["check", "convert"],
        "classes": ["check", "show", "tiers", "write"],
    }
    assert not ({""} & (TOP_LEAVES | GROUPS.keys())), "a nameless command in the walk"
    assert len(TOP_LEAVES) + len(GROUPS) == 51


def test_a_lookup_does_not_change_the_registry() -> None:
    """Looking up a group's leaves must be read-only. A lookup that grew the
    node's own set would make later results depend on which tests ran first."""
    before = {name: sorted(node[0]) for name, node in GROUPS.items()}
    _subcommands("instruments")
    _false_paths("`conductor reload`\n")
    assert {name: sorted(node[0]) for name, node in GROUPS.items()} == before
    # The group's *direct* leaves are still only its own: nested ones are not.
    assert GROUPS["instruments"][0] == {"check", "list", "prices", "resolve"}


def test_a_nested_leaf_that_does_not_exist_is_rejected() -> None:
    """The deeper walk must still judge: a real group with a fake leaf fails."""
    assert _false_paths("`instruments classes bogus`\n") == ["instruments classes bogus"]
    assert _false_paths("`instruments catalog bogus --flag`\n") == []  # not a backticked path form
