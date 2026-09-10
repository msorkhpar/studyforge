r"""Delivery planning: the product owner for an integration (SK-08).

**What it does.** Turns *"convert this repository"* into an ordered backlog of
tasks that each end in something a person can be **shown**, with acceptance
the framework can **evaluate**, gated against a **generated** capability index
rather than against thirteen epic documents.

**How you use it.** Through `SKILL.md` beside this file, which is the
procedure. This package is what the skill *calls*:

    from studyforge.skills.delivery import Backlog, capability_index, concentration

    print(capability_index(documents))        # the index a planner reads
    plan = Backlog(...).checked(index)        # the plan, checked against it
    print("\n".join(plan.lines()))            # the durable artifact

**Depends on.** The standard library. ⛔ Not on `corpus`, `archive` or
`validate` — a planner reasons about *work*, not about a corpus's contents —
and ⛔ not on the filesystem: every module here is handed text and gives back
text, so the caller names the documents.

## ⛔ Three rules shape every refusal in this package

1. ⛔ **The planner never reads the extraction source** (R20). What a consumer
   needs is carried in this repository — a ruling, a contract, the authoring
   reference, or the integration catalogue. ⭐ Otherwise every integration
   re-derives from a repository that moves, and the expertise lives nowhere.
2. ⛔ **The planner never patches the framework** (§12). It files a
   **finding**, which becomes a framework task. ⭐ An integrator who can edit
   the framework fixes their own problem and nobody learns anything.
3. ⛔ **The plan is generated, never hand-authored** (R19). A hand-edit to
   anything here is a finding, not a fix.

## ⭐ What each module refuses, because the refusals are the design

| Module | ⛔ What it will not let a plan say |
|---|---|
| `capability` | that a capability lands somewhere the epic documents do not say |
| `task` | that a task ends in a layer, or that a clause is decided by nobody |
| `terminal` | that a corpus finishes somewhere, while leaving later capabilities unaccounted for |
| `backlog` | that a milestone waits on framework work it has not declared a gate for |
| `question` | that a question is open with no way to re-run it, or a stale answer acted on |
| `finding` | that a claim is neither measured here nor received from somebody |
| `export` | that a tracker column maps to a field the backlog does not carry |

## ⚠️ R1 holds here in the direction that is easy to miss

⛔ This package names no source, and the documents it *renders* name no path
inside one. ⭐ A planner is the one place where a source-specific shortcut
would look most reasonable — *"for a corpus of this kind, do this"* — and it
is the one place where it would be copied by every integration that followed.

⚠️ **That sentence originally carried a corpus's name as its example, and the
check in this package's own test suite is what found it** — which is the shape
of the defect exactly: the naming looked like illustration rather than
knowledge, and R1's prose form is where source-specific knowledge accumulates.
"""

from __future__ import annotations

from collections.abc import Iterable

from studyforge.skills.delivery.backlog import Backlog, Milestone
from studyforge.skills.delivery.capability import (
    BANNER,
    Capability,
    Epic,
    Index,
    IndexRefused,
    read_epic,
)
from studyforge.skills.delivery.export import (
    FIELDS,
    GITHUB,
    JIRA,
    PROFILES,
    ExportRefused,
    Profile,
    export,
)
from studyforge.skills.delivery.finding import (
    MARKERS,
    NEGATIVE_OPENING,
    Claim,
    Finding,
    FindingRefused,
)
from studyforge.skills.delivery.question import (
    Answer,
    Question,
    QuestionRefused,
    numbered,
)
from studyforge.skills.delivery.risk import (
    INSIDE,
    OUTSIDE,
    Carrier,
    Concentration,
    RiskRefused,
    concentration,
)
from studyforge.skills.delivery.task import Acceptance, PlanRefused, Task
from studyforge.skills.delivery.terminal import Terminal, TerminalRefused, Unused


def capability_index(documents: Iterable[tuple[str, str]]) -> str:
    """Render the capability index from `(name, text)` pairs of epic documents.

    ⭐ The one call the procedure's first step makes. ⛔ The caller names the
    documents — this package does not know where a plan lives, and the next
    repository's does not live where this one's does.
    """
    return Index.of(read_epic(name, text) for name, text in documents).render()


__all__ = [
    "BANNER",
    "FIELDS",
    "GITHUB",
    "INSIDE",
    "JIRA",
    "MARKERS",
    "NEGATIVE_OPENING",
    "OUTSIDE",
    "PROFILES",
    "Acceptance",
    "Answer",
    "Backlog",
    "Capability",
    "Carrier",
    "Claim",
    "Concentration",
    "Epic",
    "ExportRefused",
    "Finding",
    "FindingRefused",
    "Index",
    "IndexRefused",
    "Milestone",
    "PlanRefused",
    "Profile",
    "Question",
    "QuestionRefused",
    "RiskRefused",
    "Task",
    "Terminal",
    "TerminalRefused",
    "Unused",
    "capability_index",
    "concentration",
    "export",
    "numbered",
    "read_epic",
]
