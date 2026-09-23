r"""The authoring skill: its two readings, and the loop that plans, authors, gates and commits.

**What it does.** Holds the executable half of the exercise-authoring skill
whose procedure is `SKILL.md` beside these modules. ⭐ **Two readings are taken
BEFORE anything is authored** — the **ledger**, which accounts for every fenced
example and every test file a source carries, and the **plan**, which says how
many exercises a page gets inside a band its length sets. ⭐ **The loop** then
drafts each planned exercise through the converting agent's author, gates it,
re-drafts it inside a fixed budget, and commits what cleared into the corpus
repository — additively, and once.

**How you use it.**

    from studyforge.skills.exercises import author_corpus

    authored = author_corpus(root, source="demo", material=material, graders=graders,
                             pages=pages, author=author, judge=judge, runner=runner)
    authored.shortfalls         # every exercise a gate refused, named (spec §7 §11)

    ledger = take(root, sources, tests, where="the ledger")   # the readings, alone
    plan = plan_for(words=900, skills=3, tier="core", where="the plan for page 3")

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
| `plan` | how many exercises a page gets, the band that bounds it, and the shortfall report |
| `drafts` | the page, the three source cases, the brief, the two draft shapes, and no retreat |
| `gating` | one draft staged, run through the caller's runner, and answered by every gate |
| `loop` | one page: planned, drafted, gated, re-drafted inside the budget, reported |
| `corpus` | the whole pass: the ledger once, every page, the reasons, the additive commit |

⚠️ **`AX-07`'s `Owns` named `ledger.py` as one module and R11 refused it at 502
lines**, and `AX-08`'s loop is four modules for the same reason: the remedy
this tree takes is a split at a NAMED seam, never a trim (Ruling 261). ⭐ The
loop's seams are the handoffs a pass makes: what an author is asked → what a
gate answers → what one page ships → what the corpus commits.

## ⛔ THE PROPERTIES THIS PACKAGE EXISTS TO MAKE CHECKABLE

1. ⛔ **Nothing the source already has is lost** (`E14`'s first property). The
   ledger refuses an entry that is neither the basis of an exercise nor carried
   with a written reason it is not.
2. ⛔ **The plan is a CEILING, never a quota** (R6, spec §7 §4). `shortfall`
   refuses a page that shipped past its ceiling and a gap not named with a gate.
3. ⛔ **A gate failure is re-authored within `ATTEMPTS`, never by loosening a
   gate, dropping a case or deleting a question** (spec §7 §11). No gate takes
   an option, and a retry carrying fewer case or question ids is refused.
4. ⛔ **The pass writes only inside the corpus root, only additively (R3), and
   re-running it with nothing changed rewrites nothing (R10).**
5. ⛔ **Every exercise it writes is `generated`/`advisory`** (R5). It
   supersedes `SK-04`'s refusal of a grader-less source: such a source gets
   exercises authored for it, and the gates are where its honesty lives.

**Landed at AX-07 and AX-08 (E14, step 10.3).** `AX-10` writes the guide half.
"""

from __future__ import annotations

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
from studyforge.skills.exercises.corpus import (
    COVERAGE_API,
    COVERAGE_FILENAME,
    COVERAGE_KEYS,
    LEDGER_PATH,
    SHORTFALL_REPORT_KEYS,
    Authored,
    Covered,
    author_corpus,
    commit,
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
from studyforge.skills.exercises.gating import (
    OUTPUT_LINES,
    QUIZ_API,
    QUIZ_DOCUMENT,
    QUIZ_KEYS,
    Gated,
    Ran,
    Runner,
    gate_code,
    gate_quiz,
    json_bytes,
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
    require_after_carried,
)
from studyforge.skills.exercises.plan import (
    ADVANCED,
    BANDS,
    CORE,
    INTRODUCTORY,
    PLAN_API,
    PLAN_KEYS,
    REASON_KEYS,
    SHORTFALL_KEYS,
    TIER_MOVES,
    TIERS,
    Band,
    Plan,
    PlanError,
    Reason,
    Refusal,
    band_for,
    plan_document,
    plan_for,
    shortfall,
    shortfall_document,
)
from studyforge.skills.exercises.scan import Fence, Scan, scan

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.skills.exercises.ledger` directly is a consumer this contract
#: failed — `docs/conventions/module-structure.md` calls `__init__.py` the
#: contract, and this is what it says.
__all__ = [
    "ACCOUNTED_KEYS",
    "ADVANCED",
    "ATTEMPTS",
    "AUTHORED_PROVENANCE",
    "AUTHORED_TRUST",
    "BANDS",
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
    "PLAN_API",
    "PLAN_KEYS",
    "QUIZ_API",
    "QUIZ_DOCUMENT",
    "QUIZ_KEYS",
    "REASON_DESCRIBED",
    "REASON_KEYS",
    "SHORTFALL_KEYS",
    "SHORTFALL_REPORT_KEYS",
    "SOURCE_CASES",
    "SOURCE_KEYS",
    "TESTS",
    "TIERS",
    "TIER_MOVES",
    "Accounted",
    "Author",
    "Authored",
    "AuthoringError",
    "Band",
    "Brief",
    "CodeDraft",
    "Covered",
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
    "QuizDraft",
    "Ran",
    "Reason",
    "Refusal",
    "Runner",
    "Scan",
    "Shortfall",
    "Source",
    "account",
    "accounts_for",
    "author_corpus",
    "author_page",
    "carried_practices",
    "band_for",
    "commit",
    "digests",
    "gate_code",
    "gate_quiz",
    "json_bytes",
    "key_of",
    "ledger_document",
    "page_entries",
    "plan_document",
    "plan_for",
    "require_after_carried",
    "require_draft",
    "require_no_retreat",
    "require_page",
    "scan",
    "shortfall",
    "shortfall_document",
    "source_case",
    "take",
    "words_of",
]
