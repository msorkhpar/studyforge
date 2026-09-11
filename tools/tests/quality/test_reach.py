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

## ⛔ `W139`'s group: the reading BELOW the window, and what makes it a SECOND one

⛔ **Ruling 304: the window SLIDES, so `unreached 0` is satisfiable by MINTING.**
⭐ The remedy is a second census, and its two ruled properties are asserted here
rather than described: ⛔ **the members below the window are NAMED, not counted**
— a bare scalar is the form that produced the defect — and ⛔ **the two figures
are NEVER SUMMED.** ⚠️ The second is asserted as INDEPENDENCE in both
directions: a landing below the window moves the second line and leaves the
first byte-identical, and a landing inside it does the reverse.

## ⛔ The GRAMMAR's readings are NOT here

⭐ `W139` split this module at the seam `W133`'s taker named, and the spelling
tests went with the code: `tools/tests/quality/test_citations.py` owns them.
⚠️ **The one assertion that spans the seam stays here** — `MAX_RANGE_SPAN ==
REACH_WINDOW` — because the equality cannot be an assignment (the seam runs one
way) and an unasserted equality is a silent divergence waiting to happen.
"""

from __future__ import annotations

import random
from pathlib import Path

import tools.quality.reach as reach
from tests.support import assert_package_contract, repository_root
from tools.quality.citations import MAX_RANGE_SPAN, cited_numbers
from tools.quality.reach import (
    _GAPS,
    CONVENTIONS_DIR,
    REACH_WINDOW,
    RULE_UNREACHED,
    check_rulings_reach,
    reach_notice,
)
from tools.quality.rulings.derive import records, sites

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

#: ⭐ A series one wider than the window, so there IS a below-window population
#: and it is small enough to name in an assertion: window 6–30, below 1–5.
SPANNING = tuple(range(1, REACH_WINDOW + 6))


def _tree(tmp_path: Path, *, numbers: tuple[int, ...], convention: str | None) -> Path:
    """A root with ruling records for `numbers` and one convention document."""
    records_dir = tmp_path / "docs" / "tasks" / "handoffs"
    records_dir.mkdir(parents=True)
    headings = "\n\n".join(f"## Ruling {number} — a heading that writes it" for number in numbers)
    (records_dir / RECORD_NAME).write_text(f"# round 1\n\n{headings}\n", encoding="utf-8")
    if convention is not None:
        conventions = tmp_path / CONVENTIONS_DIR
        conventions.mkdir(parents=True)
        (conventions / "rubric.md").write_text(convention, encoding="utf-8")
    return tmp_path


def _land(root: Path, clause: str) -> None:
    """Append one landing to the tree's convention document."""
    document = root / CONVENTIONS_DIR / "rubric.md"
    document.write_text(document.read_text(encoding="utf-8") + clause, encoding="utf-8")


def _below_members(line: str) -> list[int]:
    """The ids the below-window line NAMES, read back out of the line itself."""
    named = line.rsplit("Still uncited below the window: ", 1)[1].rstrip(".")
    return [] if named == "none" else [int(number) for number in named.split(", ")]


def _fresh_probe(root: Path) -> int:
    """A four-digit number this tree mentions NOWHERE as a ruling, drawn afresh per run.

    ⛔ `9999` is DISQUALIFIED as a probe and that is measured, not preference:
    two ruling records quote it, so it has stopped being impossible (check 3's
    own clause, `board.md`). ⭐ So the probe is drawn each run and verified
    against the population it must be outside of — every number a record writes
    and every number a convention cites.
    """
    taken = {site.number for record in records(root) for site in sites(record)}
    for path in (root / CONVENTIONS_DIR).rglob("*.md"):
        taken |= cited_numbers(path.read_text(encoding="utf-8"))
    for candidate in random.sample(range(1000, 10000), 200):
        if candidate not in taken:
            return candidate
    raise AssertionError("200 draws found no unmentioned number; the population cannot be dense")


def test_states_its_contract():
    assert_package_contract(reach, "tools.quality.reach")


# ── live ────────────────────────────────────────────────────────────────────


def test_the_real_tree_is_green_and_the_notice_prints_its_population():
    # ⛔ The LIVE reading. A green check alone is not evidence (Ruling 124): the
    # notice has to name the tail, the window and the denominator, or `0
    # unreached` is `0 = 0`.
    root = repository_root()
    assert check_rulings_reach(root) == []
    window, below = reach_notice(root)
    assert window.startswith("rulings reach: tail ")
    assert "CITED" in window
    assert "convention document(s)" in window
    assert "Unreached:" in window
    assert below.startswith("rulings reach below the window: ")
    assert "Still uncited below the window:" in below


def test_a_citation_in_running_prose_counts_not_only_a_heading(tmp_path):
    root = _tree(tmp_path, numbers=(1, 2), convention="see Ruling 2 for the clause\n")
    assert check_rulings_reach(root) == []


def test_the_window_is_the_cliffs_own_width():
    # ⛔ A constant with no unit is a defect (Ruling 277). 25 is the population
    # Ruling 245 measured — rulings 217–241 — and the notice's window is that.
    assert REACH_WINDOW == 25


def test_the_range_cap_equals_the_window_ACROSS_the_seam():
    # ⛔ `W139` split the grammar out, and the seam runs ONE WAY: `citations`
    # imports nothing back, so `MAX_RANGE_SPAN = REACH_WINDOW` cannot be an
    # assignment. ⭐ This is the assertion that replaces it — a range covering
    # the whole notice window in one line is the hole, not the repair
    # (Ruling 65), and the two figures may not drift apart silently.
    assert MAX_RANGE_SPAN == REACH_WINDOW


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
    _land(root, "\nRuling 3 landed\n")
    assert check_rulings_reach(root) == []


def test_the_notice_enumerates_the_unreached_members(tmp_path):
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 2 landed here\n")
    window, _ = reach_notice(root)
    assert "UNREACHED" in window
    assert "Unreached: 1, 3." in window
    assert "reached 1" in window


def test_the_same_text_backticked_and_bare_is_the_both_directions_plant(tmp_path):
    # ⭐ The grammar's negative control and its positive half, read through THIS
    # module's answer: a backticked range leaves every member unreached, and the
    # SAME text unbackticked reaches them all. ⛔ A widening that passes only the
    # positive half ships the trap.
    numbers = tuple(range(1, 6))
    root = _tree(tmp_path, numbers=numbers, convention="see `Rulings 1-5` for the forms\n")
    (finding,) = check_rulings_reach(root)
    assert finding.rule == RULE_UNREACHED
    window, _ = reach_notice(root)
    assert "Unreached: 1, 2, 3, 4, 5." in window

    document = root / CONVENTIONS_DIR / "rubric.md"
    document.write_text("see Rulings 1-5 for the forms\n", encoding="utf-8")
    assert check_rulings_reach(root) == []
    window, _ = reach_notice(root)
    assert "Unreached: none." in window
    assert "reached 5" in window


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


# ── W139: the census BELOW the window (Ruling 304) ──────────────────────────


def test_the_notice_NAMES_the_members_still_uncited_below_the_window(tmp_path):
    # ⛔ The defect in one reading: the window can say `unreached 0` while the
    # tree carries uncited rulings underneath it. ⭐ NAMED, not counted — a bare
    # scalar is the form that produced this (the row's clause 1).
    root = _tree(tmp_path, numbers=SPANNING, convention="Ruling 30 landed\nRuling 2 landed\n")
    window, below = reach_notice(root)
    assert "over the 25 newest rulings (6–30)" in window
    assert "4 of the 5 rulings below 6 are still uncited" in below
    assert _below_members(below) == [1, 3, 4, 5]


def test_a_landing_BELOW_the_window_moves_the_second_line_and_not_the_first(tmp_path):
    # ⛔ **THE READING THIS ROW LIVES ON, and it is the both-directions plant.**
    # ⭐ The two figures answer different questions and are NEVER SUMMED, so each
    # must be seen to move alone — asserted as byte-identity of the line that
    # should not have moved, which no summed scalar could survive.
    root = _tree(tmp_path, numbers=SPANNING, convention="Ruling 30 landed\n")
    window_before, below_before = reach_notice(root)
    assert _below_members(below_before) == [1, 2, 3, 4, 5]

    _land(root, "Ruling 3 landed\n")  # below the window
    window_after, below_after = reach_notice(root)
    assert window_after == window_before, "a landing below the window moved the window's line"
    assert _below_members(below_after) == [1, 2, 4, 5]

    _land(root, "Ruling 20 landed\n")  # inside the window
    window_last, below_last = reach_notice(root)
    assert below_last == below_after, "a landing inside the window moved the below-window line"
    assert window_last != window_after


def test_the_two_FIGURES_are_never_summed_into_one_number(tmp_path):
    # ⛔ The row's clause 2. A single merged scalar would make a paying minter
    # and a growing backlog indistinguishable, so the sum must appear as the
    # reported figure of neither line.
    root = _tree(tmp_path, numbers=SPANNING, convention="Ruling 30 landed\n")
    window, below = reach_notice(root)
    inside, underneath = 24, 5  # 6–29 uncited inside the window; 1–5 below it
    assert f"unreached {inside} IN THIS WINDOW ALONE" in window
    assert f"{underneath} of the {underneath} rulings below 6" in below
    assert f"unreached {inside + underneath}" not in window
    assert f"{inside + underneath} of the" not in below


def test_a_series_that_FITS_the_window_says_so_rather_than_printing_0_of_0(tmp_path):
    # ⭐ Ruling 191's shape, third empty: an empty below-window population
    # returns the PASS READING rather than a figure with no denominator.
    root = _tree(tmp_path, numbers=(1, 2, 3), convention="Ruling 3 landed\n")
    _, below = reach_notice(root)
    assert "the 25-newest window covers the whole derived series (3 ruling(s))" in below
    assert _below_members(below) == []


def test_a_number_no_record_MINTED_can_never_enter_the_below_window_set(tmp_path):
    # ⛔ The IMPOSSIBLE control, with the probe drawn FRESH this run: a number
    # outside the derived series must read empty even when a convention cites it
    # in the house spelling, because the population is the series and not the
    # citations.
    probe = _fresh_probe(repository_root())
    root = _tree(
        tmp_path,
        numbers=SPANNING,
        convention=f"Ruling 30 landed\nRuling {probe} is not a ruling of this series\n",
    )
    _, below = reach_notice(root)
    assert probe not in _below_members(below)
    assert _below_members(below) == [1, 2, 3, 4, 5]


def test_the_LIVE_below_window_set_refuses_a_freshly_drawn_probe():
    # ⭐ The same impossible control against the real tree, where the population
    # is 300-odd rulings rather than five — so the refusal is measured against
    # the set this notice actually prints.
    root = repository_root()
    probe = _fresh_probe(root)
    _, below = reach_notice(root)
    assert probe not in _below_members(below)


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


def test_BOTH_notice_lines_say_their_figure_is_an_UPPER_BOUND(tmp_path):
    # ⛔ Ruling 281's audience clause, and Ruling 280's first arm: a NOTICE may
    # under-count, and then it reports an UPPER BOUND with the spelling named —
    # beside the number, not in a module docstring. ⚠️ BOTH lines, because the
    # second reads the same under-reading predicate as the first.
    root = _tree(tmp_path, numbers=SPANNING, convention="Ruling 30 landed\n")
    for line in reach_notice(root):
        assert "UPPER BOUND" in line
        assert "declared gaps" in line
    window, _ = reach_notice(root)
    assert "code spans and fences" in window
    assert "Ruling" in window and "281" in window


def test_the_notice_COUNTS_the_declared_gaps_it_NAMES(tmp_path):
    # ⛔ `W145`, and it is this module's own defect family arriving inside it.
    # BOTH lines wrote the word "three" beside `_GAPS`, so CLOSING a gap would
    # have left the instrument mis-stating its own declaration in the same
    # breath as the figure that declaration qualifies. ⭐ The numeral is DERIVED
    # from the list now, and this is what keeps it derived: a gap added or
    # closed moves the count with it or fails here.
    root = _tree(tmp_path, numbers=SPANNING, convention="Ruling 30 landed\n")
    for line in reach_notice(root):
        assert f"{len(_GAPS)} declared gaps" in line
        for gap in _GAPS:
            assert gap in line, f"the notice counts {len(_GAPS)} gaps and does not name {gap}"
    # ⚠️ And the closed one is GONE from both, because a declaration that still
    # names a gap the grammar reads is the same defect pointing the other way.
    assert "wrapped across a line break" not in "\n".join(reach_notice(root))
