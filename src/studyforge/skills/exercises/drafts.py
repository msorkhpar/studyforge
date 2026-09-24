r"""What an author is asked, what it answers with, and the one rule a retry obeys.

**What it does.** Defines the page the converting agent describes, the three
source cases read off the ledger for it, the brief an author is handed for one
planned exercise, and the two draft shapes an author answers with — a code
exercise or a quiz. ⛔ It also holds the rule that makes *never by dropping a
case or deleting a question* structural: a retry may not carry fewer.

**How you use it.**

    page = Page(path, address, "python", unit=1, kind=CODE, aspects=(greets,),
                tier=CORE, graders=("checks/test_it.py",))
    source_case(page, ledger)             # 'code-and-tests'
    require_no_retreat(previous, draft, where)

**Depends on.** `studyforge.address`, `studyforge.exercise` for the case and
origin vocabulary, `studyforge.exercise.quiz` for a question,
`studyforge.exercise.gates` for a verdict, `studyforge.exercise.bundle` for
`Places`, and this package's `ledger` and `scan`. Standard library only.

## ⛔ THE CASE IS READ, NEVER CHOSEN

⭐ **Spec §7 §1's three rows are a fact about the page**, so they are derived
from the ledger rather than declared: a page with a test file the corpus
declares for it is `code-and-tests`, one with a fenced example and no test file
is `code-no-tests`, and one with neither is `neither`. ⚠️ An author that could
declare its own case could file a page with tests under `neither` and never
look at them.

## ⛔ A DRAFT NAMES NO PROVENANCE

⭐ **Every exercise this skill writes is `generated`/`advisory`**, and the two
words are this module's constants rather than draft fields — so no author, and
no retry, can write `authoritative` onto authored work (R5). ⚠️ A
`bundled`/`authoritative` exercise is the blanking derivation over the source's
own exercise and is not produced here.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

from studyforge.address import Address
from studyforge.exercise import CODE, EXERCISE_KINDS, Case, Origin
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import Verdict
from studyforge.exercise.gates.quiz import Judgement
from studyforge.exercise.quiz import Question
from studyforge.skills.exercises.aspects import Aspect
from studyforge.skills.exercises.ledger import EXAMPLE, TESTS, Entry, Ledger
from studyforge.skills.exercises.scan import scan

#: The page ships a test file of its own: author on top of the source's tests.
CODE_AND_TESTS = "code-and-tests"

#: The page carries a fenced example and no test file: the example is the reference.
CODE_NO_TESTS = "code-no-tests"

#: The page carries neither: the ask, the reference, the starter and the tests
#: are all authored from its prose.
NEITHER = "neither"

#: ⛔ Spec §7 §1's three rows, closed, in the order the table states them.
SOURCE_CASES = (CODE_AND_TESTS, CODE_NO_TESTS, NEITHER)

#: ⛔ **The fixed attempt budget** (spec §7 §11): how many drafts one planned
#: exercise gets before it is reported rather than shipped. A framework
#: constant, so no corpus and no caller can widen it into a quota.
ATTEMPTS = 3

#: ⛔ What every exercise this skill writes is. Never a draft's field (R5).
AUTHORED_PROVENANCE = "generated"
AUTHORED_TRUST = "advisory"

#: A word, as `words_of` counts one: letters and digits, with an apostrophe inside.
_WORD = re.compile(r"[^\W_]+(?:['’][^\W_]+)*")


class AuthoringError(ValueError):
    """A pass that cannot go on, and which of its inputs is the reason.

    ⛔ Names the page, the path or the rule — never a value read out of a
    corpus beyond a path the corpus declared (R7).
    """


@dataclass(frozen=True, slots=True)
class Page:
    """One page to author exercises for, as the converting agent read it.

    ⭐ `aspects` and `tier` are the agent's readings: the plan is read off the aspects, each
    checked by a named exercise or carried by a reason, and nothing here
    guesses one. ⛔ `nothing_checkable` is the sentence a page naming no aspect
    owes, and only such a page may carry it.
    """

    path: str
    address: Address
    variant: str
    unit: int
    kind: str
    aspects: tuple[Aspect, ...]
    tier: str
    graders: tuple[str, ...] = ()
    nothing_checkable: str | None = None


@dataclass(frozen=True, slots=True)
class CodeDraft:
    """One code exercise as an author wrote it, before any gate has read it.

    ⭐ Every path but a command's arguments is **workspace-relative**;
    `plants` maps each edge case's id to the solution that solves
    the ask and ignores exactly that edge (`G3`). ⭐ `build` maps each build
    file's workspace-relative path to its text: empty for an exercise
    whose tests need nothing but the language. ⛔ `report` is inside
    `exercise.bundle.RUN_OUTPUT_DIRNAME`, or the bundle is refused.
    """

    title: str
    lang: str
    main_file: str
    test_file: str
    run_command: tuple[str, ...]
    test_command: tuple[str, ...]
    cases: tuple[Case, ...]
    report: str
    origin: Origin
    statement: str
    starter: str
    reference: str
    tests: str
    plants: Mapping[str, str]
    build: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class QuizDraft:
    """One quiz as an author wrote it: a title and its questions, each with its passage."""

    title: str
    questions: tuple[Question, ...]


@dataclass(frozen=True, slots=True)
class Brief:
    """Everything an author is handed for one attempt at one planned exercise.

    ⭐ `slot` is which of the plan's exercises this is; `places` is where it
    will sit if it ships, numbered after the ones that already have.
    ⭐ `aspects` are the ones the plan gave this exercise to check.
    ⛔ On a retry, `refused` carries every gate that did not hold and `output`
    the last run's output, so the author re-authors against the finding.
    """

    page: Page
    case: str
    slot: int
    places: Places
    attempt: int
    entries: tuple[Entry, ...]
    aspects: tuple[Aspect, ...] = ()
    previous: CodeDraft | QuizDraft | None = None
    refused: tuple[Verdict, ...] = ()
    output: str = ""


class Author(Protocol):
    """The converting agent's half: drafting an exercise, and excusing an entry."""

    def draft(self, brief: Brief) -> CodeDraft | QuizDraft:
        """Answer one brief with a draft of the kind the page declares."""

    def excuse(self, entry: Entry) -> str:
        """Say, in one sentence, why no exercise was built from this ledger entry."""


class Judge(Protocol):
    """The independent pass a quiz's `Q1`–`Q3` are taken by — ⛔ never the author."""

    def __call__(self, brief: Brief, questions: tuple[Question, ...]) -> tuple[Judgement, ...]:
        """Return one judgement per question for `Q1` and `Q2`, one per wrong option for `Q3`."""


def words_of(text: str) -> int:
    """Count the words a page teaches with: its prose, with every fenced block left out.

    ⚠️ **A decision, and this is its one spelling** (the ledger's contract
    leaves it to the skill): a fence is an example, not reading, so its body and its language
    tag are not counted. The fence grammar is `scan`'s, never a second one.
    ⛔ **It sets no count**: the plan is read off a page's aspects. It is the
    reading that shows how little prose a code-dense page has.
    """
    read = scan(text)
    fenced = sum(len(_WORD.findall(fence.body)) for fence in read.fences)
    tags = sum(len(_WORD.findall(fence.language or "")) for fence in read.fences)
    return max(0, len(_WORD.findall(text)) - fenced - tags)


def page_entries(page: Page, ledger: Ledger) -> tuple[Entry, ...]:
    """Return the ledger's entries for this page: its fences, then its declared test files."""
    graders = set(page.graders)
    return tuple(
        entry
        for entry in ledger.entries
        if (entry.kind == EXAMPLE and entry.path == page.path)
        or (entry.kind == TESTS and entry.path in graders)
    )


def source_case(page: Page, ledger: Ledger) -> str:
    """Read spec §7 §1's case off the ledger — ⛔ never off anything the author says."""
    entries = page_entries(page, ledger)
    if any(entry.kind == TESTS for entry in entries):
        return CODE_AND_TESTS
    if any(entry.kind == EXAMPLE for entry in entries):
        return CODE_NO_TESTS
    return NEITHER


def require_page(page: Page, ledger: Ledger, where: str) -> Page:
    """Refuse a page the ledger did not read, a grader it does not carry, or an unknown kind."""
    read = {source.path for source in ledger.sources}
    graders = {entry.path for entry in ledger.entries if entry.kind == TESTS}
    if page.path not in read or page.path in graders:
        raise AuthoringError(
            f"{where}: the page '{page.path}' is not material the ledger read, so "
            f"nothing an exercise cites from it could be accounted for."
        )
    unknown = [path for path in page.graders if path not in graders]
    if unknown:
        raise AuthoringError(
            f"{where}: the page '{page.path}' names {len(unknown)} test file(s) the "
            f"ledger does not carry as a grader, starting at '{unknown[0]}'. Declare "
            f"every grader to the ledger, or the page's case is read wrongly."
        )
    if page.kind not in EXERCISE_KINDS:
        raise AuthoringError(
            f"{where}: the page '{page.path}' declares a kind that is not one of "
            f"{list(EXERCISE_KINDS)}."
        )
    return page


def require_draft(page: Page, draft: object, where: str) -> CodeDraft | QuizDraft:
    """Refuse a draft of the wrong kind for its page — a quiz on a code page, or neither."""
    wanted = CodeDraft if page.kind == CODE else QuizDraft
    if not isinstance(draft, wanted):
        raise AuthoringError(
            f"{where}: the page '{page.path}' is a {page.kind!r} page and the author "
            f"answered with something that is not a {wanted.__name__}."
        )
    return draft


def require_no_retreat(
    previous: CodeDraft | QuizDraft, draft: CodeDraft | QuizDraft, where: str
) -> CodeDraft | QuizDraft:
    """⛔ Refuse a retry that carries fewer cases or questions than the draft it replaces.

    ⭐ **This is spec §7 §11's *never by dropping a case or deleting a
    question*, made a refusal rather than a sentence.** A gate that refused an
    edge case is answered by a better test or a better plant — never by the
    edge case disappearing, which would ship an exercise that clears every
    gate by asking less. ⚠️ Ids are compared, not counts: swapping the hard
    case for an easy one keeps the count and drops the case.
    """
    before, after = _ids(previous), _ids(draft)
    gone = sorted(before - after)
    if gone:
        noun = "case" if isinstance(previous, CodeDraft) else "question"
        raise AuthoringError(
            f"{where}: a re-authored draft drops {len(gone)} {noun}(s) the draft it "
            f"replaces carried. A gate refusal is answered by re-authoring, never by "
            f"dropping a case or deleting a question (spec §7 §11). The ids are not "
            f"reproduced here, since a refusal never quotes a value that may be personal."
        )
    return draft


def _ids(draft: CodeDraft | QuizDraft) -> set[str]:
    """Return the ids a draft is answerable for: its case ids, or its question ids."""
    if isinstance(draft, CodeDraft):
        return {case.id for case in draft.cases}
    return {question.id for question in draft.questions}
