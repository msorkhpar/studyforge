"""Mirror of `tools/quality/citations.py` (R12).

⛔ **The GRAMMAR half of what was one module.** ⭐ `W139` split
`tools/quality/reach.py` at the seam `W133`'s taker named, and these readings
came with the code they are about: they assert what a SPELLING means, never
whether a ruling landed. ⚠️ The landing half stays in `test_reach.py`, and the
one assertion that spans the seam — `MAX_RANGE_SPAN == REACH_WINDOW` — stays
there too, because it is a claim about the seam rather than about the grammar.

## ⛔ `W133`'s group: the SPELLINGS, and the MENTION exclusion that makes them safe

⛔ **Ruling 280: a CHECK may not have a pass condition that only one undeclared
spelling satisfies.** ⭐ So the plural, comma-list, `+`-join and range spellings
are asserted in BOTH directions, and the negative control is the one that row
lived on: ⛔ **the same citation inside backticks must leave the ruling
UNREACHED, or the repair hands the gate a line that can never fail again** —
Ruling 280's own text quotes these forms as examples, so a span-blind widening
would be satisfied by the description of the defect.
"""

from __future__ import annotations

import tools.quality.citations as citations
from tests.support import assert_package_contract, repository_root
from tools.quality.citations import MAX_RANGE_SPAN, cited_numbers, spellings
from tools.quality.reach import CONVENTIONS_DIR


def test_states_its_contract():
    assert_package_contract(citations, "tools.quality.citations")


# ── the spellings the house style writes, both directions ───────────────────


def test_the_singular_spelling_reads_one_member_and_keeps_its_right_bound():
    # ⭐ The compatibility half: the repair must not move the reading the
    # instrument already had. `Ruling 279-281` read `279` and refused `281`
    # before W133 (MEASURED at 428223c), and it still does.
    assert cited_numbers("Ruling 279") == {279}
    assert cited_numbers("Ruling 279-281") == {279}
    assert 278 not in cited_numbers("Ruling 27")
    assert 27 not in cited_numbers("Ruling 278")


def test_a_plural_comma_list_reaches_every_member_it_names():
    # ⛔ `CTO-59/1`: `Rulings 277, 279` satisfied NEITHER member before W133.
    assert cited_numbers("Rulings 277, 279") == {277, 279}
    assert cited_numbers("⛔ **It defeats Rulings 70, 76, 83 and 123 at once**") == {
        70,
        76,
        83,
        123,
    }


def test_a_plus_join_is_a_list_this_project_actually_writes():
    # ⚠️ `review-rubric.md` heads a section `Rulings 177 + 180`. The row's own
    # printed population carries it as a live USE while its four-spelling list
    # does not name it — so it is read, and the discrepancy is a finding.
    assert cited_numbers("### ⛔ Rulings 177 + 180 — a MIGRATION is validated") == {177, 180}


def test_a_range_reaches_every_member_of_its_span_in_both_dashes():
    # ⛔ A range cites its members, not its endpoints: `Rulings 264–278` is
    # fifteen rulings. Hyphen-minus and EN DASH both, because the house writes
    # both — merge subjects write `Rulings 217-222`, prose writes the en dash.
    assert cited_numbers("Rulings 279-281") == {279, 280, 281}
    assert cited_numbers("Rulings 264–278") == set(range(264, 279))


def test_an_em_dash_is_a_sentence_dash_and_never_a_range():
    # ⚠️ This project writes `—` on nearly every line. Admitting it as a range
    # separator would read a citation out of every heading.
    assert cited_numbers("Ruling 296 — 299 lines of it") == {296}


def test_a_plural_word_is_required_for_a_MULTI_MEMBER_body():
    # ⛔ Ruling 65's narrowing, MEASURED at 428223c: all ten live plural
    # citation sites write `Rulings`, and `Ruling 290, 5 distinct ids` is a
    # sentence this project does write — a `Rulings?`-admitting list reads `5`
    # out of it as a citation of Ruling 5.
    assert cited_numbers("Ruling 290, 5 distinct ids under the unchanged tag") == {290}
    assert cited_numbers("Ruling 290 and 5 distinct ids") == {290}


def test_a_range_naming_more_than_the_cap_reads_only_its_endpoints():
    # ⛔ Ruling 65 again, from the other side: one line reading `Rulings 1-400`
    # would turn the reach gate green for every tail forever — a pass condition
    # no reviewer verified. ⚠️ The cap is a MEMBER COUNT, counted inclusively, so
    # the boundary is asserted on both sides of itself.
    widest = MAX_RANGE_SPAN  # members, inclusive
    assert cited_numbers(f"Rulings 1-{widest}") == set(range(1, widest + 1))
    assert cited_numbers(f"Rulings 1-{widest + 1}") == {1, widest + 1}
    assert cited_numbers("Rulings 281-279") == {279, 281}


# ── the MENTION exclusion, which is the repair ──────────────────────────────


def test_a_BACKTICKED_citation_is_a_MENTION_and_never_a_reach():
    # ⛔ **THE READING THIS GRAMMAR LIVES OR DIES ON.** MEASURED at 428223c: the
    # three backticked citations on `review-rubric.md:3989` are inside Ruling
    # 280's own text, and a span-blind widening reads 264–281 off that one line
    # — the ruling describing the defect satisfying the check that tests for it.
    assert cited_numbers("⛔ **`Rulings 264–278` all FAIL to match**") == set()
    assert cited_numbers("`Rulings 277, 279`, `Rulings 279-281`") == set()
    assert cited_numbers("`Ruling 296`") == set()


def test_a_FENCED_citation_is_quoted_material_and_never_a_reach():
    # ⚠️ `board.md` transcribes a measurement reading `"defeats Rulings 70, 76,
    # 83"` inside a ```text block. A transcript of this check firing is
    # evidence, not a landing (`pointers.prose_lines`' own sentence).
    fenced = "```text\nRulings 279-281 and Ruling 296\n```\n"
    assert cited_numbers(fenced) == set()
    assert cited_numbers("Ruling 296 landed\n" + fenced) == {296}


def test_the_live_tree_is_NOT_green_off_its_own_backticked_examples():
    # ⛔ The LIVE reading of the trap, and it is an assertion rather than a
    # comment. MEASURED at 428223c: stripping every backtick from the
    # conventions turns the code spans into prose, and the reach set GROWS —
    # by `272`–`281`, read off Ruling 280's own illustration. ⚠️ If this tree
    # ever stops writing a backticked citation, re-derive this reading rather
    # than relaxing it: it is the only live evidence the exclusion does work.
    root = repository_root()
    documents = sorted((root / CONVENTIONS_DIR).rglob("*.md"))
    strict: set[int] = set()
    blind: set[int] = set()
    for path in documents:
        text = path.read_text(encoding="utf-8")
        strict |= cited_numbers(text)
        blind |= cited_numbers(text.replace("`", ""))
    assert strict < blind, "no code span in docs/conventions/ hides a citation any more"


# ── the IMPOSSIBLE controls — spellings that must NOT match ─────────────────


def test_a_lowercase_plural_is_not_the_population_spelling():
    assert cited_numbers("rulings 279, 280 and 281 say so") == set()
    assert cited_numbers("RULINGS 279-281") == set()


def test_a_bare_number_range_with_no_citation_word_is_not_a_reach():
    # ⛔ `CTO-56`'s dispatcher measured a bare `grep 231` matching a LINE COUNT.
    # The widened predicate must not reopen that: a span of digits is not a
    # citation, whatever punctuation sits between them.
    assert cited_numbers("279-281, and 277, 279 besides") == set()
    assert cited_numbers("the module is 296 lines long") == set()


def test_a_five_digit_number_is_outside_the_population():
    # ⚠️ The widest ruling number this project can have is four digits, and an
    # impossible control in somebody's probe table is deliberately readable.
    assert cited_numbers("Ruling 12345") == set()
    assert cited_numbers("Rulings 12345, 12346") == set()


# ── the DECLARED GAPS, asserted so the closed claim stays closed ────────────


def test_the_declared_gaps_read_UNREACHED_and_that_is_the_claim():
    # ⛔ Ruling 258: a declared-gaps list is a CLOSED CLAIM, so each of the three
    # this module declares is a test rather than a sentence. ⭐ Ruling 185 is why
    # they are gaps and not features: Ruling 280's words are "the forms the house
    # style writes", and widening past them is the taker's, not the ruling's.
    assert cited_numbers("Rulings **15**, **62** and **68** each returned") == set()
    assert cited_numbers("Rulings 106 and\n174 forbid editing") == {106}
    assert cited_numbers("`Rulings minted: 198-202`") == set()
    assert cited_numbers("Rulings minted: 198-202") == set()


# ── Ruling 280's second arm: the spellings a finding NAMES ──────────────────


def test_the_spellings_are_written_for_the_ruling_that_failed():
    # ⚠️ A message naming `Ruling 296` when the tail is `3` would be worse than
    # none: the reader would copy the wrong number into their convention.
    assert "`Ruling 296`" in spellings(296)
    assert "`Rulings 295, 296`" in spellings(296)
    assert "`Ruling 296`" not in spellings(3)
