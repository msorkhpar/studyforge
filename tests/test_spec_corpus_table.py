"""The spec's corpus table, read against the corpora this workspace pins (`W339`).

Mirrors no source module. ⭐ It answers a clause no unit test can: *a row of the
spec's corpus table that contradicts a pinned corpus's manifest is caught
rather than read.*

## ⛔ Why the table is worth an instrument

⚠️ **A planner reads that table's *Graders* column to decide whether a corpus
enters the execution track** (spec §11.0, C5). It named a file as one corpus's
graders for rounds after the user ruled that file out (`Q5`), because nothing
read the table against anything. ⭐ **The manifest is the corpus's own
declaration**, and `exercises: false` says it sets no graded work — so a row
claiming graders for that corpus is a claim the corpus refutes.

## ⚠️ What it reads, and what it does not

- ⭐ **The manifest at the PINNED commit**, through `git show`, never the
  sibling's working tree: the pin is what this workspace says it builds with,
  and a checkout on another branch is not the workspace. ⛔ Read-only (R3).
- ⛔ **Only one direction is asserted**: `exercises: false` ⇒ the cell claims no
  graders. ⚠️ `exercises: true` does not imply graders — an ungraded exercise
  is a real third state (§7, C5) — so the converse would refuse a true row.
- ⚠️ **A sibling that is not on disk is not read**, and the sweep SKIPS SAYING
  SO when it could read no manifest at all — which is the pinned image, where
  only the checkout is mounted (Ruling 204). ⭐ The refusal half is held on a
  synthetic table below, so the image still proves the instrument can go red.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.harness.workspace import git, holds, read
from tests.studyforge.corpus.placement.test_corpora import WORKSPACE_ENV, workspace_root
from tests.support import repository_root

#: The document the table lives in.
SPEC = Path("docs") / "specs" / "2026-09-08-studyforge-v1-design.md"

#: The heading the table sits under; the first table after it is the one read.
TABLE_HEADING = "### The four shapes the contracts must fit"

#: The column naming a corpus, and the column this instrument reads.
SOURCE = "Source"
GRADERS = "Graders"

#: What a cell starts with when it claims no graders.
NO_GRADERS = "none"

#: The manifest's filename at a corpus's root (spec §4).
MANIFEST = "corpus.json"


def plain(cell: str) -> str:
    """A cell's text without Markdown emphasis or code marks, trimmed."""
    return cell.replace("`", "").replace("*", "").strip()


def table_rows(text: str) -> dict[str, dict[str, str]]:
    """`{source: {column: cell}}` for the first table under `TABLE_HEADING`.

    ⛔ `{}` when the heading or its table is missing — the caller asserts it is
    not, so a moved heading fails loudly instead of sweeping nothing.
    """
    _, found, after = text.partition(TABLE_HEADING)
    if not found:
        return {}
    lines = after.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("|")), None)
    if start is None:
        return {}
    table = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    header, body = table[0], table[2:]
    rows = [dict(zip(header, cells, strict=True)) for cells in body]
    return {plain(row[SOURCE]): row for row in rows}


def claims_no_graders(cell: str) -> bool:
    """Say whether a *Graders* cell states that the corpus has none."""
    return plain(cell).lower().startswith(NO_GRADERS)


def contradictions(rows: dict[str, dict[str, str]], manifests: dict[str, dict]) -> list[str]:
    """Every way the table disagrees with a manifest, one sentence each, sorted (R10)."""
    found = []
    for name, manifest in sorted(manifests.items()):
        row = rows.get(name)
        if row is None:
            found.append(f"{name} is pinned with a manifest and the spec's table has no row for it")
        elif manifest.get("exercises") is False and not claims_no_graders(row[GRADERS]):
            found.append(
                f"{name}: the table's {GRADERS} cell claims graders and the pinned manifest "
                f"declares exercises: false"
            )
    return found


def pinned_manifests() -> tuple[dict[str, dict], list[str]]:
    """`({name: manifest}, [unread name])` for every present sibling component.

    ⭐ A component whose pinned commit carries no manifest is not a corpus yet
    and is neither: it has nothing to contradict. ⚠️ One that is not on disk,
    or does not hold its pinned commit, is UNREAD and named as such.
    """
    workspace = workspace_root()
    manifests, unread = {}, []
    for component in read(repository_root()):
        if component.where != "sibling" or not component.present:
            continue
        checkout = workspace / component.name
        if not checkout.is_dir() or not holds(checkout, component.commit):
            unread.append(component.name)
            continue
        shown = git(checkout, "show", f"{component.commit}:{MANIFEST}")
        if shown.returncode == 0:
            manifests[component.name] = json.loads(shown.stdout)
    return manifests, unread


def spec_rows() -> dict[str, dict[str, str]]:
    """The real table, read from the tracked spec."""
    return table_rows((repository_root() / SPEC).read_text(encoding="utf-8"))


# --- the table itself -------------------------------------------------------


def test_the_table_is_found_and_every_row_has_a_graders_cell():
    # ⛔ Ruling 48: a table that parsed to nothing would pass every sweep below
    # by never running.
    rows = spec_rows()
    assert rows, f"no table under {TABLE_HEADING!r} in {SPEC}"
    assert all(row.get(GRADERS) for row in rows.values()), rows


# --- the refusal, held on a synthetic table (Ruling 191) ---------------------

#: One corpus's row, as the spec carried it before `W339`, and as it reads now.
CLAIMED = "| X | 1 | 3 | no build file | prose scenarios in `Scenarios.md` |"
DENIED = "| X | 1 | 3 | no build file | **none** — amended below |"


def synthetic(row: str) -> dict[str, dict[str, str]]:
    """A one-row table under the real heading and the real columns."""
    header = "| Source | Container levels | Units | Runnable | Graders |"
    return table_rows(f"{TABLE_HEADING}\n\n{header}\n|---|---|---|---|---|\n{row}\n\nprose\n")


def test_a_row_claiming_graders_against_exercises_false_is_refused_and_one_denying_them_is_not():
    ruled = {"X": {"exercises": False}}
    assert contradictions(synthetic(CLAIMED), ruled), "the instrument cannot go red"
    assert contradictions(synthetic(DENIED), ruled) == []


def test_a_row_claiming_graders_is_not_refused_when_the_manifest_sets_work():
    # ⚠️ The converse is NOT asserted: `exercises: true` with no grader is C5's
    # ungraded state, so a row saying "none" there is true and must pass too.
    runnable = {"X": {"exercises": True}}
    assert contradictions(synthetic(CLAIMED), runnable) == []
    assert contradictions(synthetic(DENIED), runnable) == []


def test_a_pinned_corpus_the_table_does_not_name_is_refused():
    assert contradictions(synthetic(DENIED), {"Y": {"exercises": False}})


# --- the real table against the real pins ------------------------------------


def test_the_spec_table_agrees_with_every_pinned_corpus_manifest():
    manifests, unread = pinned_manifests()
    if not manifests:
        pytest.skip(
            f"no pinned corpus manifest could be read here (unread: {unread}), so the "
            f"spec's table is proved against no corpus; set {WORKSPACE_ENV} to point at "
            f"the workspace root. The refusal is held on the synthetic table above"
        )
    assert contradictions(spec_rows(), manifests) == []
