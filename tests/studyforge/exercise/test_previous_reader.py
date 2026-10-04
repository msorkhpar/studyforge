"""The two-directional compatibility reading, taken WITH the previous reader.

⛔ **The case keys' compatibility claim is about a reader that is not in the
tree**: *a record without the case keys still reads unchanged, and a document
carrying them is refused by the previous release's reader.*
⚠️ **So it cannot be asserted from here.** A test that imported today's
`EXERCISE_KEYS` and reasoned about what an older build *would* have done would
be an assertion ABOUT the previous reader, and the half that matters — the
refusal — is exactly the half such a test cannot take.

⭐ **The previous reader is therefore RUN.** Its source is read out of git at
the ref below and imported as its own module, beside today's, and both are
asked the same questions in the same run. ⛔ The ref is pinned and named, not
resolved from `HEAD`: it is the previous release's tip, so this reading does not
move with the tree.

⚠️ **The instrument is checked before it is believed** — a loaded module that
was silently today's would pass every refusal test for the wrong reason, which
is a no-op plant wearing a green tick. `test_the_reader_loaded_is_genuinely_the
_previous_one` is that check, and the negative control beside it is that the
same module still READS a record without the case keys.

⛔ Mirrors no source module (R12 is one-way), because its subject is two
versions of one and not either of them.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from types import ModuleType

import pytest

from studyforge.exercise import (
    AUTHORED_KEYS,
    BREAKDOWN_KEYS,
    EXERCISE_KEYS,
    ExerciseError,
    from_document,
)
from studyforge.exercise import to_document as write
from tests.fixture_checks import fixture_paths
from tests.support import git, repository_root, run

#: ⛔ The ref this reading is taken against: the previous release's tip. ⚠️ Pinned rather
#: than derived — `HEAD` moves with the tree, and a "previous" reader that follows the
#: work is no control at all.
PREVIOUS = "9806710e"

#: The module the previous reader lives in, at that ref.
SOURCE = "src/studyforge/exercise/record.py"

WHERE = "kata/raw/python/unit-01/practice-1"

#: A record in the graded shape, whole, with no case keys.
BEFORE = {
    "main_path": "practice/basics-01/src/main/java/Greeter.java",
    "test_path": "practice/basics-01/src/test/java/GreeterTest.java",
    "run_command": ["mvn", "-q", "-pl", "practice/basics-01", "compile"],
    "test_command": ["mvn", "-q", "-pl", "practice/basics-01", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
}

#: What each new key carries in the documents below. ⭐ `kind` is its DEFAULT
#: token deliberately: a document saying the one thing the previous reader
#: already assumed is still a document it must refuse, because what it cannot
#: do is read the key at all.
AFTER = {
    "kind": "code",
    "cases": [{"id": "GreeterTest#greets", "kind": "main", "says": "It greets by name."}],
    "report": {"format": "junit", "path": "target/surefire-reports"},
    "origin": "docs/01-getting-started.md",
    "questions": [
        {
            "id": "q-1",
            "stem": "What does a greeter return?",
            "options": [
                {"id": "a", "text": "A greeting", "correct": True, "says": "The page says so."},
                {"id": "b", "text": "Nothing", "correct": False, "says": "It returns a string."},
            ],
            "origin": "docs/01-getting-started.md",
        }
    ],
    "mock": {"pass_mark": 70, "domains": [{"id": "d-1", "title": "A greeter"}]},
    "concepts": ["A greeter returns a greeting."],
    "files": ["practice/basics-01/notes.md"],
    "review": {"intervals_days": [1, 3, 7]},
    "cards": [{"id": "c-1", "front": "What does a greeter return?", "back": "A greeting."}],
    "layout": "page",
}

#: ⭐ A whole quiz as the quiz shape shipped it — the shape the previous reader cannot
#: read at all, since `questions` is not a key it defines and `kind` is not
#: either. ⚠️ Its own round trip is `tests/studyforge/exercise/quiz/`; what is
#: taken here is only the two-directional reading.
QUIZ_RECORD = {"kind": "quiz", "questions": AFTER["questions"]}

#: The rule the one invalid fixture carrying a record is declared to break
#: as a rule id. ⭐ This sweep reads every record through `from_document`, which
#: is the rule that fixture exists to be refused by.
ASSERTED = {"exercise-trust"}


def committed_records():
    """Every record this repository commits without case keys, with where it lives."""
    found = []
    for where, path in fixture_paths(asserting=ASSERTED, within="/raw/"):
        document = json.loads(path.read_text(encoding="utf-8"))
        if "exercise" in document:
            found.append((where, document["exercise"]))
    return found


COMMITTED = committed_records()


@pytest.fixture(scope="module")
def previous(tmp_path_factory) -> ModuleType:
    """The `exercise` record as of `PREVIOUS`, read out of git and imported beside today's.

    ⛔ Read-only (R3): `git show` writes nothing, and the source lands in a
    temporary directory rather than anywhere in the checkout.

    ⚠️ **Registered in `sys.modules` under its own name while it runs**, and
    removed after. A `slots=True` dataclass rebuilds its class and resolves
    `cls.__module__` through `sys.modules`, so a module executed outside it
    cannot define one — and the name carries the ref, so nothing of today's is
    shadowed.
    """
    shown = run([git(), "show", f"{PREVIOUS}:{SOURCE}"], cwd=repository_root())
    assert shown.returncode == 0, (
        f"git could not show {SOURCE} at {PREVIOUS}, so the previous reader cannot "
        f"be run and this clause cannot be answered: {shown.stdout + shown.stderr}"
    )
    path = tmp_path_factory.mktemp("previous") / "record_at_previous.py"
    path.write_text(shown.stdout, encoding="utf-8")
    name = f"studyforge_exercise_record_at_{PREVIOUS}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        del sys.modules[name]


def refused_by(reader, value):
    """The sentence `reader` refuses `value` with, or a failure saying it did not."""
    with pytest.raises(ExerciseError) as raised:
        reader.from_document(value, WHERE)
    return str(raised.value)


# --------------------------------------------------------------------------
# ⛔ the instrument, checked before it is believed
# --------------------------------------------------------------------------


def test_the_reader_loaded_is_genuinely_the_previous_one(previous):
    # ⛔ The plant, observed. A module that had silently resolved to today's
    # would pass every refusal below for the wrong reason and read as success.
    assert previous.__name__.endswith(PREVIOUS)
    assert previous.EXERCISE_KEYS != EXERCISE_KEYS
    assert [key for key in AUTHORED_KEYS if key in previous.EXERCISE_KEYS] == []
    assert set(previous.EXERCISE_KEYS) < set(EXERCISE_KEYS), (
        "today's record does not extend the previous one; something else changed"
    )


def test_and_it_is_a_working_reader_not_a_broken_one(previous):
    # ⭐ The negative control for every refusal below: this reader accepts the
    # shape it was written for, so a refusal is about the new keys and not
    # about how it was loaded.
    exercise = previous.from_document(BEFORE, WHERE)
    assert exercise.graded is True
    assert previous.to_document(exercise) == BEFORE


# --------------------------------------------------------------------------
# ⛔ the clause, both directions, in one run
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", list(AUTHORED_KEYS))
def test_a_document_carrying_a_new_key_is_refused_by_the_previous_reader(previous, key):
    # ⛔ This is what lets the contract land with no version bump: an older
    # build refuses the new shape rather than misreading it — spec §7's own
    # test, applied to the case keys (§6).
    message = refused_by(previous, {**BEFORE, key: AFTER[key]})
    assert key in message, "the previous reader refused without naming the key"


def test_the_whole_new_shape_is_refused_by_the_previous_reader(previous):
    assert refused_by(previous, {**BEFORE, **AFTER})


def test_a_new_key_on_a_practice_document_is_refused_by_the_previous_reader(previous):
    # ⭐ Through `of`, which is the path `archive.document.parse` takes, so the
    # refusal is the one a build would actually give.
    document = {"kind": "practice", "blocks": [], "exercise": {**BEFORE, **AFTER}}
    with pytest.raises(ExerciseError):
        previous.of(document, WHERE)


#: The keys in the groups today's reader accepts them in ON A CODE RECORD.
#: ⚠️ The breakdown is one group because it is written whole or not at all, so
#: `cases` alone is refused by BOTH readers — for different reasons, which is
#: why it is not the shape this claim is taken on. ⛔ **`questions` is absent
#: deliberately and that is not an omission**: the quiz shape makes it a key only a
#: QUIZ may carry, so on `BEFORE`'s shape today's reader refuses it too. Its
#: arm of this claim is the quiz test below, on a whole quiz record.
ACCEPTED = [("kind",), BREAKDOWN_KEYS, ("origin",)]


@pytest.mark.parametrize("keys", ACCEPTED, ids="+".join)
def test_and_todays_reader_accepts_each_of_them(previous, keys):
    # ⭐ The other direction of the same claim, in the same module so the two
    # cannot drift apart: what the previous reader refuses is exactly what this
    # one was built to read.
    document = {**BEFORE, **{key: AFTER[key] for key in keys}}
    assert from_document(document, WHERE)
    assert refused_by(previous, document)


def test_a_whole_quiz_is_refused_by_the_previous_reader_and_read_by_todays(previous):
    # ⛔ The quiz shape's half of the same two-directional claim, taken on the shape
    # that key exists for rather than on a code record wearing it. ⚠️ The
    # previous reader refuses it for the key it cannot read; today's reads it
    # and knows what it is.
    assert refused_by(previous, QUIZ_RECORD)
    exercise = from_document(QUIZ_RECORD, WHERE)
    assert exercise.is_quiz is True
    assert exercise.main_path is None and exercise.run_command is None


# --------------------------------------------------------------------------
# ⭐ a record without the case keys reads unchanged — every committed one
# --------------------------------------------------------------------------


def test_the_sweep_has_a_population_to_read():
    # ⛔ Every test below is a comparison, and an empty population
    # satisfies all of them. ⚠️ The five are the depth-2 graded fixture, the
    # execution fixture's three graded units and its ungraded one — the three
    # shapes the previous reader reads, which the case keys may not change.
    assert len(COMMITTED) >= 5, [where for where, _ in COMMITTED]
    # ⚠️ And inhabited by both shapes, or the sweep below would be a claim
    # about graded records alone.
    assert {"test_path" in record for _, record in COMMITTED} == {True, False}


@pytest.mark.parametrize("where,record", COMMITTED, ids=lambda value: str(value)[:40])
def test_a_committed_record_reads_the_same_through_both_readers(previous, where, record):
    was = previous.from_document(record, where)
    now = from_document(record, where)
    for field in previous.EXERCISE_KEYS:
        assert getattr(now, field) == getattr(was, field), field


@pytest.mark.parametrize("where,record", COMMITTED, ids=lambda value: str(value)[:40])
def test_a_committed_record_is_written_back_byte_for_byte_as_both_readers_had_it(
    previous, where, record
):
    # ⛔ R10, and the reason no version was bumped: what this build writes for
    # a record written before it is what is already on disk, key order
    # included. ⚠️ A key added unconditionally — `kind`, had it been written
    # out — would fail exactly here, on every corpus that exists.
    was = previous.to_document(previous.from_document(record, where))
    now = write(from_document(record, where))
    assert list(now.items()) == list(record.items()), "the record on disk would be rewritten"
    assert list(now.items()) == list(was.items()), "the two readers do not write the same bytes"
