r"""The CITATION GRAMMAR: which ruling numbers a line of this project's prose CITES.

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

## ⛔ A CITATION MAY SPAN A LINE BREAK, AND THE BLOCK IS WHAT BOUNDS IT

⛔ **`W145`: a citation can be UNMADE with no word changing.** ⭐ An ordinary
re-wrap moved `166` onto the next line of `review-rubric.md` and this grammar
stopped reading it, while the diff a reviewer read showed a reflowed paragraph.
⚠️ **The patterns always admitted the break — every separator here is `\s`,
which matches a newline — so the blindness was the LINE LOOP and never the
grammar, and the remedy is to feed it a BLOCK rather than a line.**

⛔ **A BLOCK IS NOT THE DOCUMENT, and that is the whole safety of it.** ⚠️ Joining
a document's lines before the exclusions run would read every fenced example as a
landing — measured below, 8 of 8 — and joining across a paragraph boundary would
invent citations no renderer shows, which is the invented-anchor family
`pointers.heading_slugs` is fence-aware to avoid. ⭐ **So two consecutive prose
lines are in ONE block only when none of these stands between them, and the list
is a CLOSED CLAIM** (Ruling 258):

| The boundary | Why no citation crosses it |
|---|---|
| a blank line | the paragraph ended |
| a gap in the line numbers | a fence stood there and `prose_lines` dropped it |
| a different blockquote prefix | quoted text and plain text are two blocks |
| the upper line is a heading or a table row | each is a block of ONE line |
| the lower line OPENS a block | see below — it belongs to the block it starts |
| either line leaves a code span OPEN | see below — a MENTION must not be joined |

⭐ **A line OPENS a block when it is a heading, a table row, a thematic break, a
bullet item, or the `1.`/`1)` ordered item CommonMark lets interrupt a
paragraph.** ⚠️ Only `1`, never `\d+`: `166. That is` mid-paragraph is a SENTENCE,
and a `\d+[.)]` reading here would refuse the very wraps this reads.

⛔ **AND AN UNCLOSED CODE SPAN ENDS THE BLOCK, which is the one way this could
have weakened `W133`'s exclusion.** ⭐ `strip_code_spans` is LINE-scoped, so a
span opened on one line and closed on the next survives both — and a join across
that pair would carry a MENTION into the reading. ⚠️ **Refused rather than
declared, and the refusal is measured to cost nothing: all 14 live wrapped pairs
in `docs/conventions/` leave both of their lines balanced.**

⭐ **MEASURED at `fc56011`, role `wt/dev2`, pinned image, over the eight documents
`reach._conventions(root)` names: the block reading GAINS `{166}` and LOSES
nothing** — exactly the citation a re-wrap had unmade, and no invention anywhere
else in that corpus. ⚠️ **Over all 398 markdown files of the tree it gains 36 and
loses 0**, and every gain read back as a real citation.

## ⛔ WHAT THIS CANNOT SEE, DECLARED — because an incomplete gaps list is worse than none

⛔ **Ruling 258: a declared-gaps list is a CLOSED CLAIM.** ⭐ **Two of the three
gaps are the GRAMMAR's and live here; the third — that a CITATION is not a
LANDING — is a property of what `reach.py` concludes and is declared there.**
⚠️ **These two were MEASURED at `428223c` while repairing the spelling hole
rather than guessed, and the WRAPPED citation that stood third among them was
CLOSED by `W145` rather than dropped from the claim:**

1. ⛔ **An EMPHASIS-INTERLEAVED citation reads UNREACHED** — `board.md:703`'s
   `Rulings **15**, **62** and **68**`, whose digits sit inside `**` runs. ⭐ Not
   widened over: Ruling 185 forbids a taker widening a ruling's own words, and
   Ruling 280's are "the forms the house style writes" — this is ONE site of ten.
2. ⛔ **`Rulings minted: 198-202`** (`review-rubric.md:292`) puts a word between
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

#: A line's BLOCKQUOTE MARKERS, split from the text they prefix. ⛔ Two lines
#: share a block only when these are IDENTICAL — `>` text and plain text are two
#: markdown blocks — and splitting them rather than testing for them is what lets
#: a citation wrapped INSIDE a quote be read at all (`board.md:864`, measured).
_QUOTE = re.compile(r"^(?P<quote>(?:[ \t]*>)*)(?P<body>.*)$")

#: A line that OPENS a markdown block, so no citation reaches it from above.
#: ⚠️ The ordered item is `1` alone and not `\d+`: CommonMark lets only a list
#: starting at one interrupt a paragraph, and `166. That is` mid-paragraph is a
#: SENTENCE — a `\d+[.)]` reading here would refuse the very wraps this reads.
_OPENS = re.compile(r"[ \t]*(?:[#|]|[-*+][ \t]|1[.)][ \t]|(?:-{3,}|\*{3,}|_{3,})[ \t]*$)")

#: A line that is a block BY ITSELF, so no citation leaves it downward: a heading
#: ends at its newline, and a table row cannot flow into the row beneath it.
_CLOSES = re.compile(r"[ \t]*[#|]")


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
        f"**{number}**`). ⭐ A citation WRAPPED across a line break IS read, so long "
        f"as the two lines are one paragraph: a blank line, a heading, a table row, "
        f"a fence or a list marker between them ends it, and the number below is then "
        f"not read as a citation"
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


def _unquote(line: str) -> tuple[str, str]:
    """Split a line's blockquote markers from the text they prefix.

    ⚠️ The markers are returned rather than discarded: two lines are in one
    block only when theirs are the SAME, so a quoted line and a plain one below
    it stay apart while two quoted lines join.
    """
    match = _QUOTE.match(line)
    return match.group("quote", "body") if match else ("", line)


def _blocks(text: str) -> list[str]:
    """Return the prose BLOCKS of `text` — the runs of lines a citation may span.

    ⛔ **The exclusions run BEFORE the join, per line, and that ordering is the
    safety** (Ruling 73, and `W145`'s clause 2): `prose_lines` has already
    dropped every fence, `strip_code_spans` blanks this line's spans, and only
    then may a line be appended to the one above it. ⚠️ The boundaries are the
    module docstring's table, and they are a closed claim rather than a taste.
    """
    blocks: list[list[str]] = []
    previous: tuple[int, str, str] | None = None
    for number, line in prose_lines(text):
        quote, body = _unquote(strip_code_spans(line))
        if not body.strip():
            previous = None
            continue
        joins = (
            previous is not None
            and number == previous[0] + 1
            and quote == previous[1]
            and "`" not in previous[2]
            and "`" not in body
            and not _CLOSES.match(previous[2])
            and not _OPENS.match(body)
        )
        if joins:
            blocks[-1].append(body)
        else:
            blocks.append([body])
        previous = (number, quote, body)
    return ["\n".join(block) for block in blocks]


def cited_numbers(text: str) -> set[int]:
    """Return every ruling number `text` CITES, in prose, outside every code span.

    ⭐ The two exclusions are `pointers`' own, reused (Ruling 73): a fenced block
    is quoted material and an inline code span is an example. ⛔ Without them the
    widened predicate reads Ruling 280's own illustration of this defect as a
    landing of the eight rulings it quotes — measured, 8 of 8.

    ⚠️ **The unit is a BLOCK and not a line** (`W145`): a citation the house
    style wrapped is still a citation, and reading one line at a time let an
    ordinary re-wrap unmake one with no word changing.
    """
    found: set[int] = set()
    for block in _blocks(text):
        for match in _SINGULAR.finditer(block):
            found.add(int(match.group(1)))
        for match in _PLURAL.finditer(block):
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
