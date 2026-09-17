"""Worked plans and epic documents the delivery tests share.

Built here rather than in each module for the reason `corpora.py` exists next
door: a fixture retyped in nine files is nine fixtures that drift.

⚠️ **Every corpus here is invented.** The framework names no source (R1), and
a test fixture that borrowed a real repository's plan would teach the next
reader that borrowing one is normal.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.skills.delivery import (
    Acceptance,
    Backlog,
    Index,
    Milestone,
    Sequence,
    Task,
    Terminal,
    Unused,
    read_epic,
    read_epics,
    read_sequence,
)

#: Two epic documents in the shape this repository writes them, small enough
#: that a reader of a failing test can hold the whole population in their head.
EPIC_ONE = """# E01 — Core contracts

Prose the walk must not read as a task.

### SF-01 — Logical address model
**Milestone** M1 · **Depends on** — · **Team** solo

Definition.

### SF-02 — Corpus manifest ⭐ SHOUTING THAT IS NOT PART OF THE NAME
**Milestone** **M2** (step 2.1) · **Depends on** SF-01 · **Team** pair

Definition.

### ⛔ A carried ruling, which is not a task and declares no milestone

It has no declaration line, so the walk passes over it.
"""

EPIC_TWO = """# E05 — Serving and execution

### SF-20 — Command runner
**Milestone** **M5** · **Depends on** SF-02 · **Team** solo

### SF-99 — ⛔ CANCELLED 2026-09-10
**Milestone** — · **Depends on** — · **Team** —
"""


#: The document that declares the order milestones run in. ⛔ **Deliberately
#: NOT id order:** `M6` runs before `M5`, and it carries no capability, so an
#: index that sorted by id — or dropped an empty milestone — reads it wrong.
#: The decoy heading names milestones and is not a milestone section.
SEQUENCE = """# A task index

### M1 — One page renders

### M2 — A corpus is readable

### ⛔ REORDERED — `M2` → `M6` → `M5`

### M6 — A gate with no framework rows

### M5 — It runs code
"""


#: ⛔ `M10` declared BEFORE `M9`: neither a lexical sort (`M1`, `M10`, `M2`, `M9`)
#: nor a numeric one (`M1`, `M2`, `M9`, `M10`) reproduces the declared order.
WIDE_SEQUENCE = "### M1 — One\n### M2 — Two\n### M10 — Ten\n### M9 — Nine\n"

#: The epic that goes with it: two-digit milestone ids, read as ids (`W247`).
WIDE_EPIC = """# E12 — Wide ids

### SF-40 — Lands at ten
**Milestone** **M10** · **Depends on** — · **Team** solo

### SF-41 — Lands at nine
**Milestone** M9 · **Depends on** SF-40 · **Team** solo
"""


def sequence() -> Sequence:
    """The fixture's declared order: M1, M2, M6, M5."""
    return read_sequence("README.md", SEQUENCE)


def index() -> Index:
    """The two-epic index: capabilities at M1, M2 and M5, none at M6, one cancelled."""
    return Index.of((read_epic("E01.md", EPIC_ONE), read_epic("E05.md", EPIC_TWO)), sequence())


def wide_index() -> Index:
    """The `W247` index: milestone ids of two digits, in their declared order."""
    return Index.of((read_epic("E12.md", WIDE_EPIC),), read_sequence("README.md", WIDE_SEQUENCE))


def _tasks() -> Path:
    return Path(__file__).resolve().parents[4] / "docs/tasks"


def live_epics() -> list[tuple[str, str]]:
    """This repository's own epic documents, as `(name, text)` pairs.

    ⭐ The generator is exercised against the real population as well as the
    small one: a parser that only ever meets its own fixture has been tested
    against the shape somebody imagined.
    """
    return [(p.name, p.read_text("utf-8")) for p in sorted(_tasks().glob("E*.md"))]


def live_sequence() -> Sequence:
    """This repository's own declared milestone order, read from its task index."""
    return read_sequence("README.md", (_tasks() / "README.md").read_text("utf-8"))


def live_index() -> Index:
    """This repository's own index, in its own declared order."""
    return Index.of(read_epics(live_epics()), live_sequence())


def terminal() -> Terminal:
    """A corpus that finishes at M2, accounting for everything after it."""
    return Terminal(
        milestone="M2",
        evidence=("0 runnable units", "0 graders anywhere in the repository"),
        unused=(Unused("SF-20", "no unit asks the reader to run anything"),),
    )


def reading_task(name: str = "C-01", **overrides: object) -> Task:
    """A task that ends in something a person can be shown."""
    fields: dict[str, object] = {
        "id": name,
        "title": "One unit opens in a browser",
        "demonstrable": "the reader opens unit 1 and every block renders",
        "acceptance": (Acceptance("the archive validates", runs="python3 -m pytest tests"),),
        "owns": ("ingest/read.py",),
    }
    fields.update(overrides)
    return Task(**fields)  # type: ignore[arg-type]


def backlog(**overrides: object) -> Backlog:
    """A two-milestone plan that passes every check."""
    fields: dict[str, object] = {
        "corpus": "a repository of teaching prose",
        "milestones": (
            Milestone(
                id="C1",
                name="the material reads",
                gated_by="M1",
                tasks=(reading_task("C-01", depends_on=("SF-01",)),),
            ),
            Milestone(
                id="C2",
                name="the whole corpus reads",
                gated_by="M2",
                tasks=(
                    reading_task(
                        "C-02",
                        depends_on=("C-01", "SF-02"),
                        owns=(),
                        evidence="a re-run of the generator that changes no byte",
                        effort=4,
                    ),
                ),
            ),
        ),
        "terminal": terminal(),
    }
    fields.update(overrides)
    return Backlog(**fields)  # type: ignore[arg-type]
