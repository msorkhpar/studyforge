r"""The authoring skill: its two readings, and the loop that plans, authors, gates and commits.

**What it does.** Holds the executable half of the exercise-authoring skill
whose procedure is `SKILL.md` beside these modules. ⭐ **Two readings are taken
BEFORE anything is authored** — the **ledger**, which accounts for every fenced
example and every test file a source carries, and the **plan**, which says which
exercises a page gets by the aspects it teaches, each checked or excused.
⭐ **The loop** then
drafts each planned exercise through the converting agent's author, gates it,
re-drafts it inside a fixed budget, and commits what cleared into the corpus
repository — additively, and once.

**How you use it.**

    from studyforge.skills.exercises import author_corpus

    authored = author_corpus(root, source="demo", material=material, graders=graders,
                             pages=pages, author=author, judge=judge, runner=runner)
    authored.shortfalls         # every exercise a gate refused, named (spec §7 §11)

    ledger = take(root, sources, tests, where="the ledger")   # the readings, alone
    plan = plan_for(aspects, tier="core", where="the plan for page 3")

**Depends on.** `studyforge.exercise` — its record, `bundle`, `gates` and
`quiz` — for everything an exercise is; `studyforge.validate.headings` for what
a heading and a fence are; `studyforge.archive.scrub` for R7;
`studyforge.address`, `studyforge.sourcepath` and `studyforge.describe`.
Standard library only. ⛔ Not on any adapter, any source (R1) or `execute`: the
runner is the caller's.

## What is in the package

| Module | Owns |
|---|---|
| `SKILL.md` | ⭐ the procedure a converting agent follows — it precedes every module here (§9) |
| `scan` | what a raw material file carries: its fenced blocks, and the headings over each |
| `ledger` | one entry per fenced example and per test file, and the digest of every file read |
| `accounting` | how each entry ends — an `origin`, or a written reason — and the document |
| `aspects` | a page's important ideas, and how each ends — an exercise, or a reason |
| `plan` | which exercises a page gets, read off its aspects, and the shortfall report |
| `drafts` | the page, the three source cases, the brief, the two draft shapes, and no retreat |
| `gating` | one draft staged, run through the caller's runner, and answered by every gate |
| `quizdoc` | a quiz's own document read back, through R9's guard, as an adapter reads it |
| `loop` | one page: planned, drafted, gated, re-drafted inside the budget, reported |
| `merge` | one pass's ledger merged into the committed one, and the delta it reports |
| `writes` | the additive commit: every file checked against the tree before any is written |
| `corpus` | the whole pass: the ledger once, every page, the reasons, the merge and the commit |

⚠️ **`ledger.py` as one module was refused by R11 at 502
lines**, and the authoring loop is four modules for the same reason: the remedy
this tree takes is a split at a NAMED seam, never a trim. ⭐ The
loop's seams are the hand-overs a pass makes: what an author is asked → what a
gate answers → what one page ships → what the corpus commits.

## ⛔ THE PROPERTIES THIS PACKAGE EXISTS TO MAKE CHECKABLE

1. ⛔ **Nothing the source already has is lost** (spec §7, section 3). The
   ledger refuses an entry that is neither the basis of an exercise nor carried
   with a written reason it is not.
2. ⛔ **The plan is a CEILING, never a quota** (R6, spec §7 §4). `shortfall`
   refuses a page that shipped past its ceiling and a gap not named with a gate.
   ⭐ **Its count is set by COVERAGE, not by length**: every aspect a page
   teaches is checked by a named exercise or
   carried by a written reason, and an aspect with neither is refused.
3. ⛔ **A gate failure is re-authored within `ATTEMPTS`, never by loosening a
   gate, dropping a case or deleting a question** (spec §7 §11). No gate takes
   an option, and a retry carrying fewer case or question ids is refused.
4. ⛔ **The pass writes only inside the corpus root, only additively (R3), and
   re-running it with nothing changed rewrites nothing (R10).**
5. ⛔ **Every exercise it writes is `generated`/`advisory`** (R5). It
   supersedes the earlier refusal of a grader-less source: such a source gets
   exercises authored for it, and the gates are where its honesty lives.
"""

from __future__ import annotations

from studyforge.exercise.bundle import PlantSpec, Replacement
from studyforge.skills.exercises.accounting import (
    ACCOUNTED_KEYS,
    LEDGER_API,
    LEDGER_KEYS,
    REASON_DESCRIBED,
    Accounted,
    account,
    accounts_for,
    ledger_document,
)
from studyforge.skills.exercises.aspects import (
    ASPECT_KEYS,
    SECTION,
    Aspect,
    AspectError,
    aspect_document,
    require_aspects,
    require_read,
)
from studyforge.skills.exercises.corpus import (
    COVERAGE_API,
    COVERAGE_FILENAME,
    COVERAGE_KEYS,
    LEDGER_PATH,
    SHORTFALL_REPORT_KEYS,
    Authored,
    Covered,
    author_corpus,
)
from studyforge.skills.exercises.drafts import (
    ATTEMPTS,
    AUTHORED_PROVENANCE,
    AUTHORED_TRUST,
    CODE_AND_TESTS,
    CODE_NO_TESTS,
    NEITHER,
    SOURCE_CASES,
    Author,
    AuthoringError,
    Brief,
    CodeDraft,
    DeckDraft,
    EditedFile,
    Judge,
    Page,
    QuizDraft,
    page_entries,
    require_draft,
    require_no_retreat,
    require_page,
    source_case,
    words_of,
)
from studyforge.skills.exercises.deckgating import gate_deck
from studyforge.skills.exercises.gating import (
    OUTPUT_LINES,
    Gated,
    Ran,
    Runner,
    gate_code,
    gate_quiz,
    json_bytes,
)
from studyforge.skills.exercises.deckdoc import (
    DECK_API,
    DECK_DOCUMENT,
    Deck,
    DeckRefused,
    deck_of,
)
from studyforge.skills.exercises.ledger import (
    ENTRY_KEYS,
    ENTRY_KINDS,
    EXAMPLE,
    SOURCE_KEYS,
    TESTS,
    Entry,
    Ledger,
    LedgerError,
    Source,
    digests,
    key_of,
    take,
)
from studyforge.skills.exercises.loop import (
    PageOutcome,
    Shortfall,
    author_page,
    carried_practices,
    plan_page,
    require_after_carried,
)
from studyforge.skills.exercises.merge import Delta, ledger_rows, merged, row_key, source_key
from studyforge.skills.exercises.plan import (
    ADVANCED,
    CORE,
    INTRODUCTORY,
    PERSONAL_DATA,
    PLAN_API,
    PLAN_KEYS,
    PLANNED_KEYS,
    SHORTFALL_KEYS,
    TIERS,
    Plan,
    PlanError,
    Planned,
    Refusal,
    plan_document,
    plan_for,
    shortfall,
    shortfall_document,
)
from studyforge.skills.exercises.practised import practised
from studyforge.skills.exercises.quizdoc import (
    QUIZ_API,
    QUIZ_DOCUMENT,
    QUIZ_KEYS,
    Quiz,
    QuizRefused,
    quiz_of,
)
from studyforge.skills.exercises.scan import Fence, Scan, scan
from studyforge.skills.exercises.writes import commit

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.skills.exercises.ledger` directly is a consumer this contract
#: failed — R17 makes `__init__.py` the
#: contract, and this is what it says.
__all__ = [
    "ACCOUNTED_KEYS",
    "ADVANCED",
    "ASPECT_KEYS",
    "ATTEMPTS",
    "AUTHORED_PROVENANCE",
    "AUTHORED_TRUST",
    "CODE_AND_TESTS",
    "CODE_NO_TESTS",
    "CORE",
    "COVERAGE_API",
    "COVERAGE_FILENAME",
    "COVERAGE_KEYS",
    "ENTRY_KEYS",
    "ENTRY_KINDS",
    "EXAMPLE",
    "INTRODUCTORY",
    "LEDGER_API",
    "LEDGER_KEYS",
    "LEDGER_PATH",
    "NEITHER",
    "OUTPUT_LINES",
    "PERSONAL_DATA",
    "PLANNED_KEYS",
    "PLAN_API",
    "PLAN_KEYS",
    "QUIZ_API",
    "QUIZ_DOCUMENT",
    "QUIZ_KEYS",
    "REASON_DESCRIBED",
    "SECTION",
    "SHORTFALL_KEYS",
    "SHORTFALL_REPORT_KEYS",
    "SOURCE_CASES",
    "SOURCE_KEYS",
    "TESTS",
    "TIERS",
    "Accounted",
    "Aspect",
    "AspectError",
    "Author",
    "Authored",
    "AuthoringError",
    "Brief",
    "CodeDraft",
    "DECK_API",
    "DECK_DOCUMENT",
    "Deck",
    "DeckDraft",
    "DeckRefused",
    "EditedFile",
    "PlantSpec",
    "Replacement",
    "Covered",
    "Delta",
    "Entry",
    "Fence",
    "Gated",
    "Judge",
    "Ledger",
    "LedgerError",
    "Page",
    "PageOutcome",
    "Plan",
    "PlanError",
    "Planned",
    "Quiz",
    "QuizDraft",
    "QuizRefused",
    "Ran",
    "Refusal",
    "Runner",
    "Scan",
    "Shortfall",
    "Source",
    "account",
    "accounts_for",
    "aspect_document",
    "author_corpus",
    "author_page",
    "carried_practices",
    "commit",
    "digests",
    "deck_of",
    "gate_code",
    "gate_deck",
    "gate_quiz",
    "json_bytes",
    "key_of",
    "ledger_document",
    "ledger_rows",
    "merged",
    "page_entries",
    "plan_document",
    "plan_for",
    "plan_page",
    "practised",
    "quiz_of",
    "require_after_carried",
    "require_aspects",
    "require_draft",
    "require_no_retreat",
    "require_page",
    "require_read",
    "row_key",
    "scan",
    "shortfall",
    "shortfall_document",
    "source_case",
    "source_key",
    "take",
    "words_of",
]
