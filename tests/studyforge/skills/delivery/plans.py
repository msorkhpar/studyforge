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
    Task,
    Terminal,
    Unused,
    read_epic,
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


def index() -> Index:
    """The two-epic index: three capabilities at M1, M2 and M5, one cancelled."""
    return Index.of((read_epic("E01.md", EPIC_ONE), read_epic("E05.md", EPIC_TWO)))


def live_epics() -> list[tuple[str, str]]:
    """This repository's own epic documents, as `(name, text)` pairs.

    ⭐ The generator is exercised against the real population as well as the
    small one: a parser that only ever meets its own fixture has been tested
    against the shape somebody imagined.
    """
    root = Path(__file__).resolve().parents[4]
    return [(p.name, p.read_text("utf-8")) for p in sorted((root / "docs/tasks").glob("E*.md"))]


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
