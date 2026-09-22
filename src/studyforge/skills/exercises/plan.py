r"""The page plan: how many exercises a page gets, decided before any is written.

**What it does.** Turns three readings of a page — its length, how many
distinct checkable skills it teaches, and its difficulty tier — into a count,
inside a band its length sets, with **every movement recorded as a reason**.
⛔ **The count is a CEILING and never a quota** (R6, spec §7 §4): what ships is
what clears the gates, and `shortfall` is where each one that did not is named
with the gate that refused it.

**How you use it.**

    from studyforge.skills.exercises.plan import plan_for, plan_document, shortfall

    plan = plan_for(words=900, skills=3, tier="core", where="the plan for page 3")
    plan.count                      # the ceiling this page is authored against
    plan_document(plan)             # the decoded object the skill writes
    shortfall(plan, shipped=2, refusals=(Refusal("G3", "…"),), where="…")

**Depends on.** `studyforge.describe` for naming a value without reproducing it
(R7) and `studyforge.exercise.gates` for the one registry of gate ids. Standard
library only. ⛔ Not on any adapter and not on any source (R1): a page arrives
as three numbers and a token, and nothing here can be told which corpus it is.

## ⛔ WHY A BAND AND NOT A FORMULA

⚠️ **A formula would make the count look derived when it is a judgement.** The
three readings are honest inputs and the arithmetic over them is a convention,
so what this module guarantees is not that the number is *right* — it is that
the number is **bounded by the page's length**, that **every movement is
written down**, and that the same three readings always produce the same count
(R10). ⭐ A reviewer disagreeing with a plan has the reasons in front of them
and can argue with one of them, which is the whole point of recording them.

## ⛔ THE BANDS ARE A FRAMEWORK CONSTANT, NEVER A CORPUS'S STRING (R1)

⭐ **A corpus cannot widen its own band.** Letting one supply the table would
make the ceiling a thing an author sets, and a ceiling an author sets is not a
ceiling. ⚠️ Moving the table is a decision taken here, in one place, for every
source at once — which is also what keeps two corpora comparable.

## ⛔ A PLAN OF ZERO SAYS WHY, AND IT IS A LEGITIMATE ANSWER

⚠️ **A page too short to carry an exercise, or one that teaches nothing
checkable, plans none** — and `E14`'s first property still holds over it,
because the ledger accounts for whatever it carries with a written reason.
⛔ **Zero is never reached silently**: the band that produced it is recorded,
so a page with no practices is a page somebody can see the reason for.

## ⛔ A SHORTFALL NAMES A REGISTERED GATE, AND THAT IS MECHANICAL

⭐ **`exercise.gates.family_of` is the one registry**, so a refusal citing
`G7` — or citing nothing — is refused here rather than read as an excuse.
⚠️ **This is the half of spec §7 §11 a module can hold.** Re-authoring within a
budget is the skill's (`AX-08`); what this guarantees is that the arithmetic
adds up: everything the plan allowed for either shipped or was refused by a
gate that exists.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe
from studyforge.exercise.gates import family_of

#: The version of the document this module writes. ⛔ Bumped when a reader of
#: the old shape would be *wrong* rather than merely incomplete.
PLAN_API = 1

#: The keys of one recorded reason, in write order (R10).
REASON_KEYS = ("moves", "says")

#: The keys of the plan document itself, in write order (R10).
PLAN_KEYS = ("plan_api", "words", "skills", "tier", "band", "count", "reasons")

#: The keys of one named shortfall, in write order (R10).
SHORTFALL_KEYS = ("gate", "says")

#: A page that teaches its reader something for the first time.
INTRODUCTORY = "introductory"

#: The tier a page sits in when nothing about it is unusual.
CORE = "core"

#: A page whose material a reader meets after the ones it builds on.
ADVANCED = "advanced"

#: ⛔ Closed, and three rather than a scale: a tier moves the count by one step
#: in one direction, and a fourth token would be a second way of saying one of
#: these. A tier this build does not define is refused, never defaulted.
TIERS = (INTRODUCTORY, CORE, ADVANCED)

#: How far each tier moves the count off its band's floor.
TIER_MOVES = {INTRODUCTORY: -1, CORE: 0, ADVANCED: 1}

#: ⛔ Said in a refusal instead of the value (R7).
TIER_PERMITTED = "one of " + ", ".join(repr(tier) for tier in TIERS)


@dataclass(frozen=True, slots=True)
class Band:
    """One length band: the words that open it, and the counts it permits.

    ⛔ **`ceiling` is the hard bound and no page may plan past it.** `floor` is
    where a page that teaches at least one checkable skill starts, before the
    movements; ⚠️ **zero is permitted in every band** and is the one value below
    the floor, because a page that teaches nothing checkable plans nothing —
    and that is recorded as a reason rather than reached quietly.
    """

    name: str
    words: int
    floor: int
    ceiling: int


#: ⛔ **Closed, ordered by the words that open each band, widest last.** The
#: numbers are a convention and are stated here so a reviewer can argue with
#: them in one place; ⚠️ what is NOT a convention is that the count cannot leave
#: the band, which is the property `AX-11` reads on a real corpus.
BANDS = (
    Band("stub", 0, 0, 0),
    Band("short", 250, 1, 2),
    Band("standard", 700, 1, 4),
    Band("long", 1800, 2, 6),
)


class PlanError(ValueError):
    """A page that cannot be planned for, and which reading is the reason.

    ⛔ Names the field and the permitted class, never the value (R7).
    """


@dataclass(frozen=True, slots=True)
class Reason:
    """One thing that moved the count, and how far it moved it."""

    moves: int
    says: str


@dataclass(frozen=True, slots=True)
class Refusal:
    """One exercise the plan allowed for that did not ship, and the gate that refused it."""

    gate: str
    says: str


@dataclass(frozen=True, slots=True)
class Plan:
    """What one page is authored against: a ceiling, its band, and every reason."""

    words: int
    skills: int
    tier: str
    band: Band
    count: int
    reasons: tuple[Reason, ...]


def band_for(words: int) -> Band:
    """Return the band a page of this length sits in — ⭐ the widest its words open."""
    found = BANDS[0]
    for band in BANDS:
        if words >= band.words:
            found = band
    return found


def plan_for(words: object, skills: object, tier: object, where: str) -> Plan:
    """Plan one page: a count inside its band, with every movement recorded.

    ⛔ **The count starts at the band's floor and is moved, never invented.**
    One step per distinct checkable skill beyond the first, one step for the
    tier, and then the band clamps — and the clamp is itself a recorded reason,
    because a ceiling that silently ate a movement is a ceiling nobody can see
    working.
    """
    length = _count(words, "words", where)
    distinct = _count(skills, "skills", where)
    named = _tier(tier, where)
    band = band_for(length)
    reasons = [
        Reason(
            0,
            f"the page is {length} words, which puts it in the {band.name!r} band, "
            f"whose ceiling is {band.ceiling} and whose floor for a page with work "
            f"is {band.floor}",
        )
    ]
    count = band.floor
    if band.ceiling == 0:
        reasons.append(Reason(0, "a page in this band is too short to carry an exercise"))
        return Plan(length, distinct, named, band, 0, tuple(reasons))
    if distinct == 0:
        reasons.append(Reason(-count, "the page names no distinct checkable skill"))
        return Plan(length, distinct, named, band, 0, tuple(reasons))
    plural = "" if distinct == 1 else "s"
    count, reasons = _moved(
        count, reasons, distinct - 1, f"{distinct} distinct checkable skill{plural}"
    )
    count, reasons = _moved(count, reasons, TIER_MOVES[named], f"the {named!r} tier")
    return Plan(length, distinct, named, band, *_clamped(count, band, reasons))


def plan_document(plan: Plan) -> dict:
    """Return the decoded object the authoring skill writes, in one fixed order (R10)."""
    return {
        "plan_api": PLAN_API,
        "words": plan.words,
        "skills": plan.skills,
        "tier": plan.tier,
        "band": plan.band.name,
        "count": plan.count,
        "reasons": [{"moves": reason.moves, "says": reason.says} for reason in plan.reasons],
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
            f"plan is a ceiling, never a quota, so a page cannot ship past it — the "
            f"reading that produced the ceiling is what would have to move."
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


def _moved(count: int, reasons: list[Reason], moves: int, says: str) -> tuple[int, list[Reason]]:
    """Apply one movement and record it — ⭐ a movement of zero is recorded too."""
    reasons.append(Reason(moves, says))
    return count + moves, reasons


def _clamped(count: int, band: Band, reasons: list[Reason]) -> tuple[int, tuple[Reason, ...]]:
    """Hold the count inside its band, recording the clamp when there was one."""
    held = max(band.floor, min(band.ceiling, count))
    if held != count:
        reasons.append(
            Reason(
                held - count,
                f"the {band.name!r} band permits {band.floor} to {band.ceiling}, and "
                f"the movements above reached {count}",
            )
        )
    return held, tuple(reasons)


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
