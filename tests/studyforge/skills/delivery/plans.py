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
    Components,
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
**Owns** `address/`
**Context** ~10k

Definition.

### SF-02 — Corpus manifest ⭐ SHOUTING THAT IS NOT PART OF THE NAME
**Milestone** **M2** (step 2.1) · **Depends on** SF-01 · **Team** pair
**Owns** `corpus/manifest/`
**Context** ~10k

Definition.

### ⛔ A carried ruling, which is not a task and declares no milestone

It has no declaration line, so the walk passes over it.
"""

EPIC_TWO = """# E05 — Serving and execution

### SF-20 — Command runner
**Milestone** **M5** · **Depends on** SF-02 · **Team** solo
**Owns** `execute/`
**Context** ~10k

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


#: A pin document declaring one component that is not this one, and the epic
#: that owns inside it. ⭐ `W92`'s distinction APPLIES over this pair.
PINS = """{
  "workspace_api": 1,
  "components": [
    {"name": "here", "where": "self", "status": "present"},
    {"name": "elsewhere-component", "where": "sibling", "status": "present"}
  ]
}"""

#: ⛔ And a pin document that declares nothing but this repository, which is
#: the document set where the distinction does NOT apply.
NO_PINS = """{
  "workspace_api": 1,
  "components": [{"name": "here", "where": "self", "status": "present"}]
}"""

EPIC_ELSEWHERE = """# E12 — A shared component

### TC-00 — The runner image
**Milestone** M5 · **Depends on** — · **Team** solo
**Owns** `elsewhere-component/docker/` — the image
**Context** ~10k

### TC-01 — A row that declares no path at all
**Milestone** M5 · **Depends on** TC-00 · **Team** solo
**Owns** the release record
**Context** ~5k
"""


#: ⛔ `M10` declared BEFORE `M9`: neither a lexical sort (`M1`, `M10`, `M2`,
#: `M9`) nor a numeric one reproduces the declared order (`W247`).
WIDE_SEQUENCE = "### M1 — One\n### M2 — Two\n### M10 — Ten\n### M9 — Nine\n"

#: The epic that goes with it: two-digit milestone ids, read as ids (`W247`).
WIDE_EPIC = """# E12 — Wide ids

### SF-40 — Lands at ten
**Milestone** **M10** · **Depends on** — · **Team** solo
**Owns** `wide/ten.py`

### SF-41 — Lands at nine
**Milestone** M9 · **Depends on** SF-40 · **Team** solo
**Owns** `wide/nine.py`
"""


def sequence() -> Sequence:
    """The fixture's declared order: M1, M2, M6, M5."""
    return read_sequence("README.md", SEQUENCE)


def components() -> Components:
    """The declaration under which one fixture epic is delivered elsewhere."""
    return Components.read(PINS, SEQUENCE)


def index() -> Index:
    """The two-epic index: capabilities at M1, M2 and M5, none at M6, one cancelled."""
    return Index.of(
        (read_epic("E01.md", EPIC_ONE), read_epic("E05.md", EPIC_TWO)),
        sequence(),
        Components.none(),
    )


def sided_index() -> Index:
    """A three-epic index over a workspace that pins a component somewhere else."""
    return Index.of(
        (
            read_epic("E01.md", EPIC_ONE),
            read_epic("E05.md", EPIC_TWO),
            read_epic("E12.md", EPIC_ELSEWHERE),
        ),
        sequence(),
        components(),
    )


def wide_index() -> Index:
    """The `W247` index: milestone ids of two digits, in their declared order."""
    return Index.of(
        (read_epic("E12.md", WIDE_EPIC),),
        read_sequence("README.md", WIDE_SEQUENCE),
        Components.none(),
    )


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


def live_pins() -> str:
    """This repository's own workspace pin document, as text."""
    return (_tasks().parents[1] / "workspace.json").read_text("utf-8")


def live_components() -> Components:
    """The components this repository pins, and the shorthand its task index declares."""
    return Components.read(live_pins(), (_tasks() / "README.md").read_text("utf-8"))


def live_index() -> Index:
    """This repository's own index, in its own declared order."""
    return Index.of(read_epics(live_epics()), live_sequence(), live_components())


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
