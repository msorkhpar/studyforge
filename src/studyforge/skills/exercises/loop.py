r"""One page, authored: planned, drafted, gated, re-drafted inside the budget, reported.

**What it does.** Plans one page, then for each exercise the plan allows asks
the author for a draft, gates it, and on a refusal hands the author every gate
that refused and the last run's output — up to `ATTEMPTS` drafts. ⭐ What
clears ships; what exhausts the budget is a `Shortfall` naming the page, the
planned exercise, the gate, the gate's own sentence and the run's last output.

**How you use it.**

    carried = carried_practices(root, page, where)     # (1,) when the unit has one
    outcome = author_page(page, ledger, author, judge, runner, source="demo",
                          where=where, carried=carried)
    outcome.shipped                     # every Gated that cleared, numbered after `carried`
    outcome.shortfalls                  # every planned exercise that did not

**Depends on.** This package's `drafts`, `gating`, `ledger` and `plan`;
`exercise.bundle` for `Places` and `require_no_gap`; `skills.adapter` for
`Layout`, the one place a unit's archive directory is computed; `unit.builder`
for `read`, the one reader of a unit's archived documents. Standard library
only.

## ⛔ THE BUDGET IS FIXED AND THE BAR NEVER MOVES

⭐ **`ATTEMPTS` is a framework constant and nothing here takes a budget, a gate
list or an option**, so no caller can buy a green exercise with a longer loop
or a shorter gate suite. ⛔ A retry that drops a case id or a question id the
previous draft carried is refused (`drafts.require_no_retreat`) and the pass
stops: that exercise is neither shipped nor re-tried, because an exercise that
clears by asking less is the exact shortfall spec §7 §11 forbids hiding.

## ⛔ ORDINALS ARE HANDED OUT AS EXERCISES SHIP, SO A PAGE NEVER HAS A GAP

⭐ A planned exercise is drafted at the ordinal after the last one that
shipped, and a refused one leaves that ordinal for the next. ⚠️ Numbering by
plan position would leave `1` and `3` on a page whose second exercise was
refused — the gap `bundle.require_no_gap` and `validate`'s `practice-ordinals`
both refuse, because renumbering later would move every reader's progress.

## ⛔ A UNIT'S OWN PRACTICES COME FIRST, AND THEY ARE READ, NEVER DECLARED

⚠️ **A unit may already carry practices** — a bundled `practice-1`, say — so an
authored exercise numbered from 1 would take an ordinal a reader's progress is
already keyed to. ⛔ **Renumbering the source's practice is refused for the
reason above**, so authored exercises number AFTER it. ⭐ `carried_practices`
READS what the unit carries through `unit.builder.read`, the reader a build
uses, at the directory `Layout` computes — ⛔ never a declared offset, which
would be a second copy that goes stale. ⛔ And `require_after_carried` refuses
a page whose authored ordinals repeat or skip past what it carries, naming the
practice, before anything is committed.

## ⛔ ONE PLANNED EXERCISE PER NAME THE ASPECTS GIVE

⭐ Each planned exercise's brief carries the aspects the plan gave it to check,
so the author drafts against what the page teaches rather than against a
count. ⛔ `plan_page` refuses an aspect whose basis the page does not carry.

## ⛔ THE PLAN IS A CEILING, AND `shortfall` IS ASKED EVERY TIME

⭐ **Shipped plus refused must equal the plan**, and `plan.shortfall` — not a
second spelling of the arithmetic — is what checks it before a page's outcome
is returned.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from studyforge.exercise import CODE, ExerciseError
from studyforge.exercise.bundle import Places, require_no_gap
from studyforge.skills.adapter import Layout
from studyforge.skills.exercises.aspects import AspectError, require_read
from studyforge.skills.exercises.drafts import (
    ATTEMPTS,
    Author,
    AuthoringError,
    Brief,
    CodeDraft,
    Judge,
    Page,
    QuizDraft,
    page_entries,
    require_draft,
    require_no_retreat,
    source_case,
)
from studyforge.skills.exercises.gating import Gated, Runner, gate_code, gate_quiz
from studyforge.skills.exercises.ledger import Ledger, key_of
from studyforge.skills.exercises.plan import Plan, Refusal, plan_for, shortfall
from studyforge.unit.builder import NoMaterial, read
from studyforge.unit.errors import ContentError

#: The kind an archive document records for a practice. ⚠️ `archive`'s own
#: vocabulary, the value `unit.builder.KIND_ORDER` orders last.
PRACTICE = "practice"


@dataclass(frozen=True, slots=True)
class Shortfall:
    """One planned exercise that exhausted the budget, and everything the report names."""

    slot: int
    gate: str
    says: str
    output: str


@dataclass(frozen=True, slots=True)
class PageOutcome:
    """What one page's pass produced: its plan, what shipped, and what did not."""

    page: Page
    case: str
    plan: Plan
    shipped: tuple[Gated, ...]
    shortfalls: tuple[Shortfall, ...]


def author_page(
    page: Page,
    ledger: Ledger,
    author: Author,
    judge: Judge | None,
    runner: Runner | None,
    *,
    source: str,
    where: str,
    carried: tuple[int, ...],
) -> PageOutcome:
    """Plan, draft, gate and re-draft one page's exercises — ⛔ the plan is a ceiling.

    ⛔ `carried` is what `carried_practices` read off the unit's archive, and
    the first authored exercise takes the ordinal after the last of them.
    """
    plan = plan_page(page, ledger, where)
    case = source_case(page, ledger)
    entries = page_entries(page, ledger)
    shipped: list[Gated] = []
    missed: list[Shortfall] = []
    for planned in plan.exercises:
        slot = planned.slot
        places = Places(page.address, page.variant, page.unit, len(carried) + len(shipped) + 1)
        first = Brief(page, case, slot, places, 1, entries, plan.checked_by(planned))
        gated, refused = _one(first, ledger, author, judge, runner, source, f"{where}, {slot}")
        if gated is not None:
            shipped.append(gated)
        else:
            missed.append(refused)
    shortfall(plan, len(shipped), tuple(Refusal(m.gate, m.says) for m in missed), where)
    require_after_carried(carried, tuple(gated.places.ordinal for gated in shipped), where)
    return PageOutcome(page, case, plan, tuple(shipped), tuple(missed))


def plan_page(page: Page, ledger: Ledger, where: str) -> Plan:
    """Plan one page from its aspects, and refuse a plan that did not read the page's code.

    ⭐ **The one place a page is planned**, so the pass and a single page's
    loop cannot plan the same page two ways. ⛔ Every aspect's basis must
    resolve to the page's own ledger entries or to a heading it carries once.
    """
    headings = next((s.sections for s in ledger.sources if s.path == page.path), ())
    try:
        plan = plan_for(page.aspects, page.tier, where, page.nothing_checkable)
        require_read(plan.aspects, map(key_of, page_entries(page, ledger)), headings, where)
    except AspectError as error:
        raise AuthoringError(str(error)) from None
    return plan


def carried_practices(root: Path | str, page: Page, where: str) -> tuple[int, ...]:
    """Return the ordinals of the practices the page's unit already carries, `1..n`.

    ⭐ **Read, never declared**: the unit's archive directory is
    `Layout`'s, and its documents are read by `unit.builder.read` — the one
    reader a build uses, gates and all. A unit nothing has been ingested for
    carries nothing. ⛔ Ordinals that are not `1..n` are refused: an authored
    exercise cannot be numbered after a hole.
    """
    directory = Layout(Path(root)).unit_dir(page.address, page.variant, page.unit)
    try:
        material = read(directory)
    except NoMaterial:
        return ()
    except ContentError as error:
        raise AuthoringError(
            f"{where}: the unit's archived documents will not read, so what it already "
            f"carries cannot be counted. {error}"
        ) from None
    found = tuple(document["ordinal"] for document in material.of_kind(PRACTICE))
    try:
        return require_no_gap(found, f"{where}: the practices the unit's archive carries")
    except ExerciseError as error:
        raise AuthoringError(str(error)) from None


def require_after_carried(carried: tuple[int, ...], shipped: tuple[int, ...], where: str) -> None:
    """Refuse authored ordinals that repeat or skip past what the unit carries, naming one.

    ⛔ **An authored exercise at an ordinal the unit already carries would
    overwrite the source's practice, and every reader's progress keyed to it**
    — so it is refused by the practice's name, never renumbered and never
    silently written over.
    """
    repeated = sorted(set(carried) & set(shipped))
    if repeated:
        raise AuthoringError(
            f"{where}: an authored exercise takes 'practice-{repeated[0]}', which the "
            f"unit already carries. Authored exercises number after the unit's own "
            f"practices, and the source's practice is never overwritten or renumbered."
        )
    try:
        require_no_gap(tuple(carried) + tuple(shipped), where)
    except ExerciseError as error:
        raise AuthoringError(str(error)) from None


def _one(
    brief: Brief,
    ledger: Ledger,
    author: Author,
    judge: Judge | None,
    runner: Runner | None,
    source: str,
    where: str,
) -> tuple[Gated | None, Shortfall | None]:
    """Draft and gate one planned exercise, up to `ATTEMPTS` times.

    ⭐ Every retry's brief carries the draft it replaces, every gate that
    refused it and the last run's output — the author re-authors against the
    finding, never against a blank page.
    """
    previous: CodeDraft | QuizDraft | None = None
    gated: Gated | None = None
    for attempt in range(1, ATTEMPTS + 1):
        current = replace(
            brief,
            attempt=attempt,
            previous=previous,
            refused=gated.refused if gated is not None else (),
            output=gated.output if gated is not None else "",
        )
        draft = require_draft(brief.page, author.draft(current), where)
        if previous is not None:
            require_no_retreat(previous, draft, where)
        gated = _gate(draft, current, ledger, judge, runner, source, where)
        if gated.clears:
            return gated, None
        previous = draft
    refused = gated.refused[0]
    return None, Shortfall(brief.slot, refused.id, refused.says, gated.output)


def _gate(
    draft: CodeDraft | QuizDraft,
    brief: Brief,
    ledger: Ledger,
    judge: Judge | None,
    runner: Runner | None,
    source: str,
    where: str,
) -> Gated:
    """Send a draft to its kind's gates, refusing a pass that brought nothing to run them with."""
    if brief.page.kind == CODE:
        if runner is None:
            raise _missing("runner", brief, where)
        return gate_code(draft, brief, ledger, runner, source=source, where=where)
    if judge is None:
        raise _missing("judge", brief, where)
    return gate_quiz(draft, brief, ledger, judge, where=where)


def _missing(what: str, brief: Brief, where: str) -> AuthoringError:
    """Return the refusal for a page whose gates cannot be read with what the pass has."""
    return AuthoringError(
        f"{where}: the page '{brief.page.path}' is a {brief.page.kind!r} page and the "
        f"pass was handed no {what}. Its gates cannot be read without one, and a gate "
        f"that is not read is not a gate that held."
    )
