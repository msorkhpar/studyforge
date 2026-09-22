r"""The authoring skill's two readings: the source ledger, and the page plan.

**What it does.** Holds the executable support the exercise-authoring skill is
built on — ⭐ **the two readings it takes BEFORE it authors anything.** The
**ledger** accounts for every fenced example and every test file a source
carries; the **plan** says how many exercises a page gets, inside a band its
length sets, with every reason recorded.

**How you use it.**

    from studyforge.skills.exercises import account, digests, plan_for, take

    ledger = take(root, sources, tests, where="the ledger")
    accounted = account(ledger, origins, reasons, where="the ledger")
    plan = plan_for(words=900, skills=3, tier="core", where="the plan for page 3")

**Depends on.** `studyforge.exercise` and `studyforge.exercise.gates` for the
exercise vocabulary, the one digest and the gate registry;
`studyforge.validate.headings` for what a heading and a fence are;
`studyforge.sourcepath` and `studyforge.describe`. Standard library only.
⛔ Not on any adapter and not on any source (R1).

## What is in the package

| Module | Owns |
|---|---|
| `scan` | what a raw material file carries: its fenced blocks, and the headings over each |
| `ledger` | one entry per fenced example and per test file, and the digest of every file read |
| `accounting` | how each entry ends — an `origin`, or a written reason — and the document |
| `plan` | how many exercises a page gets, the band that bounds it, and the shortfall report |

⚠️ **`AX-07`'s `Owns` named `ledger.py` as one module and R11 refused it at 502
lines.** ⛔ The remedy this tree takes is a split at a NAMED seam, never a trim
(`AX-00`'s own words, and Ruling 261: a ceiling is not a budget). ⭐ The seams
are the two handoffs a reading makes: what the file carries → what the ledger
records → how each record is accounted for, each reading only the one before it.

## ⛔ THESE ARE THE TWO READINGS, NOT THE AUTHORING LOOP

⚠️ **Nothing here authors anything, runs a model, or writes into a corpus.**
The loop that plans a page, authors its exercises from the three source cases,
runs the gates and commits the bundles is `AX-08`'s, and its skill document
lands beside these modules. ⭐ **These are what it is built ON**, which is the
order §9 requires: a skill precedes the artifact it produces, and the readings
it is judged against precede the skill.

## ⛔ THE TWO PROPERTIES THESE MODULES EXIST TO MAKE CHECKABLE

1. ⛔ **Nothing the source already has is lost** (`E14`'s first property). The
   ledger refuses an entry that is neither the basis of an exercise nor carried
   with a written reason it is not, so a silent drop is a refusal rather than a
   sentence nobody audits.
2. ⛔ **The plan is a CEILING, never a quota** (R6, spec §7 §4). `shortfall`
   refuses a page that shipped past its ceiling and refuses a gap not named
   with a gate `exercise.gates` actually declares.

**Landed at AX-07 (E14, step 10.3).** `AX-08` adds `SKILL.md` and the loop;
`AX-10` writes the guide half.
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
    "BANDS",
    "CORE",
    "ENTRY_KEYS",
    "ENTRY_KINDS",
    "EXAMPLE",
    "INTRODUCTORY",
    "LEDGER_API",
    "LEDGER_KEYS",
    "PLAN_API",
    "PLAN_KEYS",
    "REASON_DESCRIBED",
    "REASON_KEYS",
    "SHORTFALL_KEYS",
    "SOURCE_KEYS",
    "TESTS",
    "TIERS",
    "TIER_MOVES",
    "Accounted",
    "Band",
    "Entry",
    "Fence",
    "Ledger",
    "LedgerError",
    "Plan",
    "PlanError",
    "Reason",
    "Refusal",
    "Scan",
    "Source",
    "account",
    "accounts_for",
    "band_for",
    "digests",
    "key_of",
    "ledger_document",
    "plan_document",
    "plan_for",
    "scan",
    "shortfall",
    "shortfall_document",
    "take",
]
