r"""One page, authored: planned, drafted, gated, re-drafted inside the budget, reported.

**What it does.** Plans one page, then for each exercise the plan allows asks
the author for a draft, gates it, and on a refusal hands the author every gate
that refused and the last run's output — up to `ATTEMPTS` drafts. ⭐ What
clears ships; what exhausts the budget is a `Shortfall` naming the page, the
planned exercise, the gate, the gate's own sentence and the run's last output.

**How you use it.**

    outcome = author_page(page, ledger, author, judge, runner, source="demo", where=where)
    outcome.shipped                     # every Gated that cleared, ordinals 1..n
    outcome.shortfalls                  # every planned exercise that did not

**Depends on.** This package's `drafts`, `gating`, `ledger` and `plan`, and
`exercise.bundle` for `Places`. Standard library only.

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

## ⛔ THE PLAN IS A CEILING, AND `shortfall` IS ASKED EVERY TIME

⭐ **Shipped plus refused must equal the plan**, and `plan.shortfall` — not a
second spelling of the arithmetic — is what checks it before a page's outcome
is returned.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from studyforge.exercise import CODE
from studyforge.exercise.bundle import Places
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
from studyforge.skills.exercises.ledger import Ledger
from studyforge.skills.exercises.plan import Plan, Refusal, plan_for, shortfall


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
) -> PageOutcome:
    """Plan, draft, gate and re-draft one page's exercises — ⛔ the plan is a ceiling."""
    plan = plan_for(page.words, page.skills, page.tier, where)
    case = source_case(page, ledger)
    entries = page_entries(page, ledger)
    shipped: list[Gated] = []
    missed: list[Shortfall] = []
    for slot in range(1, plan.count + 1):
        places = Places(page.address, page.variant, page.unit, len(shipped) + 1)
        first = Brief(page, case, slot, places, 1, entries)
        gated, refused = _one(first, ledger, author, judge, runner, source, f"{where}, {slot}")
        if gated is not None:
            shipped.append(gated)
        else:
            missed.append(refused)
    shortfall(plan, len(shipped), tuple(Refusal(m.gate, m.says) for m in missed), where)
    return PageOutcome(page, case, plan, tuple(shipped), tuple(missed))


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
