"""The In-flight table's SUBJECT VOCABULARY (`W161`): what a subject IS, and where it is defined.

**What it does.** Partitions every In-flight subject into the forms
`docs/conventions/board.md` declares: a `W` id, an EPIC TASK (`NS-03`, `SF-19b`), and
the residue, a subject naming neither. ⛔ The residue is read and printed, never
refused (`NS-01/2`). ⭐ `W262`: it also answers which tasks the epics DEFINE, so an epic
task no epic defines can be named with the epics its prefix points at.

**How you use it.** `subjects(text)` returns the `Subjects` of the board's text.
`epic_definitions(root)` returns every task an epic in that tree defines, and
`undefined_epic_task(identifier, definitions)` is the message naming one that is not.
`bijection.py` judges whether each subject has its home, and that is where these are used.

**Depends on.** `observation.read` for the In-flight table's rows, `register.BOARD` for
where the epics sit, `config` for `read_text`/`relative`, `posixpath`, `pathlib` and `re`.
It imports no arm.

## ⛔ The seam (`W161/5`, cut by `W262`)

⚠️ `bijection.py` stood at R11's ceiling. ⭐ It is cut where `W161` already drew a
line: WHAT a subject is lives here, and WHETHER a subject has its home stays in
`bijection.py`. ⛔ The cut was a pure move: every name still resolves from
`tools.quality.board.bijection`, and a test asserts it.

## ⚠️ `W262`: DECIDED, and DECLARED (Ruling 292)

⭐ **Decided:** a task is defined by a HEADING whose first token is its id (`### NS-03 —`),
in a `docs/tasks/E*.md` of the tree read, so a reading at a ref is over that ref's epics
and there is no second copy of the epic list. A lettered id is its own task (`SF-19b` is
not `SF-19`). A mention in an epic's prose defines nothing.
⚠️ **Declared:** only the In-flight table of `BOARD.md` is read, never the archive or a
frozen record (Ruling 106). Whether the epic named is the RIGHT home is not read.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from typing import NamedTuple

from tools.quality.board.observation import read
from tools.quality.board.register import BOARD
from tools.quality.config import read_text, relative

#: ⛔ `W161`: an EPIC TASK id as the In-flight table writes one — `NS-03`, `SF-19b` —
#: and never a finding id, which continues past a `/` (`INT-09/5`). ⭐ The vocabulary
#: this answers to is `docs/conventions/board.md`'s, and it is not restated here.
EPIC_TASK = re.compile(r"(?<![\w/-])[A-Z]{2,}-\d+[a-z]?(?![\w/-])")

#: Where an epic task's argument lives, as the messages and the reading spell it.
EPIC_HOME = "its EPIC, docs/tasks/E<nn>-*.md"

#: ⛔ `W262`: the epics, beside the board, as a glob over the tree read. Derived from
#: `BOARD` rather than typed, so the epics' place has one home.
EPICS = posixpath.join(posixpath.dirname(BOARD), "E*.md")

#: ⛔ `W262`: a heading whose first token is the task's id DEFINES it.
DEFINED = re.compile(r"^#{1,6}[ \t]+([A-Z]{2,}-\d+[a-z]?)(?![\w/-])", re.MULTILINE)


class Subjects(NamedTuple):
    """The In-flight table's subjects, partitioned by the declared vocabulary."""

    w_rows: tuple[tuple[int, str], ...]
    epic_tasks: tuple[str, ...]
    unclassified: tuple[str, ...]
    #: ⭐ `W262`: the epic tasks again, each with its board line, for a finding to name.
    epic_rows: tuple[tuple[int, str], ...] = ()


def subjects(text: str) -> Subjects:
    """Partition every observation row's subject: `W` ids, epic tasks, and the residue.

    ⛔ **The residue is a subject naming NEITHER form, and it is READ and printed by
    name, never refused** — the parser admits every subject (`NS-01/2`).
    """
    w_rows, epics, residue, epic_rows = [], [], [], []
    for row in read(text).rows:
        w_rows.extend((row.line, identifier) for identifier in row.ids)
        found = EPIC_TASK.findall(row.subject)
        epics.extend(found)
        epic_rows.extend((row.line, identifier) for identifier in found)
        if not row.ids and not found:
            residue.append(row.subject.strip())
    return Subjects(tuple(w_rows), tuple(epics), tuple(residue), tuple(epic_rows))


def epic_definitions(root: Path) -> dict[str, str]:
    """`{"NS-03": "docs/tasks/E13-….md"}` for every task an epic in the tree at `root` defines."""
    found: dict[str, str] = {}
    for path in sorted(root.glob(EPICS)):
        for identifier in DEFINED.findall(read_text(path) or ""):
            found.setdefault(identifier, relative(path, root))
    return found


def undefined_epic_task(identifier: str, definitions: dict[str, str]) -> str:
    """Return the message naming an epic task no epic defines, and the epics its prefix names."""
    prefix = identifier.split("-", 1)[0]
    epics = sorted({epic for task, epic in definitions.items() if task.startswith(f"{prefix}-")})
    points = (
        f"its prefix `{prefix}-` points at {', '.join(epics)}"
        if epics
        else f"its prefix `{prefix}-` points at NO epic: none defines a `{prefix}-` task"
    )
    return (
        f"{identifier} is named in the In-flight table as an EPIC TASK, and no {EPICS} "
        f"defines it with a `### {identifier}` heading; {points}. ⛔ An epic task's argument "
        f"is its epic (`W161`), so a subject no epic defines is an argument with no home "
        f"(`W262`, `W161/4`)."
    )
