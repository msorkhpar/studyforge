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
would be a second copy that goes stale. ⛔ **Only the source's own practices
count**: one an earlier authoring pass generated is not carried, so a unit
authored again after its bundles are removed numbers from where the source's
own practices end. ⛔ And `require_after_carried` refuses
a page whose authored ordinals repeat or skip past what it carries, naming the
practice, before anything is committed.

## ⛔ ONE PLANNED EXERCISE PER NAME THE ASPECTS GIVE

⭐ Each planned exercise's brief carries the aspects the plan gave it to check,
so the author drafts against what the page teaches rather than against a
count. ⛔ `plan_page` refuses an aspect whose basis the page does not carry.

## ⭐ A CODE PAGE'S QUIZ IS DRAFTED LAST, SO IT TAKES THE UNIT'S LAST ORDINAL

⭐ **A page that names a `quiz` gets its code exercises first and its quiz
after them**, so the questions sit at the end of the page, after the work,
where a reader checks what they have read. ⛔ Only the ORDER of drafting moves:
each planned exercise keeps its slot, the plan is the one `plan_for` wrote, and
the brief's `name` says which kind of draft is asked for (`Brief.kind`).
⛔ `plan_page` refuses a `quiz` no aspect names, so a page cannot declare a
quiz it never plans.

## ⛔ THE PLAN IS A CEILING, AND `shortfall` IS ASKED EVERY TIME

⭐ **Shipped plus refused must equal the plan**, and `plan.shortfall` — not a
second spelling of the arithmetic — is what checks it before a page's outcome
is returned.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from pathlib import Path

from studyforge.exercise import CODE, ExerciseError, from_document
from studyforge.exercise.bundle import Places, require_no_gap
from studyforge.skills.adapter import Layout
from studyforge.skills.exercises.aspects import AspectError, require_read
from studyforge.skills.exercises.drafts import (
    ATTEMPTS,
    AUTHORED_PROVENANCE,
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
from studyforge.skills.exercises.plan import Plan, Planned, Refusal, plan_for, shortfall
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
    for planned in drafting_order(page, plan):
        slot = planned.slot
        places = Places(page.address, page.variant, page.unit, len(carried) + len(shipped) + 1)
        first = Brief(
            page, case, slot, places, 1, entries, plan.checked_by(planned), name=planned.name
        )
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
        plan = plan_for(page.aspects, page.tier, where, page.nothing_checkable, page.order)
        require_read(plan.aspects, map(key_of, page_entries(page, ledger)), headings, where)
    except AspectError as error:
        raise AuthoringError(str(error)) from None
    if page.quiz is not None and page.quiz not in {planned.name for planned in plan.exercises}:
        raise AuthoringError(
            f"{where}: the page '{page.path}' names a quiz that no aspect is checked by. "
            f"A quiz is planned like every exercise, by the aspects that name it, so "
            f"one no aspect names would ship questions about nothing the page planned."
        )
    return plan


def drafting_order(page: Page, plan: Plan) -> tuple[Planned, ...]:
    """Return the plan's exercises in the order they are drafted: code first, the quiz last.

    ⭐ Ordinals are handed out as exercises ship, so this order is the order a
    reader meets them on the page. ⛔ Slots are not renumbered.
    """
    return quiz_last(plan.exercises, page.quiz, lambda planned: planned.name)


def quiz_last[T](items: Iterable[T], quiz: str | None, name: Callable[[T], str]) -> tuple[T, ...]:
    """Return `items` in drafting order: every one not named `quiz`, then the one that is.

    ⭐ **The one spelling of the order**, so what a coverage report shipped can
    be read back against its plan (`practised`) by the rule that shipped it.
    """
    held = tuple(items)
    return tuple(one for one in held if name(one) != quiz) + tuple(
        one for one in held if name(one) == quiz
    )


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
    found = tuple(
        document["ordinal"]
        for document in material.of_kind(PRACTICE)
        if not _authored_earlier(document, where)
    )
    try:
        return require_no_gap(found, f"{where}: the practices the unit's archive carries")
    except ExerciseError as error:
        raise AuthoringError(str(error)) from None


def _authored_earlier(document: dict, where: str) -> bool:
    """Whether an archived practice is one an earlier authoring pass generated.

    ⛔ **Only the source's own practices are carried.** An authored practice
    reaches the archive when an adapter emits its bundle, and it stays there
    after its bundle is removed to be authored again — counted, it would number
    the new exercises after a practice that no longer exists. ⭐ Read off the
    record's own provenance through `exercise.from_document`, the one reader,
    so a quiz whose record leaves provenance out reads as the `generated` it is.
    """
    record = document.get("exercise")
    if record is None:
        return False
    try:
        return from_document(record, where).provenance == AUTHORED_PROVENANCE
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
        draft = require_draft(brief.page, author.draft(current), where, brief.kind)
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
    if brief.kind == CODE:
        if runner is None:
            raise _missing("runner", brief, where)
        return gate_code(draft, brief, ledger, runner, source=source, where=where)
    if judge is None:
        raise _missing("judge", brief, where)
    return gate_quiz(draft, brief, ledger, judge, where=where)


def _missing(what: str, brief: Brief, where: str) -> AuthoringError:
    """Return the refusal for a page whose gates cannot be read with what the pass has."""
    return AuthoringError(
        f"{where}: the page '{brief.page.path}' plans a {brief.kind!r} exercise and the "
        f"pass was handed no {what}. Its gates cannot be read without one, and a gate "
        f"that is not read is not a gate that held."
    )
