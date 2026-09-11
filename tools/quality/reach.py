"""Ruling 245's cliff, mechanised: the rulings index's TAIL is reachable from `docs/conventions/`.

**What it does.** Asserts that the newest ruling in `docs/tasks/rulings-index.md`
— its **tail** — is cited inside `docs/conventions/`, and prints a census of the
wider tail window through the notice channel. ⛔ A ruling that only its own
record remembers is a ruling whose cost is paid by the next office that did not
read that round (Ruling 245).

**How you use it.** `check_rulings_reach(root)` is registered in
`tools.quality.CHECKS`; `reach_notice(root)` is registered in `NOTICES`. The
remedy a finding gives is an edit, never a regeneration: a convention document
has to carry the clause.

**Depends on.** `tools.quality.rulings.derive` for the population and the tail,
`tools.quality.report` for the answer, `tools.quality.pointers` for the two span
parsers this reuses rather than re-derives (`prose_lines`, `strip_code_spans` —
Ruling 73), and `re`. Standard library only. ⛔ It does **not** read
`config.SCAN_ROOTS`: its subject is one named directory of documents, which is
the whole exemption mechanism (see below).

## ⛔ Why the CHECK is the TAIL and the NOTICE is the WINDOW

⭐ **Ruling 245 scoped the instrument to the tail deliberately, and the scope is
the part most likely to be widened by a well-meaning taker** — quoted rather
than paraphrased (Ruling 195):

> ⚠️ **Scoped deliberately to the TAIL and not to all 241: a sweep demanding
> every ruling reach a convention would fire on 25 at once and on rulings that
> correctly landed in code, and a notice whose first wave fires 25 times is a
> notice nobody reads twice.**

⛔ **So the FINDING binds one ruling — the tail — and that is the ruling a round
has just minted.** ⭐ It fires on exactly the failure the cliff was made of: a
round mints a ruling, writes it into its own record, and lands it nowhere. ⚠️ It
cannot fire twenty-five times on its first wave, which is the property that
makes it readable.

⭐ **The NOTICE carries the backlog instead, enumerated by number**, because a
hole nobody can fail you for still has to be visible (FND-07's argument, and
Ruling 48's: the unreached count means nothing without its denominator).

## ⛔ REACHABILITY, not a grep for digits

⚠️ **`CTO-56`'s own dispatcher measured a bare `grep 231` matching a LINE COUNT**
— the use-versus-mention family at the level of a bare number. ⛔ **So the
predicate is the CITATION SPELLING, bounded on the right so `Ruling 27` cannot be
satisfied by `Ruling 278`** — the same literal spelling the index's own
population is derived from, and the reason a document mentioning `278` in any
other role does not count as landing.

## ⛔ THE SPELLINGS IT READS, DECLARED — and why the list is not `Ruling N` alone

⛔ **Ruling 280: a CHECK may not have a pass condition that only one undeclared
spelling satisfies**, and this is a `CHECKS` member rather than a notice.
⭐ **`W133`'s first arm is taken here — the predicate reads the forms the house
style writes — and they are ENUMERATED, because an enumeration is a closed claim
and a paraphrase is not:**

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
  line reading `Rulings 1-400` would turn this gate green for every tail forever.
  MEASURED at `428223c`: the widest live range is `Rulings 264–278`, fifteen.

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

## ⛔ Why `docs/conventions/` and nothing else

⭐ **Ruling 200 and Ruling 212 already decided what is NOT an artifact**, and
`board.md` carries their three exclusions by name: `docs/tasks/handoffs/` is a
record; `BOARD-ARCHIVE.md` is also a record; and `docs/tasks/rulings-index.md` is
GENERATED from the records, so every ruling is in it by construction. ⛔ **A
subject confined to `docs/conventions/` excludes all three structurally rather
than by a filter a reader has to remember** — which is the same exemption shape
`source_names` uses, and for the same reason.

## ⛔ WHAT THIS CANNOT SEE, DECLARED — because an incomplete gaps list is worse than none

⛔ **Ruling 258: a declared-gaps list is a CLOSED CLAIM.** ⭐ **The gaps are four,
and the last three were MEASURED at `428223c` while repairing the spelling hole
rather than guessed:**

1. **A CITATION is not a LANDING** — the original gap, unchanged, spelled out
   below.
2. ⛔ **An EMPHASIS-INTERLEAVED citation reads UNREACHED** — `board.md:703`'s
   `Rulings **15**, **62** and **68**`, whose digits sit inside `**` runs. ⭐ Not
   widened over: Ruling 185 forbids a taker widening a ruling's own words, and
   Ruling 280's are "the forms the house style writes" — this is ONE site of ten.
3. ⛔ **A citation that WRAPS A LINE BREAK is read only as far as the break** —
   `board.md:115` writes `Rulings 106 and` with `174` on the next line, so `106`
   reads cited and `174` does not. ⭐ Line-scoped because `prose_lines` is.
4. ⛔ **`Rulings minted: 198-202`** (`review-rubric.md:292`) puts a word between
   the plural and its members and reads UNREACHED.

⭐ **Consequence, carried by Ruling 280's SECOND arm and Ruling 281's audience
clause: the FINDING names the spellings that clear it, and the NOTICE says beside
its own number that `unreached` is an UPPER BOUND.** ⛔ An instrument that
under-reads must say so where the number is read, not in a module docstring the
reader of a failure never opens.

⭐ So gap 1, named rather than discovered: **this asserts a CITATION, not a
LANDING.** ⚠️ A
convention that merely *mentions* `Ruling N` in passing — inside a neighbouring
ruling's prose, say — satisfies it exactly as a section that carries the clause
does. ⛔ **MEASURED, and it is why the gap is stated rather than implied: at
`6c4e3d0` rulings `235`, `238`, `240` and `241` all read REACHED over Ruling
245's own population of `217`–`241`, and three of those four were incidental
mentions inside round 58's sections rather than the clause `W126` was routed to
land.** ⭐ **Ruling 200 already drew this boundary and drew it the same way —
*"the reviewer confirms one of them is the document the rule was WRITTEN
INTO"*** — so the machine's half is the citation and the reviewer's half is
whether it teaches anything. ⚠️ **A check that tried to judge the second would be
judging prose, which is the one thing this floor never does.**

## ⚠️ An empty population is a REFUSAL here, not a pass

⛔ **Ruling 191: an empty population returns the PASS reading rather than no
reading.** ⭐ So the two empties are separated: a tree with **no ruling records**
is not this repository and owes nothing (the notice says so); a tree that HAS
ruling records and **no readable `docs/conventions/`** is this repository with
its subject missing, and that is a finding. ⚠️ Without the split, deleting the
conventions directory would turn this check green.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality.pointers import prose_lines, strip_code_spans
from tools.quality.report import Finding
from tools.quality.rulings.derive import records, series, sites

RULE_UNREACHED = "rulings-reach"

#: The directory a ruling must reach. ⛔ Ruling 245's subject, and the structural
#: form of Ruling 212's three exclusions — see the contract above.
CONVENTIONS_DIR = "docs/conventions"

#: How many of the newest rulings the NOTICE reports on. ⭐ 25 because that is
#: the population Ruling 245 measured (`217`–`241`, reached 0), so the notice's
#: window is the cliff's own width rather than a number somebody liked.
#: ⛔ It bounds the NOTICE only; the FINDING binds the tail alone.
REACH_WINDOW = 25

#: The most RULINGS a range may name and still be expanded to its members. ⛔ A
#: unit — rulings, counted inclusively — not a bare number (Ruling 277). ⭐ Equal
#: to `REACH_WINDOW`: a range covering the whole notice window in one line is a
#: pass condition nobody verified (Ruling 65).
MAX_RANGE_SPAN = REACH_WINDOW

#: Hyphen-minus and EN DASH — the two range separators the house style writes.
#: ⛔ The EM DASH is excluded deliberately: this project uses it as a sentence
#: dash on nearly every line, so admitting it would read a citation out of
#: `Ruling 296 — a heading` plus whatever number followed.
_RANGE_DASHES = "\\-\u2013"

#: One member: up to four digits, every ruling number this project has and the
#: `9999` probe besides.
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
    """Return the citation forms that satisfy this instrument, for `number`.

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


def _conventions(root: Path) -> list[Path]:
    """Return every markdown document under `CONVENTIONS_DIR`, sorted for R10."""
    directory = root / CONVENTIONS_DIR
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def _citations(documents: list[str]) -> set[int]:
    r"""Return every ruling number cited anywhere in `documents`.

    ⛔ Computed ONCE for the whole window rather than per number: the predicate
    is no longer a single `re.search` per ruling, and re-deriving it twenty-five
    times over eight documents would read the same prose two hundred times.
    """
    found: set[int] = set()
    for text in documents:
        found |= cited_numbers(text)
    return found


def _tail(root: Path) -> int | None:
    """Return the highest number in the index's contiguous series, or None if none."""
    written = {site.number for record in records(root) for site in sites(record)}
    if not written:
        return None
    tail = series(written).tail
    return tail or None


def check_rulings_reach(root: Path) -> list[Finding]:
    """Return a finding when the newest ruling is cited in no convention document.

    ⛔ **A tree with no ruling records passes and says so through the notice**
    (Ruling 191, and `check_rulings_index`'s own precedent): the floor runs over
    a corpus, a consumer repository and an installed tree, and none of those
    owes a rulings index or a conventions directory.
    """
    tail = _tail(root)
    if tail is None:
        return []
    paths = _conventions(root)
    if not paths:
        return [
            Finding(
                CONVENTIONS_DIR,
                0,
                RULE_UNREACHED,
                "this tree has ruling records and no readable convention documents, so "
                "no ruling can reach one. An empty population is refused here rather "
                "than passed (Ruling 191).",
            )
        ]
    documents = [path.read_text(encoding="utf-8") for path in paths]
    if tail in _citations(documents):
        return []
    return [
        Finding(
            CONVENTIONS_DIR,
            0,
            RULE_UNREACHED,
            f"Ruling {tail} is the tail of docs/tasks/rulings-index.md and no document "
            f"under {CONVENTIONS_DIR}/ cites it. A ruling is not LANDED until a "
            f"convention document carries it, and the reviewer who mints it owns that "
            f"edit (Ruling 245). Quote it, do not paraphrase it (Ruling 195) — and "
            f"regenerating the index cannot satisfy this, only an edit can. "
            f"⭐ THE SPELLINGS THAT CLEAR THIS (Ruling 280): {spellings(tail)}.",
        )
    ]


def reach_notice(root: Path) -> list[str]:
    """Return the reach census over the tail window, printed whether anything failed.

    ⛔ The unreached members are enumerated rather than counted: Ruling 245's
    finding was invisible for twenty-five rounds precisely because nobody had
    printed the population, and `0 reached` is `0 = 0` until it says out of how
    many (Ruling 48, Ruling 128).
    """
    tail = _tail(root)
    if tail is None:
        return [
            f"rulings reach: no ruling records in this checkout, so no ruling is owed a "
            f"{CONVENTIONS_DIR}/ citation. This is not a failure — the floor runs over "
            f"trees that are not this repository."
        ]
    paths = _conventions(root)
    documents = [path.read_text(encoding="utf-8") for path in paths]
    citations = _citations(documents)
    window = range(max(1, tail - REACH_WINDOW + 1), tail + 1)
    unreached = [number for number in window if number not in citations]
    reached = len(window) - len(unreached)
    members = ", ".join(str(number) for number in unreached) or "none"
    return [
        f"rulings reach: tail {tail} is "
        f"{'CITED' if tail not in unreached else 'UNREACHED'} in {CONVENTIONS_DIR}/; "
        f"over the {len(window)} newest rulings ({window.start}–{tail}) reached "
        f"{reached}, unreached {len(unreached)} — an UPPER BOUND on the hole "
        f"(Rulings 280, 281), because reach is read from the declared citation "
        f"spellings outside code spans and fences, and the three declared gaps "
        f"(emphasis inside the number, a citation wrapped across a line break, a "
        f"word between the plural and its members) read UNREACHED. Read from "
        f"{len(paths)} convention document(s). Unreached: {members}."
    ]


#: ⭐ Re-exported so a caller needs one import, and named so the mirror test can
#: assert the module's surface rather than its internals.
__all__ = [
    "CONVENTIONS_DIR",
    "MAX_RANGE_SPAN",
    "REACH_WINDOW",
    "RULE_UNREACHED",
    "check_rulings_reach",
    "cited_numbers",
    "reach_notice",
    "spellings",
]
