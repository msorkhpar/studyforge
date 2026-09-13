"""Mirror of `tools/quality/subject.py` (R12).

⛔ **Asserted in BOTH directions** (`W149`'s third clause). A subject carrying a bare
count is REFUSED, and the same fact stated as a PROPERTY PASSES. ⚠️ **Every subject
here is a string BUILT FOR THE TEST.** A historical subject is frozen, and re-deriving
one is not this row's business. ⭐ The declared remainder (Ruling 292) is asserted
SILENT, so the gap is judged rather than discovered.
"""

from __future__ import annotations

import io

import pytest

import tools.quality.subject as subject_module
from tests.support import assert_package_contract
from tools.quality import CHECKS, NOTICES
from tools.quality.subject import PASSED, REFUSED, UNREAD, bare_counts, main, read_subject

HEADER = "Merge fix/W0-built-for-the-test (W0)"
READING = f"{HEADER}: all 57 dark checks pass"
PROPERTY = f"{HEADER}: every dark check passes"


def _claims(subject: str) -> list[tuple[str, tuple[str, ...]]]:
    return [(claim.text, claim.counts) for claim in read_subject(subject).claims]


def test_states_its_contract():
    assert_package_contract(subject_module, "tools.quality.subject")


# --- clause 3: both directions ------------------------------------------------


def test_a_bare_INTEGER_is_REFUSED_and_the_same_fact_as_a_PROPERTY_PASSES():
    assert read_subject(READING).verdict == REFUSED
    assert _claims(READING) == [("all 57 dark checks pass", ("57",))]
    assert read_subject(PROPERTY).verdict == PASSED
    assert _claims(PROPERTY) == [("every dark check passes", ())]


def test_a_count_in_WORDS_is_REFUSED_and_its_property_form_PASSES():
    # ⭐ `CTO-66/19`'s shape, built for the test: a count spelled as a word.
    assert read_subject(f"{HEADER}: two branches reviewed").verdict == REFUSED
    assert read_subject(f"{HEADER}: every branch offered was reviewed").verdict == PASSED


@pytest.mark.parametrize("count", ["0 of 25", "3-5", "12,000", "Seventeen"])
def test_every_digit_and_word_shape_of_a_count_is_read(count):
    assert bare_counts(f"a claim with {count} things in it") != ()


# --- clause 2: the population is the claims, ENUMERATED ------------------------


def test_the_claims_are_ENUMERATED_and_ONE_reading_among_properties_refuses():
    subject = f"{HEADER}: every check passes; two rows close -- the exit is unchanged"
    assert _claims(subject) == [
        ("every check passes", ()),
        ("two rows close", ("two",)),
        ("the exit is unchanged", ()),
    ]
    assert read_subject(subject).verdict == REFUSED


def test_an_EMPTY_population_is_UNREAD_and_never_the_pass_reading():
    # ⛔ Ruling 191: no claim read is exit 2, not a PASS.
    for subject in (f"{HEADER}: ", "", "   \n", f"{HEADER}: (CTO: APPROVE)"):
        assert read_subject(subject).verdict == UNREAD


# --- clause 4: the header and the bracket are not claims, and stay read elsewhere --


def test_the_HEADER_and_the_VERDICT_BRACKET_are_not_claims():
    subject = "Merge chore/cto-round9 (PO round 9): both APPROVED (CTO: CHANGES REQUESTED x2)"
    assert _claims(subject) == [("both APPROVED", ())]


def test_only_the_FIRST_LINE_is_the_subject():
    assert _claims(f"{PROPERTY}\n\nThe body may say 57 things.") == [
        ("every dark check passes", ())
    ]


# --- decided: a name is not a count --------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "W149",
        "INT-06/7",
        "INT06-1/4",
        "W162/5",
        "ab9e765",
        "R12",
        "§11.0",
        "ISO-8583",
        "Ruling 320",
        "Ruling 185(a)",
        "Rulings 223-234 and 235",
        "Rulings 217, 218 and 219",
        "PO round 77",
        "exit 0",
        "order 0",
        "spec section 5",
        "the user's answer 2",
        "2026-09-12",
    ],
)
def test_a_NAME_that_carries_digits_is_not_a_count(name):
    assert bare_counts(f"{name} is named here") == ()


def test_a_naming_word_binds_only_its_own_run():
    assert bare_counts("Ruling 320 lands and 57 checks pass") == ("57",)


# --- declared, not decided (Ruling 292): each asserted SILENT -------------------


@pytest.mark.parametrize(
    "declared",
    [
        "one home and at zero ahead",  # 1. `one` and `zero` name a case
        "a three-name contract and a 3-way merge",  # 2. a hyphen compound names a kind
        "refuted for the second time",  # 3. an ordinal
        "the reading `57 checks` quoted",  # 4. a code span is a mention
        "both and all and every",  # 5. a quantifier with no numeral
        "measured GREEN at the tip",  # 6. a reading with no count
    ],
)
def test_the_DECLARED_remainder_is_SILENT(declared):
    assert bare_counts(declared) == ()


# --- the MUST NOT: it refuses and names, never edits, never sweeps --------------


def test_the_command_REFUSES_and_NAMES_the_claim_and_the_count(capsys):
    assert main([READING]) == REFUSED
    printed = capsys.readouterr().out
    assert "claim 1  READING   all 57 dark checks pass" in printed
    assert "REFUSED: claim 1 is a READING" in printed and "`57`" in printed
    assert "W149" in printed and HEADER not in printed


def test_the_command_PASSES_a_property_and_prints_its_population(capsys):
    assert main([PROPERTY]) == PASSED
    printed = capsys.readouterr().out
    assert "1 claim(s) read" in printed and "PASSED" in printed


def test_the_command_reads_STDIN_when_no_argument_is_given(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(READING + "\n"))
    assert main([]) == REFUSED
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert main([]) == UNREAD
    assert "UNREAD" in capsys.readouterr().out


def test_it_is_NOT_a_sweep_of_history():
    # ⛔ The row: not in the floor's checks or notices, so no report on frozen subjects.
    registered = {function.__module__ for function in (*CHECKS, *NOTICES)}
    assert subject_module.__name__ not in registered
