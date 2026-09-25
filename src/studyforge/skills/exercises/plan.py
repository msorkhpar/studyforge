r"""The page plan: which exercises a page gets, decided by its aspects before any is written.

**What it does.** Turns a page's **aspects** — the distinct checkable things it
teaches, read from its prose and its code, each ending in a named exercise or
a written reason (`aspects`) — and its difficulty tier into the exercises the
page is authored against: ⭐ **one planned exercise per distinct name the
aspects give, each carrying the aspects it checks.** ⛔ **The count is a
CEILING and never a quota** (R6, spec §7 §4): what ships is what clears the
gates, and `shortfall` is where each one that did not is named with the gate
that refused it.

**How you use it.**

    from studyforge.skills.exercises.plan import plan_for, plan_document, shortfall

    plan = plan_for(aspects, tier="core", where="the plan for page 3")
    plan.count                      # the ceiling this page is authored against
    plan.exercises[0].aspects       # the aspect ids the first planned exercise checks
    plan_document(plan)             # the decoded object the skill writes
    shortfall(plan, shipped=2, refusals=(Refusal("G3", "…"),), where="…")

**Depends on.** `aspects` for what an aspect is and the rules over it,
`studyforge.describe` for naming a value without reproducing it (R7) and
`studyforge.exercise.gates` for the one registry of gate ids. Standard library
only. ⛔ Not on any adapter and not on any source (R1).

## ⛔ THE COUNT IS SET BY COVERAGE, NOT BY LENGTH

A page may get no practice, two, or more: the target is covering every aspect
it teaches, not a minimum. ⚠️ **A length band would cap a code-dense page and
ship most of its examples as a reason nobody weighed**, so ⭐ **there is no
length ceiling**, and the tier does not move the count: it is recorded, and
handed to the author with the page, because it says how hard each exercise is
— never how many. ⚠️ **And not overdone** (see `aspects`): plan by the page's
IMPORTANT ideas, one exercise may check several, and a minor aspect is carried
by a short reason.

## ⚠️ WHY THE COUNT IS DERIVED FROM NAMES AND NOT FROM A FORMULA

⚠️ **A formula would make the count look derived when it is a judgement**, and
that stays true. Which aspects a page teaches, and whether one is worth an
exercise, is the author's call — so what this module guarantees is not that the
plan is *right*: it is that **every aspect is accounted for** (checked, or
excused in a sentence), that **no aspect is checked twice**, and that the same
aspects always produce the same plan (R10). ⭐ A reviewer disagreeing with a
plan has every aspect and every reason in front of them, including each aspect
that was NOT checked — which is what makes a thin plan visible.

## ⛔ A PLAN OF ZERO SAYS WHY, AND IT IS A LEGITIMATE ANSWER

⚠️ **A page that teaches nothing checkable plans none**, with the sentence
saying so written into its plan; and a page whose every aspect carries a reason
plans none with a reason per aspect. ⛔ **Zero is never reached silently.**

## ⛔ A SHORTFALL NAMES A REGISTERED GATE, AND THAT IS MECHANICAL

⭐ **`exercise.gates.family_of` is the one registry**, so a refusal citing
`G7` — or citing nothing — is refused here rather than read as an excuse.
⚠️ **This is the half of spec §7 §11 a module can hold.** Re-authoring within a
budget is the skill's; what this guarantees is that the arithmetic
adds up: everything the plan allowed for either shipped or was refused by a
gate that exists.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe
from studyforge.exercise.gates import family_of
from studyforge.skills.exercises.aspects import Aspect, aspect_document, require_aspects

#: The version of the document this module writes. ⛔ Bumped when a reader of
#: the old shape would be *wrong* rather than merely incomplete. ⚠️ **2**:
#: version 1 carried `words`, `skills`, `band` and movement `reasons`,
#: and a reader of it would take a length-capped count for a covered one.
PLAN_API = 2

#: The keys of the plan document itself, in write order (R10).
PLAN_KEYS = ("plan_api", "tier", "count", "aspects", "exercises", "nothing_checkable")

#: The keys of one planned exercise, in write order (R10).
PLANNED_KEYS = ("slot", "name", "aspects")

#: The keys of one named shortfall, in write order (R10).
SHORTFALL_KEYS = ("gate", "says")

#: A page that teaches its reader something for the first time.
INTRODUCTORY = "introductory"

#: The tier a page sits in when nothing about it is unusual.
CORE = "core"

#: A page whose material a reader meets after the ones it builds on.
ADVANCED = "advanced"

#: ⛔ Closed, and three rather than a scale. ⚠️ A tier says how
#: hard each exercise is and never how many: it is recorded and handed to the
#: author. A tier this build does not define is refused, never defaulted.
TIERS = (INTRODUCTORY, CORE, ADVANCED)

#: ⛔ Said in a refusal instead of the value (R7).
TIER_PERMITTED = "one of " + ", ".join(repr(tier) for tier in TIERS)


class PlanError(ValueError):
    """A page that cannot be planned for, and which reading is the reason.

    ⛔ Names the field and the permitted class, never the value (R7).
    """


@dataclass(frozen=True, slots=True)
class Planned:
    """One exercise the plan allows for: its slot, its name, and the aspects it checks."""

    slot: int
    name: str
    aspects: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Refusal:
    """One exercise the plan allowed for that did not ship, and the gate that refused it."""

    gate: str
    says: str


@dataclass(frozen=True, slots=True)
class Plan:
    """What one page is authored against: every aspect, and the exercises that check them."""

    tier: str
    aspects: tuple[Aspect, ...]
    exercises: tuple[Planned, ...]
    nothing_checkable: str | None

    @property
    def count(self) -> int:
        """How many exercises the page is authored against — ⛔ a ceiling, never a quota."""
        return len(self.exercises)

    @property
    def reasoned(self) -> tuple[Aspect, ...]:
        """⭐ Every aspect no exercise checks — the part of a thin plan a reviewer reads."""
        return tuple(aspect for aspect in self.aspects if aspect.exercise is None)

    def checked_by(self, planned: Planned) -> tuple[Aspect, ...]:
        """Return the aspects one planned exercise checks, in id order."""
        return tuple(aspect for aspect in self.aspects if aspect.id in planned.aspects)


def plan_for(
    aspects: object,
    tier: object,
    where: str,
    nothing_checkable: object = None,
    order: object = (),
) -> Plan:
    """Plan one page from its aspects: one planned exercise per distinct name they give.

    ⛔ **The exercises are read off the aspects, never counted separately**, so
    an exercise that checks no aspect cannot be planned and an aspect cannot
    be checked twice. ⭐ Aspects are held in id order, and the exercises in
    `order` — the author's teaching order, naming each planned exercise once —
    or, where the author gives none, in name order, so the listing order of the
    aspects cannot move the plan (R10).
    """
    named = _tier(tier, where)
    held, zero = require_aspects(aspects, nothing_checkable, where)
    names = _ordered(
        {aspect.exercise for aspect in held if aspect.exercise is not None}, order, where
    )
    exercises = tuple(
        Planned(
            slot=slot,
            name=name,
            aspects=tuple(aspect.id for aspect in held if aspect.exercise == name),
        )
        for slot, name in enumerate(names, start=1)
    )
    return Plan(named, held, exercises, zero)


def _ordered(names: set[str], order: object, where: str) -> list[str]:
    """Return the planned names in the author's order, or in name order when none is given.

    ⚠️ **Measured:** with name order only, a course's author prefixed every
    exercise `p01-`, `p02-` … to keep teaching order. ⛔ An order that does not
    name each planned exercise exactly once is refused, never completed: a
    name left out would be numbered by a rule the author did not choose.
    """
    if not isinstance(order, tuple) or not all(isinstance(one, str) for one in order):
        raise PlanError(f"{where}: a page's exercise order is a tuple of exercise names.")
    if not order:
        return sorted(names)
    if len(set(order)) != len(order) or set(order) != names:
        raise PlanError(
            f"{where}: the page's exercise order names {len(order)} exercise(s) and the "
            f"aspects plan {len(names)}; an order names each planned exercise exactly once."
        )
    return list(order)


def plan_document(plan: Plan) -> dict:
    """Return the decoded object the authoring skill writes, in `PLAN_KEYS` order (R10)."""
    return {
        "plan_api": PLAN_API,
        "tier": plan.tier,
        "count": plan.count,
        "aspects": [aspect_document(aspect) for aspect in plan.aspects],
        "exercises": [
            {"slot": planned.slot, "name": planned.name, "aspects": list(planned.aspects)}
            for planned in plan.exercises
        ],
        "nothing_checkable": plan.nothing_checkable,
    }


def shortfall(
    plan: Plan, shipped: object, refusals: tuple[Refusal, ...], where: str
) -> tuple[Refusal, ...]:
    """Check that the plan's ceiling was honoured and every gap is named by a gate.

    ⛔ **Three refusals, and each is one half of *a ceiling, never a quota*.**
    Shipping more than the plan allowed means the plan was not a ceiling.
    Shipping fewer with nothing said means a shortfall was engineered away
    rather than reported (spec §7 §11). Citing a gate no family declares means
    the report names something nobody can go and read.
    """
    count = _count(shipped, "shipped", where)
    if count > plan.count:
        raise PlanError(
            f"{where}: {count} exercises shipped against a plan of {plan.count}. The "
            f"plan is a ceiling, never a quota, so a page cannot ship past it — an "
            f"aspect the plan did not name is what would have to be added."
        )
    for refusal in refusals:
        _require_gate(refusal, where)
    if count + len(refusals) != plan.count:
        raise PlanError(
            f"{where}: the plan allowed {plan.count}, {count} shipped and "
            f"{len(refusals)} were named as refused, which leaves "
            f"{plan.count - count - len(refusals)} unaccounted for. Every shortfall is "
            f"named with the gate that refused it, or it is a shortfall nobody reported."
        )
    return refusals


def shortfall_document(refusals: tuple[Refusal, ...]) -> list[dict]:
    """Each named shortfall as a decoded object, in `SHORTFALL_KEYS` order (R10)."""
    return [{"gate": refusal.gate, "says": refusal.says} for refusal in refusals]


def _count(value: object, what: str, where: str) -> int:
    """Refuse a reading that is not a whole number of things, or is negative."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PlanError(
            f"{where}: {what!r} is a count of things and must be an int of zero or "
            f"more. The value is {describe(value)}."
        )
    return value


def _tier(value: object, where: str) -> str:
    """Refuse a difficulty tier this build does not define, rather than defaulting one."""
    if value not in TIERS:
        raise PlanError(
            f"{where}: 'tier' is {TIER_PERMITTED}. A tier this build does not define "
            f"is refused rather than read as the middle one, because defaulting it "
            f"would hide a typo as a judgement. The value is {describe(value)}."
        )
    return value  # type: ignore[return-value]


def _require_gate(refusal: Refusal, where: str) -> None:
    """⛔ Refuse a shortfall citing a gate no registered family declares."""
    if not isinstance(refusal.says, str) or not refusal.says.strip():
        raise PlanError(
            f"{where}: a shortfall's 'says' is what the gate reported, and it must be "
            f"text. The value is {describe(refusal.says)}."
        )
    if not isinstance(refusal.gate, str) or family_of(refusal.gate) is None:
        raise PlanError(
            f"{where}: a shortfall names the gate that refused the exercise, and no "
            f"registered gate family declares this one. The value is "
            f"{describe(refusal.gate)}."
        )
