r"""What the installed framework offers a plan, read from the installation itself.

**What it does.** Holds every capability a delivery plan may use — each
command the installed `studyforge` runs and each skill it ships — and renders
them as the one document a planner reads about the framework. ⭐ The offer is
what is installed NOW: a plan is made against it, and nothing here says what a
later version may add.

**How you use it.**

    from studyforge.skills.delivery import Capability, Offer

    offer = Offer.installed()            # this installation's commands and skills
    offer.ids                            # what a task's `depends_on` may name
    print(offer.render())                # the document the skill's first step prints
    Offer((Capability("studyforge build", "write the site"),))  # a plan's own, in a test

From a shell, `python3 -m studyforge.skills.delivery` prints the same document.

**Depends on.** `dataclasses`, `sys`, `studyforge.exitcodes`, this package's
`refusal`, and two registries the installed package already keeps:
`studyforge.cli.dispatch.VERBS`, the table of commands, and
`studyforge.skills.documents`, the skill locator. ⛔ Nothing else, and in
particular no path: both registries are read through their own modules.

## ⛔ Read from the installation, never typed

A list of capabilities written by hand would be a second copy of the command
table and the skill tree, and the day a verb or a skill is added it is the copy
that is wrong. ⭐ So `installed()` asks the two registries, and a capability
exists here exactly when a reader could run it.

## ⭐ The planner is not one of its own capabilities

The delivery skill is the thing making the plan, so it is never a capability
the plan schedules or forgoes. It is left out by the name of the package this
module is in, never by a name typed here.

## ⛔ A capability the framework lacks is a finding, never an entry

A plan that needs something this offer does not list files a finding against
the framework, and the task that needs it waits on that finding. ⛔ There is
no way to add a capability to the installed offer from a plan: an integrator
who could would be planning against a framework that does not exist.

## ⛔ `__init__` names every duplicate, never the first one

⭐ A refusal names its whole population, so an offer carrying three repeated
ids is refused once, with three reasons.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from studyforge.exitcodes import UNUSABLE
from studyforge.skills.delivery.refusal import one_or_all

#: What a command's capability id opens with: the command a reader types.
COMMAND = "studyforge"

#: What a skill's capability id opens with, before the skill's name.
SKILL = "skill"

#: The skill that makes the plan, by the name of the package holding this module.
PLANNER = __name__.split(".")[-2]

#: How a skill document's first line opens, before the skill's own title.
TITLE_OPENING = "# Skill — "

#: How the command line is used, printed when it is used wrongly.
USAGE = "usage: python3 -m studyforge.skills.delivery"

#: The banner the rendered document opens with.
BANNER = "Read from this installation each time the command runs; nothing here is stored."


class OfferRefused(Exception):
    """Raised when an offer cannot be built, with every reason."""


@dataclass(frozen=True, slots=True)
class Capability:
    """One thing the installed framework does, by the id a plan names it with."""

    id: str
    what: str

    def __post_init__(self) -> None:
        """Refuse a capability with no id or no description."""
        if not self.id.strip() or not self.what.strip():
            raise OfferRefused("a capability needs an id and a sentence saying what it does")

    def row(self) -> str:
        """Render as one row of the offer's table."""
        return f"| `{self.id}` | {self.what.strip()} |"


@dataclass(frozen=True, slots=True)
class Offer:
    """Every capability a plan may use, in the order the installation lists them."""

    capabilities: tuple[Capability, ...]

    def __post_init__(self) -> None:
        """Refuse an empty offer, and name every id offered twice."""
        if not self.capabilities:
            raise OfferRefused("an offer of nothing answers every question with silence")
        named = [capability.id for capability in self.capabilities]
        repeated = sorted({name for name in named if named.count(name) > 1})
        if repeated:
            raise OfferRefused(one_or_all([f"{name} is offered twice" for name in repeated]))

    @classmethod
    def installed(cls) -> Offer:
        """Read this installation's commands and skills, leaving out the planner itself."""
        from studyforge.cli.dispatch import VERBS
        from studyforge.skills import documents

        commands = tuple(
            Capability(f"{COMMAND} {verb.name}", verb.summary) for verb in VERBS.values()
        )
        skills = tuple(
            Capability(f"{SKILL} {name}", _title(documents.text(name), name))
            for name in documents.names()
            if name != PLANNER
        )
        return cls(commands + skills)

    @property
    def ids(self) -> frozenset[str]:
        """Every id a task's `depends_on` may name as a framework capability."""
        return frozenset(capability.id for capability in self.capabilities)

    def render(self) -> str:
        """Render the offer as the document a planner reads, the same on every run."""
        return "\n".join(
            [
                "# What the installed framework offers",
                "",
                f"**{BANNER}**",
                "",
                "⭐ **A plan uses these capabilities, and only these.** Each is available "
                "now, in the framework this command ran from.",
                "",
                "⛔ **A capability a plan needs and this table does not list is a finding "
                "against the framework**, filed with the plan; the task that needs it waits "
                "on the finding.",
                "",
                f"**{len(self.capabilities)} capabilities.**",
                "",
                "| capability | what it does |",
                "|---|---|",
                *(capability.row() for capability in self.capabilities),
                "",
            ]
        )


def _title(document: str, name: str) -> str:
    """Return a skill's title from its document's first line, or its name when it has none."""
    first = document.partition("\n")[0]
    if first.startswith(TITLE_OPENING):
        return first.removeprefix(TITLE_OPENING).strip() or name
    return name


def main(argv: list[str]) -> int:
    """Print what this installation offers; take no argument."""
    if argv:
        sys.stderr.write(f"{USAGE}\n")
        return UNUSABLE
    sys.stdout.write(Offer.installed().render())
    return 0
