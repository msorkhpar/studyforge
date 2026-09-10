r"""Rendering a backlog into a tracker — ⛔ as data, so the next tracker is not code.

**What it does.** Turns a `Backlog` into a tracker's import format. The
backlog document is the **source**; an export is a rendering of it, and a
profile is a **name and an ordered list of (column, field) pairs** — nothing
executable.

**How you use it.**

    from studyforge.skills.delivery import JIRA, PROFILES, export

    print(export(backlog, JIRA))
    print(export(backlog, PROFILES["github"]))

**Depends on.** `csv`, `io`, `dataclasses` and this package's `backlog`.
⛔ Nothing else.

## ⛔ A planner that can only speak one tracker is a planner one team can use

⭐ **Jira first, and the format is a profile rather than a hard-coding.** The
next repository may not use Jira, and the cost of that must be one `Profile`
value — ⛔ **not one line of the planner**, which is what the test asserts by
building a profile the shipped code has never seen and exporting through it.

## ⭐ The field registry is the closed set, and it is checked both ways

⛔ **Subset:** a profile naming a field the backlog does not carry is refused
at construction, so a typo in a column mapping fails where it is written
rather than producing a column of empty cells.

⛔ **Coverage:** every field in the registry is reachable from at least one
shipped profile. ⚠️ A field nothing exports is a field nobody maintains, and
it rots in place until somebody's first export is missing it.

## ⚠️ Why CSV, and why the header row is the profile's own columns

⛔ Every tracker in use imports CSV, and none of them agree on a column name.
The header is therefore the profile's words, never the registry's — a mapping
that renamed both ends would be a mapping that maps nothing.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Callable
from dataclasses import dataclass

from studyforge.skills.delivery.backlog import Backlog, Milestone
from studyforge.skills.delivery.task import Task

#: ⛔ The closed set of things a task can export. A profile may name these and
#: nothing else. Each reads one fact from the task and the milestone holding
#: it; ⚠️ none of them computes anything, because a field that computed
#: something would be a second opinion about the plan.
FIELDS: dict[str, Callable[[Task, Milestone], str]] = {
    "id": lambda task, milestone: task.id,
    "title": lambda task, milestone: task.title.strip(),
    "milestone": lambda task, milestone: milestone.id,
    "gate": lambda task, milestone: milestone.gated_by or "",
    "owns": lambda task, milestone: ", ".join(task.owns),
    "depends_on": lambda task, milestone: ", ".join(task.depends_on),
    "effort": lambda task, milestone: str(task.effort),
    "demonstrable": lambda task, milestone: task.demonstrable.strip(),
    "evidence": lambda task, milestone: task.evidence.strip(),
    "acceptance": lambda task, milestone: " · ".join(
        f"{clause.clause.strip()} [{clause.instrument}]" for clause in task.acceptance
    ),
}


class ExportRefused(Exception):
    """Raised when a profile asks for something a backlog does not carry."""


@dataclass(frozen=True, slots=True)
class Profile:
    """One tracker's import format, expressed entirely as data."""

    name: str
    columns: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ExportRefused("a profile with no name cannot be cited in a procedure")
        if not self.columns:
            raise ExportRefused(f"{self.name}: no columns, so the export is a header of nothing")
        unknown = [field for _, field in self.columns if field not in FIELDS]
        if unknown:
            raise ExportRefused(
                f"{self.name}: no such field — {', '.join(sorted(unknown))}. "
                f"⛔ The registry is closed at {', '.join(sorted(FIELDS))}"
            )
        headers = [column for column, _ in self.columns]
        repeated = sorted({name for name in headers if headers.count(name) > 1})
        if repeated:
            raise ExportRefused(f"{self.name}: two columns share a header — {', '.join(repeated)}")

    @property
    def header(self) -> tuple[str, ...]:
        """The tracker's own words, in the tracker's own order."""
        return tuple(column for column, _ in self.columns)

    @property
    def fields(self) -> tuple[str, ...]:
        """Which registry fields this profile reaches."""
        return tuple(field for _, field in self.columns)


#: ⭐ Jira, because it is first and because it is the one with opinions about
#: column names. ⚠️ `Epic Link` carries the milestone: a tracker's hierarchy is
#: its own, and mapping a milestone onto it is exactly what a profile is for.
JIRA = Profile(
    name="jira",
    columns=(
        ("Issue key", "id"),
        ("Summary", "title"),
        ("Epic Link", "milestone"),
        ("Story Points", "effort"),
        ("Description", "demonstrable"),
        ("Acceptance Criteria", "acceptance"),
        ("Blocked By", "depends_on"),
        ("Labels", "gate"),
    ),
)

#: ⭐ And one other, to prove the seam: this profile was added without a line
#: of the planner changing. ⚠️ It reaches `owns` and `evidence`, which Jira
#: does not — between the two, every field in the registry is exported.
GITHUB = Profile(
    name="github",
    columns=(
        ("title", "title"),
        ("body", "demonstrable"),
        ("milestone", "milestone"),
        ("labels", "id"),
        ("assignees", "owns"),
        ("notes", "evidence"),
        ("blocked-by", "depends_on"),
        ("size", "effort"),
        ("acceptance", "acceptance"),
        ("gate", "gate"),
    ),
)

#: The profiles this package ships, by name. ⭐ Adding one is an entry here
#: and a `Profile` value — never a branch anywhere.
PROFILES: dict[str, Profile] = {JIRA.name: JIRA, GITHUB.name: GITHUB}


def export(plan: Backlog, profile: Profile) -> str:
    """Render `plan` in `profile`'s format, one row per task, milestone order."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(profile.header)
    for milestone in plan.milestones:
        for task in milestone.tasks:
            writer.writerow([FIELDS[field](task, milestone) for _, field in profile.columns])
    return out.getvalue()
