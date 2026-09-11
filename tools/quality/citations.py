"""The CITATION GRAMMAR: which ruling numbers a line of this project's prose CITES.

**What it does.** Reads the ruling-citation spellings the house style writes —
`Ruling 296`, `Rulings 295, 296`, `Rulings 177 + 180`, `Rulings 264–278` — and
returns the set of ruling numbers a text CITES, outside every code span and
fence. ⛔ It answers *"is this number USED as a citation here"* and nothing
else: it knows nothing about conventions, windows, backlogs or findings.

**How you use it.** `cited_numbers(text)` is the predicate;
`spellings(number)` renders the forms that satisfy it, for a message that has
to tell an office what would clear a gate. `tools.quality.reach` is the one
consumer in the tree, and re-exports both so a caller needs one import.

**Depends on.** `re`, and `tools.quality.pointers` for the two span parsers
this reuses rather than re-derives (`prose_lines`, `strip_code_spans` —
Ruling 73). Standard library only. ⛔ It imports NOTHING from
`tools.quality.reach`: the seam runs one way, and that is what lets the check
side grow without dragging the grammar with it.

## ⛔ WHY THIS IS A SIBLING MODULE AND NOT A SECTION OF `reach.py`

⚠️ **MEASURED at `6aef480`: `tools/quality/reach.py` was `385` of R11's `400`
and `tools/quality/board/register.py` `399` — two modules of one package inside
fifteen lines of a ceiling `FND-01` makes a BUILD FAILURE.** ⭐ **Ruling 261: a
ceiling is not a budget, so the next edit is a SPLIT rather than a trim** —
⛔ and the seam is not a new idea: `W133`'s taker NAMED it (*the citation
grammar as a sibling module*) and correctly refused to cut it outside their
surface. ⭐ **The two halves answer different questions — this one reads a
SPELLING, `reach.py` asks whether a RULING LANDED — so the cut is along a seam
that already existed rather than at whatever line number reached 400.**

## ⛔ REACHABILITY, not a grep for digits

⚠️ **`CTO-56`'s own dispatcher measured a bare `grep 231` matching a LINE COUNT**
— the use-versus-mention family at the level of a bare number. ⛔ **So the
predicate is the CITATION SPELLING, bounded on the right so `Ruling 27` cannot be
satisfied by `Ruling 278`** — the same literal spelling the index's own
population is derived from, and the reason a document mentioning `278` in any
other role does not count as landing.

## ⛔ THE SPELLINGS IT READS, DECLARED — and why the list is not `Ruling N` alone

⛔ **Ruling 280: a CHECK may not have a pass condition that only one undeclared
spelling satisfies**, and `reach.check_rulings_reach` is a `CHECKS` member rather
than a notice. ⭐ **`W133`'s first arm is taken here — the predicate reads the
forms the house style writes — and they are ENUMERATED, because an enumeration
is a closed claim and a paraphrase is not:**

| The spelling | Read as |
|---|---|
| `Ruling 296` — SINGULAR, one member | `296`, with the right bound |
| `Rulings 295, 296` / `Rulings 294, 295 and 296` | each member |
| `Rulings 177 + 180` — plural `+` join | `177` and `180` |
| `Rulings 294-296` / `Rulings 264–278` — range | every member of the span |

⛔ **TWO NARROWINGS go with the widening, both Ruling 65's shape — a widened
predicate that cannot fail is worse than a narrow one that can** (Ruling 185(b),
and round 60's own near-miss):

* ⭐ **A multi-member body requires the PLURAL word.** ⛔ MEASURED at `428223c`:
  all ten live plural citation sites write `Rulings` and `0` write a singular
  word with a multi-member body — while `Ruling 290, 5 distinct ids` is a
  sentence this project *does* write, and a `Rulings?`-admitting list would read
  `5` out of it. ⚠️ **So the singular keeps exactly its old reading:
  `Ruling 279-281` reads `279` and refuses `281`, unchanged.**
* ⭐ **A range naming more than `MAX_RANGE_SPAN` rulings is NOT expanded.** ⛔ One
  line reading `Rulings 1-400` would turn the reach gate green for every tail
  forever. MEASURED at `428223c`: the widest live range is `Rulings 264–278`,
  fifteen.

## ⛔ A CODE SPAN IS A MENTION, AND THE EXCLUSION IS THE WHOLE REPAIR

⛔ **The widening is unsafe without it.** The three backticked citations on ONE
line of `review-rubric.md` sit inside **Ruling 280's own text, quoting these
forms as examples** — ⭐ **and MEASURED at `428223c`, a span-blind plural
predicate reads `264`–`281` off that single line. The ruling describing the
defect would satisfy the check that tests for it, and the cliff would vanish from
the only instrument that prints it.**

⭐ **Hence `prose_lines` and `strip_code_spans` are imported from
`tools.quality.pointers` rather than rewritten** (Ruling 73): that module already
draws this line for a link inside backticks, and its `0 unresolved` is
trustworthy only because it does. ⚠️ **A fence is quoted material, an inline code
span is an example, and neither is a landing.**

## ⛔ WHAT THIS CANNOT SEE, DECLARED — because an incomplete gaps list is worse than none

⛔ **Ruling 258: a declared-gaps list is a CLOSED CLAIM.** ⭐ **Three of the four
gaps are the GRAMMAR's and live here; the fourth — that a CITATION is not a
LANDING — is a property of what `reach.py` concludes and is declared there.**
⚠️ **These three were MEASURED at `428223c` while repairing the spelling hole
rather than guessed:**

1. ⛔ **An EMPHASIS-INTERLEAVED citation reads UNREACHED** — `board.md:703`'s
   `Rulings **15**, **62** and **68**`, whose digits sit inside `**` runs. ⭐ Not
   widened over: Ruling 185 forbids a taker widening a ruling's own words, and
   Ruling 280's are "the forms the house style writes" — this is ONE site of ten.
2. ⛔ **A citation that WRAPS A LINE BREAK is read only as far as the break** —
   `board.md:115` writes `Rulings 106 and` with `174` on the next line, so `106`
   reads cited and `174` does not. ⭐ Line-scoped because `prose_lines` is.
3. ⛔ **`Rulings minted: 198-202`** (`review-rubric.md:292`) puts a word between
   the plural and its members and reads UNREACHED.

⭐ **Consequence, carried by Ruling 280's SECOND arm and Ruling 281's audience
clause: the caller's FINDING names the spellings that clear it, and the caller's
NOTICE says beside its own number that `unreached` is an UPPER BOUND.** ⛔ An
instrument that under-reads must say so where the number is read, not in a module
docstring the reader of a failure never opens.
"""

from __future__ import annotations

import re

from tools.quality.pointers import prose_lines, strip_code_spans

#: The most RULINGS a range may name and still be expanded to its members. ⛔ A
#: unit — rulings, counted inclusively — not a bare number (Ruling 277).
#:
#: ⭐ **25 because that is the width of Ruling 245's measured cliff (`217`–`241`),
#: which is the same figure and the same reason as `reach.REACH_WINDOW`: a range
#: covering the whole notice window in one line is a pass condition nobody
#: verified (Ruling 65).** ⛔ **It is written here rather than imported because
#: the seam runs one way — `reach` imports this module and this module imports
#: nothing back — so the equality is ASSERTED, in
#: `tools/tests/quality/test_reach.py`, rather than expressed as an assignment.**
#: ⚠️ A reader changing either figure has a red test, not a silent divergence.
MAX_RANGE_SPAN = 25

#: Hyphen-minus and EN DASH — the two range separators the house style writes.
#: ⛔ The EM DASH is excluded deliberately: this project uses it as a sentence
#: dash on nearly every line, so admitting it would read a citation out of
#: `Ruling 296 — a heading` plus whatever number followed.
_RANGE_DASHES = "\\-\u2013"

#: One member: up to four digits, every ruling number this project has and the
#: impossible-control probes besides.
_MEMBER = r"\d{1,4}"

#: What joins two members: a comma (optionally with `and`), a bare `and`, a `+`,
#: or a range dash.
_JOIN = rf"(?:\s*,\s*(?:and\s+)?|\s+and\s+|\s*\+\s*|\s*[{_RANGE_DASHES}]\s*)"

#: ⛔ SINGULAR, one member, with the right bound that keeps `Ruling 27` out of
#: `Ruling 278`. ⭐ Disjoint from `_PLURAL` by construction: `\s+` demands
#: whitespace exactly where the plural writes its `s`.
_SINGULAR = re.compile(rf"Ruling\s+({_MEMBER})(?!\d)")

#: ⛔ PLURAL, one or more members. The body goes to `_members`, not to this
#: pattern: a range and a list look the same until their separator is read.
_PLURAL = re.compile(rf"Rulings\s+(?P<body>{_MEMBER}(?:{_JOIN}{_MEMBER})*)(?!\d)")

#: Walks a body: a member, or the dash making the previous member a low bound.
_BODY_TOKEN = re.compile(rf"(?P<member>{_MEMBER})|(?P<dash>[{_RANGE_DASHES}])")


def spellings(number: int) -> str:
    """Return the citation forms that satisfy this grammar, for `number`.

    ⛔ **Ruling 280's second arm, and it is why this is a function rather than a
    constant**: a finding that said "write it in the house spelling" would put
    the pass condition back in the reader. ⭐ The caller is the finding's own
    message, so the office that trips the gate is told what clears it.
    """
    low, lower = number - 1, number - 2
    return (
        f"`Ruling {number}`, `Rulings {low}, {number}`, `Rulings {low} and {number}`, "
        f"`Rulings {low} + {number}`, or a range containing it — "
        f"`Rulings {lower}-{number}` or `Rulings {lower}\u2013{number}` (en dash). "
        f"⛔ A citation inside a code span or a ``` fence is an EXAMPLE and is not "
        f"read; nor is one written with emphasis inside it (`Rulings **{low}**, "
        f"**{number}**`) or wrapped across a line break"
    )


def _members(body: str) -> set[int]:
    """Return every ruling number a plural citation's `body` names.

    ⛔ A dash between two members expands to the inclusive span, which is the
    whole point of reading the range spelling at all — `Rulings 264–278` cites
    fifteen rulings and not two. ⚠️ A range naming more than `MAX_RANGE_SPAN`
    rulings, or one that runs backwards, is read as its two endpoints instead.
    """
    found: set[int] = set()
    previous: int | None = None
    ranged = False
    for token in _BODY_TOKEN.finditer(body):
        if token.group("dash"):
            ranged = previous is not None
            continue
        number = int(token.group("member"))
        if ranged and previous is not None and 0 < number - previous < MAX_RANGE_SPAN:
            found.update(range(previous, number + 1))
        else:
            found.add(number)
        previous, ranged = number, False
    return found


def cited_numbers(text: str) -> set[int]:
    """Return every ruling number `text` CITES, in prose, outside every code span.

    ⭐ The two exclusions are `pointers`' own, reused (Ruling 73): a fenced block
    is quoted material and an inline code span is an example. ⛔ Without them the
    widened predicate reads Ruling 280's own illustration of this defect as a
    landing of the eight rulings it quotes — measured, 8 of 8.
    """
    found: set[int] = set()
    for _, line in prose_lines(text):
        prose = strip_code_spans(line)
        for match in _SINGULAR.finditer(prose):
            found.add(int(match.group(1)))
        for match in _PLURAL.finditer(prose):
            found |= _members(match.group("body"))
    return found


#: ⭐ Named so the mirror test can assert this module's surface rather than its
#: internals — the regexes are private on purpose: a caller that reached for
#: `_PLURAL` would be re-deriving the grammar the seam exists to hold once.
__all__ = [
    "MAX_RANGE_SPAN",
    "cited_numbers",
    "spellings",
]
