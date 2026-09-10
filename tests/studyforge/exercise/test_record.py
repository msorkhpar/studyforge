"""The `exercise` record, and R5's refusal in code (SF-23).

⭐ **R5's acceptance is here**: a `bundled` + `authoritative` record is
accepted, a `generated` + `authoritative` one is refused — in code, at the point
the record is read, so no consumer has to remember to ask.
"""

import json
from pathlib import Path

import pytest

from studyforge.exercise import (
    EXERCISE_KEYS,
    Exercise,
    ExerciseError,
    from_document,
    of,
    to_document,
)
from studyforge.unit.errors import ContentError
from tests.fixture_checks import excluded_by, fixture_paths
from tests.support import repository_root

WHERE = "basics/01-getting-started/unit-01/practice-1"

RECORD = {
    "main_path": "practice/basics-01/src/main/java/Greeter.java",
    "test_path": "practice/basics-01/src/test/java/GreeterTest.java",
    "run_command": ["mvn", "-q", "-pl", "practice/basics-01", "compile"],
    "test_command": ["mvn", "-q", "-pl", "practice/basics-01", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
}

GRADED_DOCUMENT = {"kind": "practice", "blocks": [], "exercise": RECORD}


def record(**changes):
    """The valid record with `changes` applied; a `None` value removes a key."""
    out = {**RECORD, **changes}
    return {key: value for key, value in out.items() if value is not None}


def refuse(call, *args):
    with pytest.raises(ExerciseError) as raised:
        call(*args)
    return str(raised.value)


# --------------------------------------------------------------------------
# reading a record
# --------------------------------------------------------------------------


def test_a_full_record_is_read_field_for_field():
    exercise = from_document(RECORD, WHERE)
    assert exercise.main_path == RECORD["main_path"]
    assert exercise.test_path == RECORD["test_path"]
    assert exercise.run_command == tuple(RECORD["run_command"])
    assert exercise.test_command == tuple(RECORD["test_command"])
    assert exercise.provenance == "bundled"
    assert exercise.trust == "authoritative"


def test_the_record_round_trips_through_a_document():
    # ⭐ R10: the record that reaches disk must be one the reader accepts back,
    # unchanged, in the same key order.
    exercise = from_document(RECORD, WHERE)
    again = to_document(exercise)
    assert tuple(again) == EXERCISE_KEYS
    assert from_document(again, WHERE) == exercise


def test_trust_defaults_from_provenance_rather_than_being_required():
    # ⚠️ `unit.trust`'s ruling, followed rather than restated: a field an
    # author must fill in to say the obvious is a field an author fills in
    # wrongly.
    assert from_document(record(trust=None), WHERE).trust == "authoritative"
    assert from_document(record(provenance="generated", trust=None), WHERE).trust == "advisory"


def test_a_defaulted_trust_is_still_written_out():
    # ⛔ A field that disappears when it is obvious cannot be told from one
    # nobody wrote — the archive's `counts` makes the same argument.
    written = to_document(from_document(record(trust=None), WHERE))
    assert written["trust"] == "authoritative"


def test_authoritative_asks_the_record_rather_than_the_provenance():
    assert from_document(RECORD, WHERE).authoritative is True
    assert from_document(record(provenance="user", trust=None), WHERE).authoritative is False


# --------------------------------------------------------------------------
# ⛔ R5, in code
# --------------------------------------------------------------------------


def test_a_bundled_authoritative_record_is_accepted():
    assert from_document(record(provenance="bundled", trust="authoritative"), WHERE)


def test_a_generated_authoritative_record_is_refused():
    # ⛔ E06's named acceptance, and R5's whole point: presenting our own
    # reading as the source's grader is a claim nobody notices is false until
    # a reader trusts a green tick that was never earned.
    message = refuse(from_document, record(provenance="generated", trust="authoritative"), WHERE)
    assert "R5" in message


def test_a_generated_advisory_record_is_accepted():
    # ⚠️ The negative control: `generated` is not refused, the *pair* is.
    assert from_document(record(provenance="generated", trust="advisory"), WHERE)


def test_the_rule_is_not_re_spelled_in_this_package(monkeypatch):
    # ⛔ `unit.trust` owns R5's rule and its own contract says "SF-23 consumes
    # it". Two spellings of one rule is the defect `placement.names.label_of`
    # records paying for, so this asserts the verdict comes from **there**.
    #
    # ⚠️ Asserted by **delegation**, not by importing that module's `FORBIDDEN`
    # tuple. Ruling 35 is restating R5 positively — `authoritative` implies
    # `bundled` — so a test shaped around the enumeration would go red for a
    # ruling that strengthens the rule it is guarding. What must stay true is
    # that this package asks rather than answers.
    called = []

    def refuses(provenance, trust=None):
        called.append((provenance, trust))
        raise ContentError("the owning module said no")

    monkeypatch.setattr("studyforge.exercise.record.check_test_record", refuses)
    message = refuse(from_document, RECORD, WHERE)
    assert called == [("bundled", "authoritative")], "the record did not ask unit.trust"
    assert "the owning module said no" in message, "the owner's sentence was re-worded"


def test_and_the_pair_r5_was_written_for_is_refused_however_it_is_stated():
    # ⭐ The behavioural half, which survives any restatement: a grader we
    # wrote may not claim to be the source's own.
    assert refuse(from_document, record(provenance="generated", trust="authoritative"), WHERE)


@pytest.mark.parametrize("provenance", ["Bundled", "vendored", "", None, 1])
def test_an_unknown_provenance_is_refused(provenance):
    assert refuse(from_document, record(provenance=provenance), WHERE)


@pytest.mark.parametrize("trust", ["Authoritative", "trusted", "", 1])
def test_an_unknown_trust_is_refused(trust):
    assert refuse(from_document, record(trust=trust), WHERE)


# --------------------------------------------------------------------------
# ⛔ every field is required, and no field is invented
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing", ["main_path", "test_path", "run_command", "test_command", "provenance"]
)
def test_a_record_missing_a_required_field_is_refused(missing):
    # ⛔ The key's presence means graded, and graded means a workspace **plus**
    # a grader. A record without one is an ungraded exercise wearing the
    # graded key — for which the contract is to write no key at all.
    message = refuse(from_document, record(**{missing: None}), WHERE)
    assert missing in message


def test_the_refusal_says_what_to_write_instead():
    message = refuse(from_document, record(test_command=None), WHERE)
    assert "write no 'exercise' key at all" in message


def test_a_key_the_record_does_not_define_is_refused():
    # ⛔ Finding 20's argument one level down: tolerating an unknown key means
    # tolerating a **typo** in a known one, and a misspelled field is a grader
    # nobody is offered while the corpus validates green.
    message = refuse(from_document, {**RECORD, "timeout_s": 30}, WHERE)
    assert "timeout_s" in message


def test_a_misspelled_known_field_is_caught_as_an_unknown_key():
    # ⚠️ The realistic case, and the reason the set is closed rather than open.
    message = refuse(from_document, {**record(test_command=None), "test_commnad": []}, WHERE)
    assert "test_commnad" in message


def test_an_unknown_key_that_could_carry_an_identifier_is_counted_not_named():
    # ⛔ Structural, not a shape list: a plain lowercase identifier holds no
    # '/', '@', ':' or space, so naming one is safe by construction. Anything
    # else is counted instead.
    poison = "/" + "home/janedoe/notes"
    message = refuse(from_document, {**RECORD, poison: 1}, WHERE)
    assert "janedoe" not in message


@pytest.mark.parametrize("value", [None, [], "exercise", 7, True])
def test_an_exercise_that_is_not_an_object_is_refused(value):
    assert refuse(from_document, value, WHERE)


# --------------------------------------------------------------------------
# ⛔ an exercise belongs to a practice document
# --------------------------------------------------------------------------


def test_of_returns_the_record_a_practice_document_carries():
    assert of(GRADED_DOCUMENT, WHERE) == from_document(RECORD, WHERE)


def test_of_returns_none_for_a_practice_with_no_exercise_key():
    # ⚠️ `None` is the **ungraded** answer and it is not a failure — it is two
    # of the three states, and the common one.
    assert of({"kind": "practice", "blocks": []}, WHERE) is None


def test_of_returns_none_for_a_lesson_that_carries_no_exercise():
    assert of({"kind": "lesson", "blocks": []}, WHERE) is None


def test_an_exercise_on_a_lesson_is_refused_rather_than_ignored():
    # ⛔ The key's presence *is* the graded state, so a key in the wrong place
    # is a grader the reader will never be offered while the corpus passes.
    message = refuse(of, {"kind": "lesson", "exercise": RECORD}, WHERE)
    assert "practice" in message and "'lesson'" in message


def test_an_exercise_on_a_document_with_no_kind_at_all_is_refused():
    message = refuse(of, {"exercise": RECORD}, WHERE)
    assert "neither" in message


# --------------------------------------------------------------------------
# the committed fixture — the graded state, shipped by this task
# --------------------------------------------------------------------------


GRADED_FIXTURE = Path(
    "tests/fixtures/depth2/archive/basics/01-getting-started/raw/java/unit-01/practice-1.json"
)
UNGRADED_FIXTURE = Path(
    "tests/fixtures/depth2/archive/advanced/02-going-further/raw/java/unit-01/practice-1.json"
)


def load(relative):
    return json.loads((repository_root() / relative).read_text(encoding="utf-8"))


def test_the_committed_graded_fixture_reads_back_field_for_field():
    # ⭐ **SF-23 ships this fixture.** Measured before it existed: nothing under
    # `tests/fixtures/` carried an `exercise` key, so the state this task
    # encodes had no committed example.
    exercise = of(load(GRADED_FIXTURE), "depth2 basics unit-01 practice-1")
    assert exercise is not None
    assert exercise.provenance == "bundled"
    assert exercise.authoritative is True
    assert exercise.run_command[-1] == "compile"
    assert exercise.test_command[-1] == "test"


def test_the_two_commands_in_the_fixture_are_actually_different():
    # ⛔ Run and Submit are different acts, and a fixture carrying one command
    # twice would let a design that conflated them look correct.
    exercise = of(load(GRADED_FIXTURE), "depth2")
    assert exercise.run_command != exercise.test_command


def test_the_other_committed_practice_is_ungraded():
    # ⚠️ Deliberate: the set carries all three states, and graded is the
    # exception in real material rather than the majority.
    assert of(load(UNGRADED_FIXTURE), "depth2 advanced unit-01 practice-1") is None


def test_no_exercise_appears_anywhere_in_the_depth_one_fixture():
    # ⛔ E06: "The depth-1 fixture (zero exercises) validates." A corpus with
    # no graders is complete, not short.
    #
    # ⭐ **Named reason for not taking `asserting=`** (`FND-09` acceptance 3):
    # `depth1` is this test's **subject**, not an exclusion policy. The claim
    # is about that one corpus by name, so there is nothing for a declaration
    # to widen or narrow. ⛔ Not the same thing as "skip `invalid/`".
    root = repository_root() / "tests/fixtures/depth1"
    swept = 0
    for path in sorted(root.rglob("*.json")):
        assert "exercise" not in json.loads(path.read_text(encoding="utf-8"))
        swept += 1
    assert swept >= 6, swept


#: ⛔ **The rule this module's sweeps assert** (Ruling 46). `of()` refuses an
#: exercise the source declared authoritative, which is exactly what
#: `user-authoritative` is declared to break — so the *valid* set is the one
#: the declaration leaves, and the refused set is the one it drops.
#: ⚠️ Both used to be `"/invalid/" in p.as_posix()`, which is the directory
#: name Ruling 46 forbids and which would have swept in an eighth fixture
#: declaring something else entirely.
ASSERTED = {"exercise-trust"}


def _carrying_an_exercise(*, asserting):
    """Every archive document a sweep asserting `asserting` may read that grades."""
    return [
        path
        for _where, path in fixture_paths(asserting=asserting, within="/raw/")
        if "exercise" in json.loads(path.read_text(encoding="utf-8"))
    ]


def test_exactly_one_valid_corpus_document_carries_an_exercise():
    # ⚠️ Pinned so "improving coverage" cannot quietly make the exception the
    # majority — see `tests/fixtures/README.md`. ⛔ The graded state is the
    # exception in real material, and a set in which it is the majority is a
    # set that will let a design fitted to the exception look correct.
    valid = _carrying_an_exercise(asserting=ASSERTED)
    assert len(valid) == 1, [p.name for p in valid]


def test_every_other_exercise_in_the_tree_exists_to_be_refused():
    # ⭐ The one sanctioned second copy, and its licence is that it must fail.
    # `user-authoritative` is W18's negative control: restore the forbidden-pair
    # list and it violates nothing, which reds the fixture-consistency suite.
    # ⛔ So the rule is not "one exercise in the tree" but "one that validates",
    # and this states the second half rather than leaving it to a count.
    everything = _carrying_an_exercise(asserting=())
    others = [p for p in everything if p not in _carrying_an_exercise(asserting=ASSERTED)]
    # ⭐ Derived from the declaration in both directions: the refused set is
    # exactly what naming `exercise-trust` drops, so an eighth fixture cannot
    # land here silently and cannot be missed here either.
    assert {p.parts[p.parts.index("invalid") + 1] for p in others} == excluded_by(ASSERTED)
    assert len(everything) == len(others) + 1
    for path in others:
        with pytest.raises(ExerciseError):
            of(json.loads(path.read_text(encoding="utf-8")), path.name)


def test_the_frozen_record_is_not_a_validated_one():
    # ⚠️ Worth asserting because `archive.document` relies on the opposite:
    # a dataclass can be constructed with anything, so it re-reads a record
    # through `from_document` even when the caller already holds one.
    unchecked = Exercise("/etc/passwd", "x", ("sh",), ("sh",), "bundled", "authoritative")
    assert unchecked.main_path == "/etc/passwd"
    assert refuse(from_document, to_document(unchecked), WHERE)
