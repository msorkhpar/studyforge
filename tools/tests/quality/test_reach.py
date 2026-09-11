"""Mirror of `tools/quality/reach.py` (R12).

⛔ **Ruling 123 and Ruling 140: an instrument is validated by PLANTING, and the
plant is adversarial to the SEARCH TERM rather than to the subject.** ⭐ So the
three readings this module owes are written as three groups of tests:

* **live** — the real tree, where the tail is cited and the check is green;
* **planted** — a synthetic tree where the tail's citation is replaced by a
  NEAR MISS of the search term (a bare number, a lowercase spelling, a longer
  number with the tail as a prefix), each of which must still read UNREACHED;
* **impossible** — a population that cannot be satisfied, and the two EMPTIES
  kept apart, so the check demonstrably can fail (Ruling 128, Ruling 191).

## ⛔ `W133`'s group: the SPELLINGS, and the MENTION exclusion that makes them safe

⛔ **Ruling 280: a CHECK may not have a pass condition that only one undeclared
spelling satisfies.** ⭐ So the plural, comma-list, `+`-join and range spellings
are asserted in BOTH directions, and the negative control is the one the row
lives on: ⛔ **the same citation inside backticks must leave the ruling
UNREACHED, or the repair hands the gate a line that can never fail again** —
Ruling 280's own text quotes these forms as examples, so a span-blind widening
would be satisfied by the description of the defect.
"""

from __future__ import annotations

from pathlib import Path

import tools.quality.reach as reach
from tests.support import assert_package_contract, repository_root
from tools.quality.reach import (
    CONVENTIONS_DIR,
    MAX_RANGE_SPAN,
    REACH_WINDOW,
    RULE_UNREACHED,
    check_rulings_reach,
    cited_numbers,
    reach_notice,
    spellings,
)

#: ⭐ The smallest tree that is recognisably this repository to the instrument:
#: one ruling record whose heading writes a number, and one convention document.
#: ⛔ Built rather than fixtured, so the plants below change exactly one byte
#: group and nothing else can drift underneath them.
#:
#: ⚠️ `round14` is load-bearing: `derive.SERIES_FIRST_ROUND` is 14 and a record
#: naming an earlier round is correctly not part of the numbered series, so a
#: fixture named `round1` would build a tree the instrument cannot see — and
#: every plant below would then pass for the wrong reason.
RECORD_NAME = "CTO-2026-01-01-round14.md"


def _tree(tmp_path: Path, *, numbers: tuple[int, ...], convention: str | None) -> Path:
    """A root with ruling records for `numbers` and one convention document."""
    records = tmp_path / "docs" / "tasks" / "handoffs"
    records.mkdir(parents=True)
    headings = "\n\n".join(f"## Ruling {number} — a heading that writes it" for number in numbers)
    (records / RECORD_NAME).write_text(f"# round 1\n\n{headings}\n", encoding="utf-8")
    if convention is not None:
        conventions = tmp_path / CONVENTIONS_DIR
        conventions.mkdir(parents=True)
        (conventions / "rubric.md").write_text(convention, encoding="utf-8")
    return tmp_path


def test_states_its_contract():
    assert_package_contract(reach, "tools.quality.reach")


# ── live ────────────────────────────────────────────────────────────────────


def test_the_real_tree_is_green_and_the_notice_prints_its_population():
    # ⛔ The LIVE reading. A green check alone is not evidence (Ruling 124): the
    # notice has to name the tail, the window and the denominator, or `0
    # unreached` is `0 = 0`.
    root = repository_root()
    assert check_rulings_reach(root) == []
    (line,) = reach_notice(root)
    assert line.startswith("rulings reach: tail ")
    assert "CITED" in line
    assert "convention document(s)" in line
    assert "Unreached:" in line


def test_a_citation_in_running_prose_counts_not_only_a_heading(tmp_path):
    root = _tree(tmp_path, numbers=(1, 2), convention="see Ruling 2 for the clause\n")
    assert check_rulings_reach(root) == []


def test_the_window_is_the_cliffs_own_width():
    # ⛔ A constant with no unit is a defect (Ruling 277). 25 is the population
    # Ruling 245 measured — rulings 217–241 — and the notice's window is that.
    assert REACH_WINDOW == 25


# ── planted, adversarial to the SEARCH TERM ─────────────────────────────────


def test_the_tail_uncited_is_a_finding_naming_the_ruling(tmp_path):
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 2 landed here\n")
    (finding,) = check_rulings_reach(root)
    assert finding.rule == RULE_UNREACHED
    assert finding.path == CONVENTIONS_DIR
    assert "Ruling 3" in finding.message
    # ⛔ And the remedy may not be a regeneration: that is the confusion with
    # `check_rulings_index` this check exists to separate.
    assert "only an edit can" in finding.message


def test_a_bare_number_is_a_mention_and_never_a_reach(tmp_path):
    # ⛔ `CTO-56`'s dispatcher measured a bare `grep 231` matching a LINE COUNT.
    # This is that plant: the number is present, the citation is not.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="the module is 3 lines long\n")
    assert [finding.rule for finding in check_rulings_reach(root)] == [RULE_UNREACHED]


def test_a_longer_number_with_the_tail_as_a_prefix_is_not_a_reach(tmp_path):
    # ⛔ The right bound. Without `(?!\d)`, `Ruling 27` would be satisfied by
    # every `Ruling 278` in the tree — a reach the tree does not have.
    root = _tree(tmp_path, numbers=tuple(range(1, 28)), convention="Ruling 278 is elsewhere\n")
    assert [finding.rule for finding in check_rulings_reach(root)] == [RULE_UNREACHED]


def test_a_lowercase_spelling_is_not_the_index_population_spelling(tmp_path):
    # ⚠️ The predicate is the literal spelling the index's own population is
    # derived from. A convention that writes `ruling 3` has not cited Ruling 3
    # in the form every brief resolves, so it does not count.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="ruling 3 says so\n")
    assert [finding.rule for finding in check_rulings_reach(root)] == [RULE_UNREACHED]


def test_landing_the_planted_ruling_turns_it_green(tmp_path):
    # ⭐ The other half of a plant: it must go GREEN again when the ruling lands,
    # or the instrument is stuck red and certifies nothing either way.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="the module is 3 lines long\n")
    assert check_rulings_reach(root)
    document = root / CONVENTIONS_DIR / "rubric.md"
    document.write_text(document.read_text(encoding="utf-8") + "\nRuling 3 landed\n", "utf-8")
    assert check_rulings_reach(root) == []


def test_the_notice_enumerates_the_unreached_members(tmp_path):
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 2 landed here\n")
    (line,) = reach_notice(root)
    assert "UNREACHED" in line
    assert "Unreached: 1, 3." in line
    assert "reached 1" in line


# ── impossible, and the two empties kept apart ──────────────────────────────


def test_a_tree_with_no_ruling_records_owes_nothing(tmp_path):
    # ⭐ The floor runs over a corpus, a consumer repository and an installed
    # tree. None of those owes a rulings index (Ruling 191's PASS reading).
    assert check_rulings_reach(tmp_path) == []
    (line,) = reach_notice(tmp_path)
    assert "no ruling records in this checkout" in line


def test_records_with_no_conventions_directory_is_REFUSED_not_passed(tmp_path):
    # ⛔ The IMPOSSIBLE reading, and it is why the two empties are separated:
    # without this arm, deleting `docs/conventions/` turns the check green.
    root = _tree(tmp_path, numbers=(1, 2), convention=None)
    (finding,) = check_rulings_reach(root)
    assert finding.rule == RULE_UNREACHED
    assert "Ruling 191" in finding.message


def test_a_number_outside_the_contiguous_series_is_not_the_tail(tmp_path):
    # ⚠️ The index's own population splits the contiguous series from the rest,
    # and a probe number written as a ruling (`9999`) is outside it. ⛔ If the
    # tail were `max()`, an impossible control in somebody's probe table would
    # become the thing every convention had to cite.
    root = _tree(tmp_path, numbers=(1, 2, 9999), convention="Ruling 2 landed here\n")
    assert check_rulings_reach(root) == []


# ── W133: the spellings the house style writes, both directions ──────────────


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
    # would turn this gate green for every tail forever — a pass condition no
    # reviewer verified. ⚠️ The cap is a MEMBER COUNT, counted inclusively, so
    # the boundary is asserted on both sides of itself.
    widest = MAX_RANGE_SPAN  # members, inclusive
    assert cited_numbers(f"Rulings 1-{widest}") == set(range(1, widest + 1))
    assert cited_numbers(f"Rulings 1-{widest + 1}") == {1, widest + 1}
    assert cited_numbers("Rulings 281-279") == {279, 281}


def test_the_range_cap_carries_its_unit():
    # ⛔ A constant with no unit is a defect (Ruling 277). The unit is RULINGS,
    # and the figure is the notice window because a range that covers the whole
    # window in one line is the hole, not the repair.
    assert MAX_RANGE_SPAN == REACH_WINDOW


# ── W133: the MENTION exclusion, which is the repair ────────────────────────


def test_a_BACKTICKED_citation_is_a_MENTION_and_never_a_reach():
    # ⛔ **THE READING THIS ROW LIVES OR DIES ON.** MEASURED at 428223c: the
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


def test_the_same_text_backticked_and_bare_is_the_both_directions_plant(tmp_path):
    # ⭐ The row's negative control and its positive half in one reading: a
    # backticked range leaves every member unreached, and the SAME text
    # unbackticked reaches them all. ⛔ A widening that passes only the positive
    # half ships the trap.
    numbers = tuple(range(1, 6))
    root = _tree(tmp_path, numbers=numbers, convention="see `Rulings 1-5` for the forms\n")
    (finding,) = check_rulings_reach(root)
    assert finding.rule == RULE_UNREACHED
    (line,) = reach_notice(root)
    assert "Unreached: 1, 2, 3, 4, 5." in line

    document = root / CONVENTIONS_DIR / "rubric.md"
    document.write_text("see Rulings 1-5 for the forms\n", encoding="utf-8")
    assert check_rulings_reach(root) == []
    (line,) = reach_notice(root)
    assert "Unreached: none." in line
    assert "reached 5" in line


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


# ── W133: the IMPOSSIBLE controls — spellings that must NOT match ───────────


def test_a_lowercase_plural_is_not_the_population_spelling():
    assert cited_numbers("rulings 279, 280 and 281 say so") == set()
    assert cited_numbers("RULINGS 279-281") == set()


def test_a_bare_number_range_with_no_citation_word_is_not_a_reach():
    # ⛔ `CTO-56`'s dispatcher measured a bare `grep 231` matching a LINE COUNT.
    # The widened predicate must not reopen that: a span of digits is not a
    # citation, whatever punctuation sits between them.
    assert cited_numbers("279-281, and 277, 279 besides") == set()
    assert cited_numbers("the module is 296 lines long") == set()


def test_a_five_digit_number_is_outside_the_population(tmp_path):
    # ⚠️ The widest ruling number this project can have is four digits, and the
    # `9999` probe is the impossible control the index itself carries.
    assert cited_numbers("Ruling 12345") == set()
    assert cited_numbers("Rulings 12345, 12346") == set()


# ── W133: the DECLARED GAPS, asserted so the closed claim stays closed ──────


def test_the_declared_gaps_read_UNREACHED_and_that_is_the_claim():
    # ⛔ Ruling 258: a declared-gaps list is a CLOSED CLAIM, so each of the three
    # is a test rather than a sentence. ⭐ Ruling 185 is why they are gaps and
    # not features: Ruling 280's words are "the forms the house style writes",
    # and widening past them is the taker's, not the ruling's.
    assert cited_numbers("Rulings **15**, **62** and **68** each returned") == set()
    assert cited_numbers("Rulings 106 and\n174 forbid editing") == {106}
    assert cited_numbers("`Rulings minted: 198-202`") == set()
    assert cited_numbers("Rulings minted: 198-202") == set()


# ── W133: Ruling 280's second arm and Ruling 281's audience clause ──────────


def test_the_finding_NAMES_the_spellings_that_would_clear_it(tmp_path):
    # ⛔ Ruling 280's second arm. A check whose pass condition is satisfiable by
    # one undeclared spelling puts the condition in the reader; this puts it in
    # the message the office that trips the gate actually reads.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 2 landed here\n")
    (finding,) = check_rulings_reach(root)
    for form in ("`Ruling 3`", "`Rulings 2, 3`", "`Rulings 1-3`", "`Rulings 1–3`"):
        assert form in finding.message, f"the finding does not name {form}"
    assert "code span" in finding.message
    assert "Ruling 280" in finding.message


def test_the_spellings_are_written_for_the_ruling_that_failed():
    # ⚠️ A message naming `Ruling 296` when the tail is `3` would be worse than
    # none: the reader would copy the wrong number into their convention.
    assert "`Ruling 296`" in spellings(296)
    assert "`Rulings 295, 296`" in spellings(296)
    assert "`Ruling 296`" not in spellings(3)


def test_the_notice_says_its_figure_is_an_UPPER_BOUND(tmp_path):
    # ⛔ Ruling 281's audience clause, and Ruling 280's first arm: a NOTICE may
    # under-count, and then it reports an UPPER BOUND with the spelling named —
    # beside the number, not in a module docstring.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 2 landed here\n")
    (line,) = reach_notice(root)
    assert "UPPER BOUND" in line
    assert "code spans and fences" in line
    assert "Ruling" in line and "281" in line
