"""Mirror of `tools/quality/rulings/__init__.py` (R12).

⛔ **A freshness check that cannot fail is the whole defect it exists to close**,
so the stale and absent readings are inhabited here — by PLANTING a changed
document under a temporary root, never by describing what would happen.
"""

from __future__ import annotations

from tests.support import assert_package_contract, repository_root
from tools.quality import CHECKS, NOTICES
from tools.quality.rulings import (
    REBUILD_COMMAND,
    RULE_STALE,
    check_rulings_index,
    rulings_notice,
)
from tools.quality.rulings.derive import INDEX_PATH, entries
from tools.quality.rulings.document import text
from tools.tests.quality.rulings.support import ROUND_14, tree


def build(root):
    """A temporary tree with one record and the index it derives, both on disk."""
    tree(root, r14=ROUND_14)
    target = root / INDEX_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text(root), encoding="utf-8")
    return target


def test_the_package_states_its_contract():
    """R17: the package says what it is and how it is used."""
    import tools.quality.rulings as package

    assert_package_contract(package, "tools.quality.rulings")


def test_both_arms_are_registered_in_the_floor():
    """⛔ Adding a check means adding it to `CHECKS`, and nowhere else."""
    assert check_rulings_index in CHECKS
    assert rulings_notice in NOTICES


def test_a_generated_index_is_clean(tmp_path):
    """The live shape: what the records derive is what is on disk."""
    build(tmp_path)
    assert check_rulings_index(tmp_path) == []


def test_the_live_tree_is_clean():
    """⛔ The reading the branch stands on: this repository's index is fresh."""
    assert check_rulings_index(repository_root()) == []


def test_a_hand_edited_index_is_a_finding(tmp_path):
    """⛔ PLANTED: one word changed in a generated document, which R19 calls a finding."""
    target = build(tmp_path)
    target.write_text(target.read_text(encoding="utf-8").replace("settled", "decided"), "utf-8")
    findings = check_rulings_index(tmp_path)
    assert [finding.rule for finding in findings] == [RULE_STALE]
    assert REBUILD_COMMAND in findings[0].message
    assert findings[0].path == INDEX_PATH


def test_a_new_ruling_with_no_row_is_a_finding(tmp_path):
    """⛔ The day a ruling is minted without an entry, this returns `no`."""
    build(tmp_path)
    tree(tmp_path, r15="# CTO — round 15\n\n## ⛔ Ruling 3 — minted after the index was built\n")
    findings = check_rulings_index(tmp_path)
    assert len(findings) == 1
    assert "3 rulings" in findings[0].message


def test_an_absent_index_is_a_finding(tmp_path):
    """A tree with records and no index resolves no citation at all."""
    tree(tmp_path, r14=ROUND_14)
    findings = check_rulings_index(tmp_path)
    assert len(findings) == 1
    assert "does not exist" in findings[0].message


def test_a_tree_with_no_ruling_records_passes_and_says_so(tmp_path):
    """⛔ Ruling 191: an empty population returns the PASS reading, never no reading.

    ⚠️ The floor runs over arbitrary roots — a corpus, a consumer repository, an
    installed tree — and none of them owes a rulings index. ⭐ The notice is what
    keeps that from being silence.
    """
    assert check_rulings_index(tmp_path) == []
    (line,) = rulings_notice(tmp_path)
    assert "no ruling records in this checkout" in line
    assert "not a failure" in line


def test_this_repository_owes_the_index_and_has_it():
    """⛔ The repository-specific half of the clause above, where `board`'s lives too."""
    assert (repository_root() / INDEX_PATH).is_file(), (
        f"{INDEX_PATH} is this repository's only resolvable home for a bare `(Ruling N)`"
    )


def test_the_notice_prints_the_denominator(tmp_path):
    """⛔ Ruling 48: a count with no population is `0 = 0`."""
    build(tmp_path)
    (line,) = rulings_notice(tmp_path)
    assert "2 rulings derived from 1 ruling records" in line
    assert "tail 2" in line
    assert "outside the series: none" in line


def test_the_notice_names_what_fell_outside_on_the_live_tree():
    """The live reading, and it is inhabited: one probe number sits outside the series."""
    (line,) = rulings_notice(repository_root())
    derived = len(entries(repository_root()))
    assert f"{derived} rulings derived from" in line
    assert "outside the series: 9999" in line
    assert "mint round disputed for" in line
