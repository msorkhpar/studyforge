"""The In-flight table's SUBJECT VOCABULARY (`W161`): what a subject IS.

**What it does.** Partitions every In-flight subject into the forms
`docs/conventions/board.md` declares: a `W` id, an EPIC TASK (`NS-03`, `SF-19b`), and
the residue, a subject naming neither. ⛔ The residue is read and printed, never
refused (`NS-01/2`).

**How you use it.** `subjects(text)` returns the `Subjects` of the board's text.
`EPIC_TASK` is the epic-task grammar and `EPIC_HOME` how a message names where such a
task is argued. `bijection.py` judges whether each subject has its home, and that is
where these are used.

**Depends on.** `observation.read` for the In-flight table's rows, and `re`. Nothing
else, so the vocabulary imports no arm.

## ⛔ The seam (`W161/5`, cut by `W262`)

⚠️ `bijection.py` stood at R11's ceiling. ⭐ It is cut where `W161` already drew a
line: WHAT a subject is lives here, and WHETHER a subject has its home stays in
`bijection.py`. ⛔ The cut was a pure move: every name still resolves from
`tools.quality.board.bijection`, and a test asserts it.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from tools.quality.board.observation import read

#: ⛔ `W161`: an EPIC TASK id as the In-flight table writes one — `NS-03`, `SF-19b` —
#: and never a finding id, which continues past a `/` (`INT-09/5`). ⭐ The vocabulary
#: this answers to is `docs/conventions/board.md`'s, and it is not restated here.
EPIC_TASK = re.compile(r"(?<![\w/-])[A-Z]{2,}-\d+[a-z]?(?![\w/-])")

#: Where an epic task's argument lives, as the messages and the reading spell it.
EPIC_HOME = "its EPIC, docs/tasks/E<nn>-*.md"


class Subjects(NamedTuple):
    """The In-flight table's subjects, partitioned by the declared vocabulary."""

    w_rows: tuple[tuple[int, str], ...]
    epic_tasks: tuple[str, ...]
    unclassified: tuple[str, ...]


def subjects(text: str) -> Subjects:
    """Partition every observation row's subject: `W` ids, epic tasks, and the residue.

    ⛔ **The residue is a subject naming NEITHER form, and it is READ and printed by
    name, never refused** — the parser admits every subject (`NS-01/2`).
    """
    w_rows, epics, residue = [], [], []
    for row in read(text).rows:
        w_rows.extend((row.line, identifier) for identifier in row.ids)
        found = EPIC_TASK.findall(row.subject)
        epics.extend(found)
        if not row.ids and not found:
            residue.append(row.subject.strip())
    return Subjects(tuple(w_rows), tuple(epics), tuple(residue))
