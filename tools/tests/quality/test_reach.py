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
"""

from __future__ import annotations

from pathlib import Path

import tools.quality.reach as reach
from tests.support import assert_package_contract, repository_root
from tools.quality.reach import (
    CONVENTIONS_DIR,
    REACH_WINDOW,
    RULE_UNREACHED,
    check_rulings_reach,
    reach_notice,
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
