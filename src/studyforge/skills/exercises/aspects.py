r"""A page's checkable aspects, and how each one ends: checked by an exercise, or a reason.

**What it does.** Holds the unit a page's plan is made of: an
**aspect** is one IMPORTANT idea the page teaches that a reader could be
checked on, read from its prose **and** its code. ⛔ **Every aspect ends one of
two ways** — the planned exercise (or quiz) that checks it, or a written reason
nothing does — and this module refuses an aspect with neither, one with both,
and two aspects that are one aspect named twice.

**How you use it.**

    from studyforge.skills.exercises.aspects import Aspect, require_aspects, require_read

    aspect = Aspect("totals", "a basket totals its prices", ("section:Totals",), exercise="total")
    aspects = require_aspects((aspect,), nothing_checkable=None, where="the plan for page 3")
    require_read(aspects, entry_keys, headings, where="the plan for page 3")

**Depends on.** `studyforge.exercise.gates` for the one token rule a name
written into a record obeys, and `studyforge.describe` for R7. Standard library
only. ⛔ Not on any adapter and not on any source (R1): an aspect arrives as
data the converting agent wrote, and nothing here can be told which corpus it
came from.

## ⛔ USER RULING, 2026-09-23 — COVERAGE, NOT LENGTH

> *"Depending on the context of the page there might be no practice, 2 or more,
> The target is covering all the aspects not just having something minimum we
> are looking for quality"*

⭐ **This module is that ruling's accounting**, and it mirrors the ledger's on
purpose (`accounting`): the ledger asks of every FILE entry *is it built on, or
excused?*; this asks the same of every ASPECT a page teaches. ⛔ **A thin plan
is therefore VISIBLE** — every aspect the author did not check is listed, with
the sentence that excuses it, in the page's committed plan.

## ⚠️ WHAT AN ASPECT IS, AND WHO JUDGES IT, IS AN AUTHORING JUDGEMENT

⛔ **Nothing here decides what a page teaches**, exactly as the band this
replaced never decided whether its numbers were right. A model or a person
reads the page and names the aspects; ⭐ what this module guarantees is that
the judgement is **written down where a reviewer can argue with it**: each
aspect says what it is, names what it was read from, and ends with an exercise
or a reason. ⚠️ **The mechanical halves are the ones below, and they are all
there is**: a basis that resolves, one ending per aspect, and no aspect
stated twice.

## ⛔ THE USER'S REFINEMENT, SAME DAY — IMPORTANT IDEAS, NOT EVERY FACT

> *"regarding the coverage don't over do it! at the same time we are not a
> university that wants to grade the knowdlge! Sometimes a single practice might
> cover better than 4 unrelated small practices. It's all about quality and the
> importants ofthe text. Like for the first quiz the dates do not matter. The
> version might matter. And for sure 4 questions were a lot"*

⭐ **So an aspect is an idea that matters to the page, never a fact it
mentions**: a date, a name or an incidental number is not an aspect, and the
concept it illustrates may be. ⭐ **One exercise may check many aspects**, and
one exercise that practises related aspects together is preferred over several
small unrelated ones. ⚠️ **A minor aspect may be carried by a short reason**
(*"incidental detail, not practised"*). ⛔ **No ceiling and no quota**: the
record is what was judged important and why, never a percentage to maximise.
⚠️ **So nothing here asks every fenced example to be an aspect** — the ledger
already accounts for every example, file by file (`accounting`), and a rule
here that did would turn every snippet into an aspect somebody must excuse.

## ⛔ A BASIS RESOLVES, OR IT IS NOT A BASIS

⭐ **"From its prose AND its code" is recorded, and each half resolves**: an
aspect read from code names the page's own ledger entry (`example:<path>:<n>`,
`tests:<path>`), and one read from prose names a heading the page carries once
(`section:<heading>`), because prose has no ledger entry.

## ⛔ A NEAR-DUPLICATE IS REFUSED, NEVER COUNTED

⭐ **An aspect names ONE exercise**, so two exercises checking one aspect
cannot be written. ⚠️ The remaining route is one aspect under two ids, and the
mechanical half of that is caught: two aspects whose sentences are the same
once case, spacing and punctuation are set aside are refused. ⛔ A restatement
in other words is the judgement's to catch, and this says so rather than
claiming more.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from studyforge.describe import describe
from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import require_role

#: A basis naming a heading the page carries: `section:<heading>`.
SECTION = "section:"

#: The keys of one aspect in the plan document, in write order (R10).
ASPECT_KEYS = ("id", "says", "basis", "exercise", "reason")

#: Said in a refusal instead of the value (R7).
BASIS_DESCRIBED = (
    "a ledger key of one of the page's own entries ('example:<path>:<n>' or "
    "'tests:<path>'), or 'section:<heading>' for a heading the page carries once"
)

#: What two sentences are compared on: letters and digits, case set aside.
_WORD = re.compile(r"[^\W_]+")


class AspectError(ValueError):
    """An aspect the plan cannot account for, and which rule is the reason.

    ⛔ Names the aspect's id and the rule — never a value read out of a corpus
    beyond a token the author wrote (R7).
    """


@dataclass(frozen=True, slots=True)
class Aspect:
    """One distinct checkable thing a page teaches, and how it ends.

    ⭐ `says` is one sentence a reader who has the aspect could be checked on;
    `basis` is what it was read from. ⛔ Exactly one of `exercise` (the name
    of the planned exercise that checks it) and `reason` (why nothing does).
    """

    id: str
    says: str
    basis: tuple[str, ...]
    exercise: str | None = None
    reason: str | None = None


def require_aspects(
    aspects: object, nothing_checkable: object, where: str
) -> tuple[tuple[Aspect, ...], str | None]:
    """Return the aspects in id order and the zero reason, refusing every rule this owns.

    ⛔ **Zero is legitimate and never silent**: a page naming no aspect must
    say why in `nothing_checkable`, and a page naming some must not, because
    that sentence would contradict the aspects beside it.
    """
    if not isinstance(aspects, tuple) or not all(isinstance(a, Aspect) for a in aspects):
        raise AspectError(f"{where}: a page's aspects are a tuple of Aspect.")
    for aspect in aspects:
        _require_aspect(aspect, where)
    _require_distinct(aspects, where)
    zero = _zero(aspects, nothing_checkable, where)
    return tuple(sorted(aspects, key=lambda aspect: aspect.id)), zero


def require_read(
    aspects: tuple[Aspect, ...], entries: Iterable[str], headings: Iterable[str], where: str
) -> None:
    """⛔ Refuse a basis that resolves to nothing the page carries.

    `entries` are the ledger keys of the page's own entries; `headings` every
    heading the page carries, with its repeats (`ledger.Source.sections`).
    """
    keys = tuple(entries)
    carried = tuple(headings)
    for aspect in aspects:
        for basis in aspect.basis:
            _require_basis(aspect, basis, keys, carried, where)


def aspect_document(aspect: Aspect) -> dict:
    """One aspect as the plan document writes it, in `ASPECT_KEYS` order (R10)."""
    return {
        "id": aspect.id,
        "says": aspect.says,
        "basis": list(aspect.basis),
        "exercise": aspect.exercise,
        "reason": aspect.reason,
    }


def _require_aspect(aspect: Aspect, where: str) -> None:
    """One aspect's own shape: a token id, a sentence, a basis, and exactly one ending."""
    ident = _token(aspect.id, "an aspect's id", where)
    if not isinstance(aspect.says, str) or not aspect.says.strip():
        raise AspectError(
            f"{where}: the aspect {ident!r} says nothing. An aspect is one sentence a "
            f"reader could be checked on. The value is {describe(aspect.says)}."
        )
    basis = aspect.basis
    if not isinstance(basis, tuple) or not basis or not all(_named(b) for b in basis):
        raise AspectError(
            f"{where}: the aspect {ident!r} names no basis. Every aspect is read from "
            f"something the page carries — {BASIS_DESCRIBED}."
        )
    if aspect.exercise is not None and aspect.reason is not None:
        raise AspectError(
            f"{where}: the aspect {ident!r} is checked by an exercise and also carries a "
            f"reason nothing checks it. The two cannot both be true."
        )
    if aspect.exercise is None and aspect.reason is None:
        raise AspectError(
            f"{where}: the aspect {ident!r} is checked by no exercise and carries no "
            f"written reason it is not. Every aspect a page teaches is one or the other "
            f"(spec §7 §4), because an aspect nobody accounted for is how a thin plan hides."
        )
    if aspect.exercise is not None:
        _token(aspect.exercise, f"the exercise that checks {ident!r}", where)
    elif not isinstance(aspect.reason, str) or not aspect.reason.strip():
        raise AspectError(
            f"{where}: the reason the aspect {ident!r} is not checked must be one "
            f"sentence. The value is {describe(aspect.reason)}."
        )


def _require_distinct(aspects: tuple[Aspect, ...], where: str) -> None:
    """⛔ Refuse one id twice, and one sentence under two ids — a near-duplicate."""
    seen: dict[str, str] = {}
    ids: set[str] = set()
    for aspect in aspects:
        if aspect.id in ids:
            raise AspectError(f"{where}: the aspect {aspect.id!r} is named twice.")
        ids.add(aspect.id)
        said = " ".join(_WORD.findall(aspect.says.casefold()))
        if said in seen:
            raise AspectError(
                f"{where}: the aspects {seen[said]!r} and {aspect.id!r} say the same "
                f"thing, so two exercises would check one aspect. Merge them into one "
                f"aspect: coverage is counted by aspects, never by exercises."
            )
        seen[said] = aspect.id


def _zero(aspects: tuple[Aspect, ...], nothing_checkable: object, where: str) -> str | None:
    """Return why a page names no aspect — ⛔ required for zero, refused beside any aspect."""
    if aspects:
        if nothing_checkable is not None:
            raise AspectError(
                f"{where}: the page names {len(aspects)} aspect(s) and also says it teaches "
                f"nothing checkable. The two cannot both be true."
            )
        return None
    if not isinstance(nothing_checkable, str) or not nothing_checkable.strip():
        raise AspectError(
            f"{where}: the page names no aspect and says nothing about why. A page that "
            f"teaches nothing checkable plans zero, and the sentence saying so is written "
            f"into its plan. The value is {describe(nothing_checkable)}."
        )
    return nothing_checkable


def _require_basis(
    aspect: Aspect, basis: str, keys: tuple[str, ...], headings: tuple[str, ...], where: str
) -> None:
    """One basis must resolve: to the page's own entry, or to a heading it carries once."""
    if basis.startswith(SECTION):
        occurrences = headings.count(basis[len(SECTION) :])
        if occurrences == 1:
            return
        raise AspectError(
            f"{where}: the aspect {aspect.id!r} is read from a section the page carries "
            f"{occurrences} times, and a region is bounded by one heading. "
            f"The section is not reproduced here (R7)."
        )
    if basis not in keys:
        raise AspectError(
            f"{where}: the aspect {aspect.id!r} names a basis that is not {BASIS_DESCRIBED}. "
            f"The value is not reproduced here (R7)."
        )


def _named(value: object) -> bool:
    """Answer whether a basis is one a reader could look up: text, and not blank."""
    return isinstance(value, str) and bool(value.strip())


def _token(value: object, what: str, where: str) -> str:
    """Return a token written into a plan, checked with the gate record's own role rule."""
    try:
        return require_role(value, f"{where}: {what}")
    except ExerciseError as error:
        raise AspectError(str(error)) from None
