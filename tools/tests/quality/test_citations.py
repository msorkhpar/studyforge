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

## ⛔ `W145`'s group: the BLOCK, and the BOUNDARIES that keep it from inventing

⛔ **A citation can be UNMADE by a re-wrap with no word changing**, so the unit
is a block and not a line. ⭐ **Which makes the REFUSALS the load-bearing half:
every boundary the module declares is asserted with a probe number drawn AFRESH
per run** (`9999` is disqualified — records quote it), because a join that
crossed a paragraph, a heading, a table row, a list marker or a fence edge would
invent citations no renderer shows. ⚠️ And the live control is a POPULATION
rather than one line number: a specific line pair is one re-wrap away from
moving, and the property — *some pair of prose lines in `docs/conventions/`
carries a citation neither line carries alone* — is not.
"""

from __future__ import annotations

import random
import re
from functools import lru_cache
from pathlib import Path

import tools.quality.citations as citations
from tests.support import assert_package_contract, repository_root
from tools.quality.citations import MAX_RANGE_SPAN, cited_numbers, spellings
from tools.quality.pointers import prose_lines
from tools.quality.reach import CONVENTIONS_DIR


@lru_cache(maxsize=1)
def _four_digit_numbers() -> frozenset[str]:
    """Every four-digit number written in any markdown file of this tree."""
    root = repository_root()
    written: set[str] = set()
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        written.update(re.findall(r"(?<!\d)\d{4}(?!\d)", text))
    return frozenset(written)


def _fresh_probe() -> int:
    """A four-digit number NO markdown file in this tree writes, drawn per run.

    ⛔ `9999` is DISQUALIFIED and that is measured rather than preference: two
    ruling records quote it, so it has stopped being impossible. ⚠️ **And the
    freshness this needs is not `test_reach._fresh_probe`'s.** That one asks
    whether a number is outside the DERIVED ruling population; a control here
    has to be a number a reviewer's grep finds ONLY in the control, so it is
    drawn against the TEXT of every markdown file instead. ⭐ Two predicates,
    two populations — which is this module's own subject one level up.
    """
    taken = _four_digit_numbers()
    for candidate in random.sample(range(1000, 10000), 200):
        if str(candidate) not in taken:
            return candidate
    raise AssertionError("200 draws found no unwritten number; the population cannot be dense")


def _conventions() -> list[Path]:
    return sorted((repository_root() / CONVENTIONS_DIR).rglob("*.md"))


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
    # three backticked citations on `docs/conventions/review-rubric.md` are inside Ruling
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
    strict: set[int] = set()
    blind: set[int] = set()
    for path in _conventions():
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
    # ⛔ Ruling 258: a declared-gaps list is a CLOSED CLAIM, so each gap
    # this module declares is a test rather than a sentence. ⭐ Ruling 185 is why
    # they are gaps and not features: Ruling 280's words are "the forms the house
    # style writes", and widening past them is the taker's, not the ruling's.
    # ⚠️ Another stood here — `Rulings 106 and\n174` read `{106}` — until `W145`
    # CLOSED it. The assertion MOVED to the group below rather than being
    # deleted, because a gap that is closed and a gap that is forgotten leave
    # the same hole in the list.
    assert cited_numbers("Rulings **15**, **62** and **68** each returned") == set()
    assert cited_numbers("`Rulings minted: 198-202`") == set()
    assert cited_numbers("Rulings minted: 198-202") == set()


# ── W145: a citation WRAPPED across a line break, and where it STOPS ────────


def test_a_citation_WRAPPED_across_a_line_break_is_still_a_citation():
    # ⛔ **The reading this row was minted over.** `review-rubric.md` re-wrapped
    # a paragraph so `166` began the next line, and the citation was UNMADE with
    # no word changing — no word added, none removed, and a diff showing a
    # reflowed paragraph. ⭐ The first of these two is the live loss, quoted from
    # `docs/conventions/review-rubric.md`; the second is the gap `citations.py` used to
    # declare, quoted from `docs/conventions/board.md`. MEASURED at `fc56011`.
    assert cited_numbers("closed and therefore takes **Ruling\n166**'s disposition") == {166}
    assert cited_numbers("Rulings 106 and\n174 forbid editing") == {106, 174}


def test_the_number_below_the_break_may_be_INDENTED():
    # ⚠️ The member that separates the shape's population from a sweep anchored
    # on a leading digit (`W145`'s clause 6, where three offices read 7, 6 and 1
    # and all three were right): `docs/conventions/review-rubric.md` continues with three
    # spaces. ⛔ `reach` is indifferent to indentation, so this grammar is too.
    assert cited_numbers("⚠️ Ruling\n   70 asks for same-size mutations") == {70}


def test_a_wrap_INSIDE_a_blockquote_is_read_and_one_ACROSS_its_edge_is_not():
    # ⭐ `docs/conventions/board.md` writes a wrapped citation inside a `>` block, so the
    # marker is split off before the join — a rule that refused every quoted
    # line would have left the closed gap still open in one shape and called it
    # closed. ⛔ But quoted text and plain text are two markdown blocks, and a
    # citation crosses between them in neither direction.
    assert cited_numbers("> so Ruling\n> 189 binds it") == {189}
    assert cited_numbers("> so Ruling\n189 binds it") == set()
    assert cited_numbers("so Ruling\n> 189 binds it") == set()


def test_a_number_across_a_BLOCK_BOUNDARY_is_NOT_a_landing():
    # ⛔ **THE IMPOSSIBLE CONTROL, and it is the half that makes the widening
    # safe** (R12, Ruling 65: a widened predicate that cannot fail is worse than
    # a narrow one that can). ⚠️ A line count, an ordinal or a year below a
    # boundary must not become a citation — so the probe is drawn AFRESH per run
    # and every declared boundary is asserted, not just the paragraph one.
    probe = _fresh_probe()
    assert str(probe) not in _four_digit_numbers(), "the probe is not fresh"
    assert cited_numbers(f"is a Ruling\n\n{probe} rounds later") == set()
    assert cited_numbers(f"is a Ruling\n# {probe} things") == set()
    assert cited_numbers(f"| what | Ruling\n| {probe} | a mention |") == set()
    assert cited_numbers(f"is a Ruling\n- {probe} things") == set()
    assert cited_numbers(f"is a Ruling\n1. {probe} things") == set()
    assert cited_numbers(f"is a Ruling\n---\n{probe} things") == set()
    assert cited_numbers(f"is a Ruling\n```text\nx\n```\n{probe} rounds") == set()
    assert cited_numbers(f"is a Ruling\n{probe}0 rounds") == set()


def test_an_ORDERED_ITEM_at_ANY_number_is_a_boundary_and_never_a_citation():
    # ⛔ **CTO round 65's required change, and it is the direction Ruling 65 ranks
    # WORST: this INVENTED a citation.** ⚠️ The breaker was `1[.)]` — CommonMark's
    # *only a list starting at one interrupts a paragraph* — which is true of a
    # PARAGRAPH and false between two adjacent list ITEMS, where every number
    # starts one. ⭐ 0 live instances, so it was LATENT; refused anyway, and
    # MEASURED to cost nothing: over every markdown file of this tree the
    # widened breaker loses nothing and gains nothing.
    probe = _fresh_probe()
    assert cited_numbers(f"1. This is a Ruling\n2. {probe} things") == set()
    assert cited_numbers(f"is a Ruling\n2. {probe} things") == set()
    assert cited_numbers("is a Ruling\n10.") == set()


def test_a_BRACKETED_ordinal_is_ADMITTED_because_the_house_wraps_a_paren():
    # ⛔ **The other edge of the same boundary, declared rather than left silent.**
    # ⭐ MEASURED: this tree wraps a parenthesised citation — `(Ruling` with `279)`
    # beneath it — in `docs/tasks/handoffs/PO-2026-09-10-round25.md` and
    # `docs/tasks/handoffs/SESSION-2026-09-11-coordinator-2.md`, and BOTH are real citations a
    # `\d{1,4}[.)]` breaker would have thrown away. ⚠️ So `N)` is NOT a boundary,
    # and this is what stops the next editor widening it back for symmetry.
    assert cited_numbers("`PO-24/1`'s own control (Ruling\n  95) already showed this") == {95}
    assert cited_numbers("a GATE only at its own tip (Ruling\n279) — that gate read 0") == {279}
    assert cited_numbers("is a Ruling\n3) a thing") == {3}


def test_an_UNCLOSED_code_span_ends_the_block_rather_than_carrying_a_MENTION():
    # ⛔ `strip_code_spans` is LINE-scoped, so a span opened on one line and
    # closed on the next survives it — and a join across that pair would carry a
    # MENTION into the reading, which is the ONE way this change could have
    # weakened the exclusion `W133` lived on. ⭐ Refused rather than declared,
    # and MEASURED at `fc56011`: all 14 live wrapped pairs in the conventions
    # leave both their lines balanced, so the refusal costs nothing real.
    probe = _fresh_probe()
    assert cited_numbers(f"an example, `Ruling\n{probe}` in a span") == set()
    # ⭐ And the other direction, so the rule is a BOUNDARY and not a refusal of
    # every line that ever held a span: a span that CLOSES on its own line
    # leaves the join intact.
    assert cited_numbers("`a span` and Ruling\n296 after it") == {296}


def test_the_LIVE_conventions_carry_a_wrapped_citation_and_never_LOSE_one():
    # ⛔ **The live control, in BOTH directions** (Ruling 191): the instrument
    # must be seen to FIND and to REFUSE. ⭐ FIND — some pair of prose lines in
    # `docs/conventions/` yields a citation neither line yields alone, which is
    # the population `W145` was minted over (14 pairs at `fc56011`). ⚠️ REFUSE —
    # the block reading never LOSES a member the line reading had, so the gain
    # cannot be a repair that dropped something quietly (measured: gained
    # `{166}`, lost nothing). ⛔ If this tree ever stops wrapping a citation,
    # re-derive this rather than relaxing it: it is the only LIVE evidence.
    wrapped = 0
    for path in _conventions():
        text = path.read_text(encoding="utf-8")
        lines = prose_lines(text)
        per_line: set[int] = set()
        for _, line in lines:
            per_line |= cited_numbers(line)
        for (upper, above), (lower, below) in zip(lines, lines[1:], strict=False):
            if lower != upper + 1:
                continue
            if cited_numbers(f"{above}\n{below}") > cited_numbers(above) | cited_numbers(below):
                wrapped += 1
        assert per_line <= cited_numbers(text), f"{path.name} LOST a citation to the block"
    assert wrapped, "no document under docs/conventions/ wraps a citation any more"


# ── Ruling 280's second arm: the spellings a finding NAMES ──────────────────


def test_the_spellings_are_written_for_the_ruling_that_failed():
    # ⚠️ A message naming `Ruling 296` when the tail is `3` would be worse than
    # none: the reader would copy the wrong number into their convention.
    assert "`Ruling 296`" in spellings(296)
    assert "`Rulings 295, 296`" in spellings(296)
    assert "`Ruling 296`" not in spellings(3)
