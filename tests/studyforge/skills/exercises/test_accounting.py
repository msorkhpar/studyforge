"""Mirror of `src/studyforge/skills/exercises/accounting.py` (R12) — the *nothing is lost* half.

**What it asserts.** Spec §7's *nothing is lost*, mechanically: each ledger entry
ends either as the basis of an exercise — named by that exercise's `origin` —
or with a written reason it is not, and ⛔ **an entry with neither is refused**.
Plus the region rules an origin resolves through, and the byte stability of the
document the skill commits (R10).

⭐ **Every refusal below is read beside a positive control on the same ledger**,
because a control that reads the same as the experiment has controlled nothing.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import Origin
from studyforge.skills.exercises.accounting import (
    ACCOUNTED_KEYS,
    LEDGER_API,
    LEDGER_KEYS,
    account,
    accounts_for,
    ledger_document,
)
from studyforge.skills.exercises.ledger import ENTRY_KEYS, LedgerError, key_of, take
from tests.studyforge.skills.exercises.pages import BECAUSE, PAGE, written


def ledger_of(root, text=PAGE, name="guide.md"):
    """One page's ledger, which every case below starts from."""
    return take(root, (written(root, name, text),), (), "the ledger")


def test_an_entry_with_no_exercise_and_no_reason_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    unaccounted = key_of(ledger.entries[0])
    reasons = {key_of(entry): BECAUSE for entry in ledger.entries[1:]}
    with pytest.raises(LedgerError) as refusal:
        account(ledger, {}, reasons, "the ledger")
    assert unaccounted in str(refusal.value), "the refusal names the entry it refused"
    assert "nothing is lost" in str(refusal.value), "the refusal says what it is protecting"


def test_the_same_ledger_with_every_entry_excused_is_accepted(tmp_path):
    """⭐ The positive control beside the refusal above."""
    ledger = ledger_of(tmp_path)
    accounted = account(
        ledger, {}, {key_of(entry): BECAUSE for entry in ledger.entries}, "the ledger"
    )
    assert len(accounted) == len(ledger.entries)
    assert all(row.reason == BECAUSE and not row.exercises for row in accounted)


def test_an_exercise_accounts_for_the_examples_inside_the_region_its_origin_names(tmp_path):
    ledger = ledger_of(tmp_path)
    accounted = account(
        ledger,
        {"unit-01/practice-1": Origin("guide.md", "Edge cases")},
        {key_of(entry): BECAUSE for entry in ledger.entries if "Edge cases" not in entry.sections},
        "the ledger",
    )
    covered = [row for row in accounted if row.exercises]
    assert [row.entry.ordinal for row in covered] == [2], "the region covers its own fence only"
    assert covered[0].exercises == ("unit-01/practice-1",)


def test_an_origin_naming_the_whole_file_accounts_for_every_example_in_it(tmp_path):
    ledger = ledger_of(tmp_path)
    accounted = account(ledger, {"whole": Origin("guide.md", None)}, {}, "the ledger")
    assert all(row.exercises == ("whole",) for row in accounted)
    assert all(row.reason is None for row in accounted)


def test_an_ancestor_section_accounts_for_an_example_nested_under_it(tmp_path):
    ledger = ledger_of(tmp_path)
    nested = next(entry for entry in ledger.entries if entry.ordinal == 2)
    assert nested.sections == ("Adding up", "Edge cases"), "the chain is outermost first"
    assert accounts_for(nested, Origin("guide.md", "Adding up")), "Ruling 92, from the inside"
    assert not accounts_for(nested, Origin("guide.md", "Elsewhere")), "a sibling covers nothing"
    assert not accounts_for(nested, Origin("other.md", None)), "another file covers nothing"


def test_two_exercises_on_one_entry_are_both_named_and_in_a_fixed_order(tmp_path):
    ledger = ledger_of(tmp_path)
    accounted = account(
        ledger,
        {"second": Origin("guide.md", None), "first": Origin("guide.md", None)},
        {},
        "the ledger",
    )
    assert all(row.exercises == ("first", "second") for row in accounted), "sorted, not handed in"


def test_an_entry_that_is_both_the_basis_of_an_exercise_and_excused_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    with pytest.raises(LedgerError) as refusal:
        account(
            ledger,
            {"whole": Origin("guide.md", None)},
            {key_of(entry): BECAUSE for entry in ledger.entries},
            "the ledger",
        )
    assert "cannot both be true" in str(refusal.value)


def test_a_reason_filed_under_no_entry_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    reasons = {key_of(entry): BECAUSE for entry in ledger.entries}
    reasons["example:guide.md:99"] = BECAUSE
    with pytest.raises(LedgerError) as refusal:
        account(ledger, {}, reasons, "the ledger")
    assert "guide.md:99" in str(refusal.value)


def test_a_reason_that_is_not_a_sentence_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    for empty in ("", "   ", 3, True):
        reasons = {key_of(entry): BECAUSE for entry in ledger.entries}
        reasons[key_of(ledger.entries[0])] = empty
        with pytest.raises(LedgerError):
            account(ledger, {}, reasons, "the ledger")


def test_an_origin_the_ledger_never_read_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    with pytest.raises(LedgerError) as refusal:
        account(ledger, {"stray": Origin("elsewhere.md", None)}, {}, "the ledger")
    assert "elsewhere.md" in str(refusal.value)
    assert "does not account for" in str(refusal.value)


def test_an_exercise_name_a_record_could_not_carry_is_refused(tmp_path):
    """⛔ One family for a caller of this package — the rule is imported, the type is ours."""
    ledger = ledger_of(tmp_path)
    for bad in ("with a space", "", None):
        with pytest.raises(LedgerError):
            account(ledger, {bad: Origin("guide.md", None)}, {}, "the ledger")


def test_a_section_the_file_does_not_carry_is_refused(tmp_path):
    ledger = ledger_of(tmp_path)
    with pytest.raises(LedgerError) as refusal:
        account(ledger, {"p": Origin("guide.md", "Renamed heading")}, {}, "the ledger")
    assert "0 times" in str(refusal.value)
    assert "Renamed heading" not in str(refusal.value), "the section is not reproduced (R7)"


def test_a_section_the_file_carries_twice_is_refused(tmp_path):
    ledger = ledger_of(tmp_path, "# Same\n\n```py\na\n```\n\n# Same\n\n```py\nb\n```\n", "twice.md")
    with pytest.raises(LedgerError) as refusal:
        account(ledger, {"p": Origin("twice.md", "Same")}, {}, "the ledger")
    assert "2 times" in str(refusal.value), "zero and two are both loud (SF-36)"


def test_an_origin_that_accounts_for_no_entry_is_not_a_fault(tmp_path):
    """⭐ A quiz cites a PASSAGE, and a passage of prose holds no fence."""
    ledger = ledger_of(tmp_path, "# Only prose\n\nNothing fenced here at all.\n", "prose.md")
    assert ledger.entries == (), "a prose page carries no entry"
    assert account(ledger, {"q-1": Origin("prose.md", "Only prose")}, {}, "the ledger") == ()


def test_the_document_writes_both_endings_for_every_entry(tmp_path):
    ledger = ledger_of(tmp_path)
    accounted = account(
        ledger,
        {"p": Origin("guide.md", "Edge cases")},
        {key_of(entry): BECAUSE for entry in ledger.entries if "Edge cases" not in entry.sections},
        "the ledger",
    )
    document = ledger_document(ledger, accounted)
    assert list(document) == list(LEDGER_KEYS), "the document's keys are in write order"
    assert document["ledger_api"] == LEDGER_API
    for entry in document["entries"]:
        assert list(entry) == list(ENTRY_KEYS) + list(ACCOUNTED_KEYS), "both keys, always"
    assert document["sources"][0]["sections"] == ["Adding up", "Edge cases", "Elsewhere"]


def test_re_running_on_an_unchanged_corpus_produces_a_byte_identical_ledger(tmp_path):
    """⛔ R10, and the caller's mapping order is part of what must not matter."""
    ledger = ledger_of(tmp_path)
    reasons = {key_of(entry): BECAUSE for entry in ledger.entries}
    left = ledger_document(ledger, account(ledger, {}, reasons, "the ledger"))
    right = ledger_document(
        ledger, account(ledger, {}, dict(reversed(list(reasons.items()))), "a different where")
    )
    assert left == right, "two accountings of one unchanged ledger disagree"
