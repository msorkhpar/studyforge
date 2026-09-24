r"""Where the work actually sits — ⛔ including where it sits in somebody else's repository.

**What it does.** Ranks the carriers of a plan's work and says how
concentrated it is, over a population that is **not** limited to the target
repository's own tasks.

**How you use it.**

    from studyforge.skills.delivery import Carrier, concentration

    report = concentration(backlog.tasks, outside=(Carrier("AB-28", "the framework", 8),))
    print("\n".join(report.lines()))

**Depends on.** `dataclasses` and this package's `task`. ⛔ Nothing else.

## ⛔ *"Most tasks are small"* is false comfort

⭐ A plan where a few tasks carry most of the work says so, out loud, with the
share. ⚠️ The mean is the number that hides it: eleven one-day tasks and one
twelve-day task average out to something reassuring.

## ⛔ And the risk is not all inside the target repository

⚠️ **The current shape of a plan cannot express where an integration's risk
actually sits.** A corpus whose own plan is six small tasks, all of which wait
on a framework milestone that has not started, has a *small plan* and a *large
risk* — and a concentration report that can only see its own tasks reports the
first and misses the second entirely.

⭐ **So `outside` is a required argument and never a defaulted one.** An
integration with nothing outside says so by passing an empty declaration;
⛔ one that simply never thought about it cannot get a report at all, which is
the only way a missing thought becomes visible.

## ⚠️ Why the threshold is a fraction of the *population*, not a fixed count

⛔ A rule like *"flag the top three"* is meaningless at four carriers and
blind at forty. The report answers *how few carriers reach half the work*,
which is a statement about the shape and travels between plans of any size.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from studyforge.skills.delivery.task import Task

#: The share of the work whose carriers the headline names. ⭐ Half, because
#: *"three tasks are half of this plan"* is a sentence a reader acts on.
CONCENTRATION_SHARE = 0.5

#: How a carrier that is not in the target repository is labelled in the
#: report. ⛔ A literal, so a reader scanning the table can find every one.
OUTSIDE = "outside this repository"

#: And its counterpart, so neither side is the unmarked default.
INSIDE = "this repository"


class RiskRefused(Exception):
    """Raised when a plan cannot be ranked, with what was not declared."""


@dataclass(frozen=True, slots=True)
class Carrier:
    """One thing that carries work, wherever it lives."""

    id: str
    where: str
    effort: int

    def __post_init__(self) -> None:
        """Refuse a carrier that names no work, or no place."""
        if not self.id.strip() or not self.where.strip():
            raise RiskRefused("a carrier names what it is and where it lives")
        if self.effort < 1:
            raise RiskRefused(f"a carrier's effort is {self.effort}, which is not work")

    @property
    def is_outside(self) -> bool:
        """True when this carrier is not in the target repository."""
        return self.where != INSIDE

    def row(self, total: int) -> str:
        """Render as one row of the concentration table."""
        share = 100 * self.effort / total
        return f"| `{self.id}` | {self.where} | {self.effort} | {share:.0f}% |"


@dataclass(frozen=True, slots=True)
class Concentration:
    """The ranked carriers, and what their shape says."""

    carriers: tuple[Carrier, ...]

    @property
    def total(self) -> int:
        """All the work, inside and out."""
        return sum(carrier.effort for carrier in self.carriers)

    @property
    def outside_share(self) -> float:
        """⭐ The fraction of the work that is in nobody-here's hands."""
        outside = sum(c.effort for c in self.carriers if c.is_outside)
        return outside / self.total

    @property
    def heaviest(self) -> tuple[Carrier, ...]:
        """The fewest carriers reaching `CONCENTRATION_SHARE` of the work."""
        reached, taken = 0, []
        for carrier in self.carriers:
            taken.append(carrier)
            reached += carrier.effort
            if reached >= CONCENTRATION_SHARE * self.total:
                break
        return tuple(taken)

    @property
    def concentrated(self) -> bool:
        """True when a minority of the carriers hold half the work."""
        return len(self.heaviest) * 2 < len(self.carriers)

    def headline(self) -> str:
        """Render the sentence a reader acts on, with both numbers in it."""
        few, all_of_them = len(self.heaviest), len(self.carriers)
        share = 100 * self.outside_share
        verdict = "⛔ CONCENTRATED" if self.concentrated else "⭐ spread"
        return (
            f"**{verdict}: {few} of {all_of_them} carriers hold half of {self.total} "
            f"units of work, and {share:.0f}% of it is {OUTSIDE}.**"
        )

    def lines(self) -> list[str]:
        """Render the whole report, ⛔ the full population and not a top slice."""
        return [
            "## Concentration risk",
            "",
            self.headline(),
            "",
            "| carrier | where | effort | share |",
            "|---|---|---|---|",
            *(carrier.row(self.total) for carrier in self.carriers),
        ]


def concentration(
    tasks: Sequence[Task], *, outside: Sequence[Carrier] | None = None
) -> Concentration:
    """Rank a plan's carriers — ⛔ refusing until `outside` has been declared.

    `outside` is where this integration's risk sits that is not in the target
    repository: a framework task that gates it, a shared component that does
    not exist yet, a person who is the only one who can answer something.
    ⭐ Pass `()` to declare there is none. ⛔ Omitting it is refused.
    """
    if outside is None:
        raise RiskRefused(
            "⛔ concentration() will not rank against an undeclared outside. "
            "A plan whose risk sits in another repository reads as a small plan. "
            "Pass outside=() to declare there is none"
        )
    if not tasks and not outside:
        raise RiskRefused("no carriers at all — there is no plan here to rank")
    carriers = [Carrier(task.id, INSIDE, task.effort) for task in tasks]
    carriers += list(outside)
    named = [carrier.id for carrier in carriers]
    repeated = sorted({name for name in named if named.count(name) > 1})
    if repeated:
        raise RiskRefused(
            f"{len(repeated)} carrier id(s) counted twice. ⛔ A carrier named inside "
            "and outside inflates the total and flatters every share in the table"
        )
    ordered = sorted(carriers, key=lambda carrier: (-carrier.effort, carrier.id))
    return Concentration(tuple(ordered))
