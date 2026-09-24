r"""Delivery planning: the product owner for an integration.

**What it does.** Turns *"convert this repository"* into an ordered backlog of
tasks that each end in something a person can be **shown**, with acceptance
the framework can **evaluate**, checked against what the **installed**
framework offers now.

**How you use it.** Through `SKILL.md` beside this file, which is the
procedure. This package is what the skill *calls*:

    from studyforge.skills.delivery import Backlog, Offer, concentration

    offer = Offer.installed()                        # what this installation offers
    print(offer.render())                            # the document a planner reads
    plan = Backlog(...).checked(offer)               # the plan, checked against it
    print("\n".join(plan.lines()))                   # the durable artifact

**Depends on.** The standard library. ⛔ Not on `corpus`, `archive` or
`validate` — a planner reasons about *work*, not about a corpus's contents —
and ⛔ not on the filesystem: every module here is handed data and gives back
text. ⭐ The one exception is `offer`, which reads the installed command table
and skill locator through their own modules and never a path, so a planner
needs no checkout.

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
| `offer` | that a capability is offered twice, or that a plan can add one to the installation |
| `refusal` | ⭐ nothing — it is the FORM the rest take once they found several (R6) |
| `task` | that a task ends in a layer, or that a clause is decided by nobody |
| `terminal` | that a corpus finishes somewhere, leaving an offered capability unaccounted for |
| `backlog` | that a task waits on something nobody offers and no finding names |
| `question` | that a question is open with no way to re-run it, or a stale answer acted on |
| `finding` | that a claim is neither measured here nor received from somebody |
| `findings_log` | that a run closes with no log, or a finding in it with no disposition slot |
| `export` | that a tracker column maps to a field the backlog does not carry |

## ⚠️ R1 holds here in the direction that is easy to miss

⛔ This package names no source, and the documents it *renders* name no path
inside one. ⭐ A planner is the one place where a source-specific shortcut
would look most reasonable — *"for a corpus of this kind, do this"* — and it
is the one place where it would be copied by every integration that followed.

⚠️ **A corpus's name used as an example is the same defect**: naming looks like
illustration rather than knowledge, and R1's prose form is where
source-specific knowledge accumulates. This package's own test suite checks it.
"""

from __future__ import annotations

from studyforge.skills.delivery.backlog import Backlog, Milestone
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
from studyforge.skills.delivery.findings_log import (
    ANSWERS,
    LOG,
    QUESTION,
    Disposition,
    Entry,
    FindingsLog,
    LogRefused,
    closing,
)
from studyforge.skills.delivery.offer import BANNER, Capability, Offer, OfferRefused
from studyforge.skills.delivery.question import (
    Answer,
    Question,
    QuestionRefused,
    numbered,
)
from studyforge.skills.delivery.refusal import one_or_all
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

__all__ = [
    "ANSWERS",
    "BANNER",
    "FIELDS",
    "GITHUB",
    "INSIDE",
    "JIRA",
    "LOG",
    "MARKERS",
    "NEGATIVE_OPENING",
    "OUTSIDE",
    "PROFILES",
    "QUESTION",
    "Acceptance",
    "Answer",
    "Backlog",
    "Capability",
    "Carrier",
    "Claim",
    "Concentration",
    "Disposition",
    "Entry",
    "ExportRefused",
    "Finding",
    "FindingRefused",
    "FindingsLog",
    "LogRefused",
    "Milestone",
    "Offer",
    "OfferRefused",
    "PlanRefused",
    "Profile",
    "Question",
    "QuestionRefused",
    "RiskRefused",
    "Task",
    "Terminal",
    "TerminalRefused",
    "Unused",
    "closing",
    "concentration",
    "export",
    "numbered",
    "one_or_all",
]
