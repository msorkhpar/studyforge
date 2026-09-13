"""`W153`: the CARRIER DECLARATION — which rows a branch carries, as its own git description.

**What it does.** Reads `branch.<name>.description` for every local branch, and hands
`unclaimed.unnamed()` the carriers it may treat as claimed: a branch no In-flight row names
whose description names only OPEN register rows the table carries nowhere else. ⛔ **Every
other declaration is REFUSED and printed with its reason**, and a refused branch stays on
the gate exactly as if it had declared nothing.

**How you use it.** The office that cuts a carrier declares it in the same invocation:
`git switch -c fix/W153-slug <ref> && git config branch.fix/W153-slug.description W153`.
`read(root)` returns a `Reading`; `judge(reading, heads, rows, text)` returns
`(the branches taken as claimed, the two lines reporting it)`.

**Depends on.** `tools.workspace.git`, `board.register` for the register and its ids,
`board.observation` for the row type and `board.verdict` for `tokens`. ⛔ **Nothing in
`tools.quality.CHECKS` imports this**: config is untracked state (Ruling 80).

## ⛔ Why the declaration is the BRANCH DESCRIPTION

⭐ **The contract, and each refused candidate, are in `docs/conventions/board.md` under
`W153`.** In short: the register cannot be written in a wave with no register round
(`PO-50/7`), a tracked file needs a commit, so it cannot be read at `0` ahead, and a branch
name carries no row id (`fix/INT06-9-highlight-languages` carried `W243`). ⭐ **A
description needs no commit, is shared by every worktree, and is deleted with its branch.**

## ⛔ Why it is not a THIRD COPY of the dispatch

⭐ **The declaration is read ONLY where the register is silent.** A branch any row claims
never has its description read, and a declared id that the table carries on another branch
is refused. ⛔ **The register never edits a description, so when a fact changes exactly one
file changes.** `inflight.py` must never read one either: a generated table asserted
against git would assert git against itself (Ruling 231(c), `W125`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from tools.quality.board.observation import Observation
from tools.quality.board.register import identifiers, is_closed, register
from tools.quality.board.verdict import tokens
from tools.workspace import git

#: The git config keys this module reads, as `git config --get-regexp` matches them.
KEY = r"^branch\..*\.description$"
PREFIX, SUFFIX = "branch.", ".description"


@dataclass(frozen=True)
class Reading:
    """Every branch description git holds, and whether git answered at all."""

    #: `{branch: its description}`, for every description key, branch present or not.
    descriptions: dict[str, str] = field(default_factory=dict)
    #: ⛔ `""` when git answered, else git's own error text. A failure takes nothing off.
    failed: str = ""


def read(root: Path) -> Reading:
    """Read every `branch.<name>.description` key. ⛔ Exit `1` from git is *none*, not failure.

    ⭐ **`--local`: the repository's own config, which every linked worktree shares** — never
    the user's global file. ⛔ **A failure is reported by its EXIT CODE alone**, because git's
    error text names the config file by its absolute path, and that path is personal (R7).
    """
    told = git(root, "config", "--local", "-z", "--get-regexp", KEY)
    if told.returncode == 1:
        return Reading()
    if told.returncode != 0:
        return Reading(failed=f"git config exited {told.returncode}")
    found: dict[str, str] = {}
    for entry in told.stdout.split("\0"):
        key, _, value = entry.partition("\n")
        if key.startswith(PREFIX) and key.endswith(SUFFIX):
            found[key[len(PREFIX) : -len(SUFFIX)]] = value
    return Reading(found)


def _refusal(ids: list[str], known: dict[str, bool], carried: dict[str, str]) -> str:
    """Return why a declaration naming `ids` is refused, or `""` when it is accepted."""
    if not ids:
        return "names no W row id"
    for row in ids:
        if row not in known:
            return f"{row} has no register row"
        if known[row]:
            return f"{row} is closed in the register"
        if row in carried:
            return f"the In flight table carries {row} on {carried[row]}"
    return ""


def judge(
    reading: Reading, heads: Iterable[str], rows: tuple[Observation, ...], text: str
) -> tuple[frozenset[str], list[str]]:
    """Split the declarations into ACCEPTED, SUPERSEDED by a row, and REFUSED.

    ⛔ **Only an accepted declaration leaves the gate's population.** A superseded one is
    counted and never read, because the row answers there. A refused one stays on the gate.
    """
    present = set(heads)
    claimed = {branch for row in rows for branch in tokens(row.checkout)}
    carried = {i: branch for row in rows for branch in tokens(row.checkout) for i in row.ids}
    known: dict[str, bool] = {}
    for _line, ids, cell in register(text):
        for row in ids:
            known[row] = known.get(row, False) or is_closed(cell)
    accepted: dict[str, str] = {}
    refused: list[str] = []
    superseded = 0
    for branch, value in sorted(reading.descriptions.items()):
        if branch not in present:
            continue
        if branch in claimed:
            superseded += 1
            continue
        ids = identifiers(value)
        reason = _refusal(ids, known, carried)
        if reason:
            refused.append(f"{branch} ({reason})")
        else:
            accepted[branch] = "+".join(ids)
    label = "carrier declarations (git config branch.<branch>.description)"
    if reading.failed:
        return frozenset(), [
            f"  ⛔ {label}: NOT READ — git said {reading.failed!r}. ⚠️ Nothing is taken off "
            f"the gate, so every carrier stays named as if undeclared."
        ]
    lines = [
        f"  ⭐ carriers DECLARED by their own branch description, named by no row "
        f"({len(accepted)}): " + " ".join(f"{b}={i}" for b, i in accepted.items())
        if accepted
        else f"  {label}, named by no row: none.",
    ]
    lines[0] += (
        f" — {superseded} more on branches a row already claims, where the row answers and "
        f"the description is never read."
    )
    lines.append(
        f"  ⛔ carrier declarations REFUSED ({len(refused)}): {' '.join(refused)} — each "
        f"branch stays on the gate lines above as if it had declared nothing."
        if refused
        else "  carrier declarations refused: none."
    )
    return frozenset(accepted), lines
