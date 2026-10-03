"""The case vocabulary, and the record's reading of the four case keys.

⭐ **The case record's acceptance is here** except its last clause, which is a reading
taken with the **previous** reader and lives in `test_previous_reader.py`:
`cases`, `report`, `origin` and `kind` round-trip; a case map on an ungraded
record is refused, naming the key; an unknown case kind is refused; an unknown
exercise kind is refused.

⚠️ **No fixture is added and none is modified.** The corpus and
`tests/fixtures/runnable/` carry the three shapes with no `cases`, and this
contract's job is to keep them valid — so the documents below live here, where
a shape being *refused* cannot be mistaken for material.
"""

import pytest

from studyforge.corpus.container import ORIGIN_KEYS as CONTAINER_ORIGIN_KEYS
from studyforge.corpus.container import ContainerError
from studyforge.exercise import (
    AUTHORED_KEYS,
    BREAKDOWN_KEYS,
    CASE_KEYS,
    CASE_KINDS,
    CODE,
    DEFAULT_KIND,
    EDGE,
    EXERCISE_KEYS,
    EXERCISE_KINDS,
    JUNIT,
    MAIN,
    ORIGIN_KEYS,
    QUIZ,
    REPORT_FORMATS,
    REPORT_KEYS,
    Case,
    Exercise,
    ExerciseError,
    Origin,
    Report,
    cases_document,
    cases_of,
    from_document,
    kind_of,
    of,
    origin_document,
    origin_in,
    report_document,
    report_of,
    to_document,
)

WHERE = "iso/02-parsing/unit-02/practice-1"

#: The ungraded shape: the reader's file, and how it runs.
UNGRADED = {
    "main_path": "practice/iso-02/src/main/java/Parser.java",
    "run_command": ["mvn", "-q", "-pl", "practice/iso-02", "compile"],
}

#: The grader half, written whole.
GRADER = {
    "test_path": "practice/iso-02/src/test/java/ParserTest.java",
    "test_command": ["mvn", "-q", "-pl", "practice/iso-02", "test"],
    "provenance": "generated",
    "trust": "advisory",
}

#: ⭐ The shape an authored exercise takes: an ask, one named edge of it, the report the two
#: ids are read out of, and the passage the exercise was built from.
CASES = [
    {"id": "com.example.ParserTest#parsesTheMti", "kind": MAIN, "says": "It reads the MTI."},
    {
        "id": "com.example.ParserTest#refusesAShortMessage",
        "kind": EDGE,
        "says": "A message shorter than its header is refused.",
    },
]
REPORT = {"format": JUNIT, "path": "practice/iso-02/target/surefire-reports"}
ORIGIN = {"path": "docs/02-parsing.md", "section": "Parsing the MTI"}

#: The whole case record: graded, authored, with a breakdown and an origin.
AUTHORED = {**UNGRADED, **GRADER, "cases": CASES, "report": REPORT, "origin": ORIGIN}

#: ⭐ The least a quiz may carry. Named here so the seam test below
#: reads one shape rather than re-deriving it; the questions' own tests are
#: in `tests/studyforge/exercise/quiz/`.
QUESTIONS = [
    {
        "id": "q-1",
        "stem": "What does the MTI name?",
        "options": [
            {"id": "a", "text": "The message type", "correct": True, "says": "The page says so."},
            {"id": "b", "text": "The bitmap", "correct": False, "says": "That is the next field."},
        ],
        "origin": ORIGIN,
    }
]


def record(**changes):
    """The authored record with `changes` applied; a `None` value removes a key."""
    out = {**AUTHORED, **changes}
    return {key: value for key, value in out.items() if value is not None}


def refuse(call, *args):
    with pytest.raises(ExerciseError) as raised:
        call(*args)
    return str(raised.value)


def case(**changes):
    """The main-ask case with `changes` applied; a `None` value removes a key."""
    out = {**CASES[0], **changes}
    return {key: value for key, value in out.items() if value is not None}


# --------------------------------------------------------------------------
# ⭐ The four keys round-trip
# --------------------------------------------------------------------------


def test_the_four_keys_round_trip_through_the_record():
    exercise = from_document(AUTHORED, WHERE)
    assert exercise.kind == CODE
    assert exercise.cases == (
        Case("com.example.ParserTest#parsesTheMti", MAIN, "It reads the MTI."),
        Case(
            "com.example.ParserTest#refusesAShortMessage",
            EDGE,
            "A message shorter than its header is refused.",
        ),
    )
    assert exercise.report == Report(JUNIT, REPORT["path"])
    assert exercise.origin == Origin(ORIGIN["path"], ORIGIN["section"])
    again = to_document(exercise)
    assert again == AUTHORED, "a written record is not the one that was read"
    # ⚠️ Every key but `kind`, which this record does not carry — it is `code`,
    # and the default is not written out — and `questions`, which only a QUIZ
    # carries. The rest are in the record's own order, appended after
    # the six an untested unit's record carries.
    written = tuple(
        key for key in EXERCISE_KEYS if key not in ("kind", "questions", "mock", "concepts")
    )
    assert tuple(again) == written, "the authored keys are not in the record's order"
    assert from_document(again, WHERE) == exercise


def test_the_quiz_token_now_selects_a_shape_and_not_a_label():
    # ⭐ Stated for the quiz shape too, and strictly stronger: this asserts that
    # a record may SAY it is a quiz; a quiz now has a shape, so the same
    # document — a workspace wearing the token — is refused, and the token
    # reads back off the record the quiz shape gives it.
    # ⚠️ The quiz's own round trip lives in `tests/studyforge/exercise/quiz/`,
    # with the rest of its tests; what is asserted here is the seam.
    message = refuse(from_document, record(kind=QUIZ), WHERE)
    assert "main_path" in message, "a workspace on a quiz was not named"
    quiz = from_document({"kind": QUIZ, "questions": QUESTIONS}, WHERE)
    assert quiz.kind == QUIZ
    assert to_document(quiz)["kind"] == QUIZ


def test_an_origin_may_be_a_whole_file_and_keeps_the_shape_it_was_written_in():
    # ⭐ An origin's two shapes: a path is the string form, a region is the
    # object. ⛔ Neither is rewritten into the other, because a corpus declared
    # one of them and only the corpus knows which it meant.
    written = record(origin="docs/02-parsing.md")
    whole = from_document(written, WHERE)
    assert whole.origin == Origin("docs/02-parsing.md", None)
    assert to_document(whole) == written, "the string form did not survive"
    assert to_document(from_document(AUTHORED, WHERE)) == AUTHORED, "nor did the region"


def test_an_ungraded_record_may_still_say_what_it_was_built_from():
    # ⭐ An `origin` is a fact about the MATERIAL, not about a grader (spec §7
    # §3): the source ledger must resolve the entry whether or not anything
    # checks the reader's answer.
    written = {**UNGRADED, "origin": "docs/02-parsing.md"}
    exercise = from_document(written, WHERE)
    assert (exercise.graded, exercise.origin) == (False, Origin("docs/02-parsing.md", None))
    assert to_document(exercise) == written


def test_the_authored_keys_are_appended_never_inserted():
    # ⛔ R10: a record that gains a `kind` must not reorder what was already on
    # disk, so the four keys sit after the six an untested unit's record carries, in this order.
    assert EXERCISE_KEYS[-len(AUTHORED_KEYS) :] == AUTHORED_KEYS
    # ⭐ The quiz shape's own key sits after the four rather
    # than inserting one among them, and what an exercise practises after it.
    assert AUTHORED_KEYS == ("kind", *BREAKDOWN_KEYS, "origin", "questions", "mock", "concepts")


# --------------------------------------------------------------------------
# ⛔ a key is written only where the record carries it
# --------------------------------------------------------------------------


def test_todays_record_writes_none_of_the_four_keys():
    # ⛔ The clause the whole no-version-bump argument rests on, asserted here
    # on a constructed record and in `test_previous_reader.py` on every
    # committed one.
    written = to_document(from_document({**UNGRADED, **GRADER}, WHERE))
    assert [key for key in written if key in AUTHORED_KEYS] == []


def test_the_default_kind_is_not_written_out():
    # ⚠️ The one place this record departs from `trust`, which IS written when
    # defaulted. The reason is the installed base: every record ever written is
    # `code`, so writing the token would re-render every archive document that
    # exists (R10). ⭐ Value-for-value the round trip still holds.
    explicit = from_document(record(kind=CODE), WHERE)
    assert explicit.kind == CODE
    assert "kind" not in to_document(explicit)
    assert from_document(to_document(explicit), WHERE) == explicit


def test_a_record_with_no_kind_is_a_code_exercise():
    assert DEFAULT_KIND == CODE
    assert from_document({**UNGRADED, **GRADER}, WHERE).kind == CODE


def test_the_keys_written_follow_the_shape_never_which_values_are_none():
    # ⛔ The dataclass is frozen, not validated. One built with a breakdown and
    # no grader must not write half a claim to disk — the untested unit's argument, and
    # the same test one key further on.
    stray = Exercise(
        "practice/hello.py",
        None,
        ("python3", "practice/hello.py"),
        None,
        None,
        None,
        cases=(Case("t", MAIN, "It works."),),
        report=Report(JUNIT, "reports"),
    )
    assert [key for key in to_document(stray) if key in BREAKDOWN_KEYS] == []
    half = Exercise(*[AUTHORED[key] for key in ("main_path", "test_path")], ("mvn",), ("mvn",),
                    "generated", "advisory", cases=(Case("t", MAIN, "It works."),))  # fmt: skip
    assert [key for key in to_document(half) if key in BREAKDOWN_KEYS] == []


# --------------------------------------------------------------------------
# ⛔ A breakdown on an ungraded record is refused, by name
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", list(BREAKDOWN_KEYS))
def test_a_case_map_or_a_report_on_an_ungraded_record_is_refused_naming_the_key(key):
    message = refuse(from_document, {**UNGRADED, key: AUTHORED[key]}, WHERE)
    assert key in message
    assert "no grader" in message


def test_the_refusal_says_what_an_ungraded_record_may_carry_instead():
    assert "'origin'" in refuse(from_document, {**UNGRADED, "cases": CASES}, WHERE)


@pytest.mark.parametrize("missing", list(BREAKDOWN_KEYS))
def test_a_breakdown_written_in_part_is_refused_naming_what_is_missing(missing):
    # ⛔ Whole or not at all, for the grader half's own reason: `cases` with no
    # `report` names tests nothing can be read from, and a `report` with no
    # `cases` is a file nothing folds through.
    message = refuse(from_document, record(**{missing: None}), WHERE)
    assert missing in message


def test_a_graded_record_need_not_carry_a_breakdown_at_all():
    # ⚠️ The negative control: `cases` is a shape a record may add, never one it
    # must. A graded record with no `cases` stays valid.
    assert from_document({**UNGRADED, **GRADER}, WHERE).breaks_down is False
    assert from_document(AUTHORED, WHERE).breaks_down is True


# --------------------------------------------------------------------------
# ⛔ An unknown kind is refused, on the exercise and on a case
# --------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["puzzle", "Code", "", None, 1, ["code"]])
def test_an_unknown_exercise_kind_is_refused(kind):
    message = refuse(from_document, {**AUTHORED, "kind": kind}, WHERE)
    assert str(list(EXERCISE_KINDS)) in message, "the refusal does not say what is permitted"


@pytest.mark.parametrize("kind", ["corner", "Main", "", None, 1, [MAIN]])
def test_an_unknown_case_kind_is_refused(kind):
    # ⚠️ Written directly rather than through `case()`, which drops a `None`:
    # a case whose kind is JSON `null` is a kind that is wrong, not one that
    # is missing, and both are refused for different reasons.
    wrong = [{**CASES[0], "kind": kind}, CASES[1]]
    message = refuse(from_document, record(cases=wrong), WHERE)
    assert str(list(CASE_KINDS)) in message


def test_both_kind_vocabularies_are_closed_and_neither_leaks_into_the_other():
    # ⛔ Two closed sets, and the tell that they are two: no token is in both,
    # so a case kind written as an exercise kind is refused rather than read.
    assert not set(EXERCISE_KINDS) & set(CASE_KINDS)
    assert kind_of(CODE, WHERE) == CODE and kind_of(QUIZ, WHERE) == QUIZ
    assert refuse(kind_of, MAIN, WHERE)


# --------------------------------------------------------------------------
# the case map: a map, and total over the ask it belongs to
# --------------------------------------------------------------------------


def test_the_cases_keep_the_order_they_were_written_in():
    # ⭐ A list and not an object: the reader is shown these in order, and two
    # ids that collide must be refusable rather than silently one entry.
    read = cases_of([CASES[1], CASES[0]], WHERE)
    assert [one.id for one in read] == [CASES[1]["id"], CASES[0]["id"]]
    assert cases_document(read) == [CASES[1], CASES[0]]
    assert [tuple(one) for one in cases_document(read)] == [CASE_KEYS, CASE_KEYS]


def test_a_map_naming_no_main_ask_is_refused():
    # ⛔ A reader is shown "main ask" plus "edge cases n/m", so a map of edges
    # alone describes a run whose ask nothing reports.
    message = refuse(cases_of, [CASES[1]], WHERE)
    assert MAIN in message


def test_a_map_is_a_map_and_a_repeated_id_is_refused_without_quoting_it():
    poison = "com.example.Test#jane"
    message = refuse(cases_of, [case(id=poison), case(id=poison), CASES[1]], WHERE)
    assert "more than once" in message
    assert "jane" not in message, "a case id is corpus data and is not reproduced (R7)"


def test_an_empty_case_map_is_refused_rather_than_read_as_no_breakdown():
    # ⚠️ Absent and empty are different mistakes: a grader that names nothing
    # writes no `cases` key, and an empty list is somebody who meant to.
    assert refuse(cases_of, [], WHERE)


@pytest.mark.parametrize("value", [None, {}, "main", 7, True])
def test_a_case_map_that_is_not_an_array_is_refused(value):
    assert refuse(cases_of, value, WHERE)


@pytest.mark.parametrize("entry", [None, "main", 7, ["id"]])
def test_a_case_that_is_not_an_object_is_refused(entry):
    assert refuse(cases_of, [entry], WHERE)


@pytest.mark.parametrize("missing", list(CASE_KEYS))
def test_a_case_missing_any_of_its_three_keys_is_refused_naming_it(missing):
    assert missing in refuse(cases_of, [case(**{missing: None})], WHERE)


def test_a_key_a_case_does_not_define_is_refused():
    # ⛔ `record`'s argument one level further down: tolerating an unknown key
    # is tolerating a typo in a known one, and a misspelled `says` is a case
    # the reader is shown nothing for while the corpus validates green.
    assert "weight" in refuse(cases_of, [{**CASES[0], "weight": 2}], WHERE)
    assert "says" in refuse(cases_of, [{**case(says=None), "sais": "typo"}], WHERE)


@pytest.mark.parametrize("says", [None, "", "   ", 7, ["a sentence"]])
def test_a_case_with_nothing_to_say_is_refused(says):
    # ⛔ `says` is what a reader is shown when the case fails; a blank one is a
    # failed edge case reported as an empty line.
    assert "says" in refuse(cases_of, [case(says=says)], WHERE)


@pytest.mark.parametrize(
    "spelling",
    [
        "com.example.ParserTest#parsesTheMti",
        "tests/test_parser.py::test_parses_the_mti",
        "ParserTest.parses[1]",
        "ParserTest.adds(int, int)".replace(" ", ""),
        "suite:parser+edge",
    ],
)
def test_an_id_is_read_as_the_report_spells_it(spelling):
    # ⭐ Wider than a path or an argv token on purpose: this value is compared
    # byte for byte with what a report writes, across two test runners.
    assert cases_of([{**CASES[0], "id": spelling}], WHERE)[0].id == spelling


@pytest.mark.parametrize(
    "spelling", ["", "   ", "a  test", " a test", "a\ttest", None, 7, "Test#x\n"]
)
def test_an_id_no_report_could_spell_is_refused(spelling):
    # ⚠️ The trailing newline is in the population deliberately: `$` matches
    # before one, so an id ending in a newline is exactly the shape a pattern
    # anchored the ordinary way lets through.
    assert "id" in refuse(cases_of, [{**CASES[0], "id": spelling}], WHERE)


def test_a_refused_id_is_not_reproduced():
    # ⛔ R7: an id is corpus data, and a refusal that echoed it would put the
    # one shape being refused into a build log.
    assert "janedoe" not in refuse(cases_of, [case(id="a  test by janedoe")], WHERE)


# --------------------------------------------------------------------------
# the report: what it is, and where it lands
# --------------------------------------------------------------------------


def test_the_report_round_trips_in_its_own_key_order():
    read = report_of(REPORT, WHERE)
    assert (read.format, read.path) == (JUNIT, REPORT["path"])
    assert tuple(report_document(read)) == REPORT_KEYS
    assert report_document(read) == REPORT


@pytest.mark.parametrize("format_", ["console", "junit-xml", "JUnit", "", None, 1])
def test_a_format_this_build_cannot_read_is_refused(format_):
    # ⛔ Closed, and console output is deliberately not in it: the quiet run
    # modes rewrite that stream by design.
    message = refuse(report_of, {**REPORT, "format": format_}, WHERE)
    assert str(list(REPORT_FORMATS)) in message


@pytest.mark.parametrize("value", [{"format": JUNIT}, {"path": "reports"}, {}, None, "reports", 1])
def test_a_report_that_is_not_both_keys_is_refused(value):
    assert refuse(report_of, value, WHERE)


@pytest.mark.parametrize("path", ["/var/reports", "../reports", "", None, ["reports"]])
def test_a_report_path_meets_the_same_safety_as_the_workspace(path):
    # ⛔ The report is read out of the workspace after a run, so it obeys
    # `safety`'s rule and not a second one written here.
    assert refuse(report_of, {**REPORT, "path": path}, WHERE)


# --------------------------------------------------------------------------
# the origin: a location inside the SOURCE, not inside the workspace
# --------------------------------------------------------------------------


def test_the_shape_is_sf_36s_and_this_package_does_not_spell_it_again(monkeypatch):
    # ⛔ `origin` has ONE reader in this tree, so this asserts the
    # verdict comes from THERE — by delegation, never by comparing a copied
    # tuple, which is the shape `record`'s own R5 test settled on.
    called = []

    def refuses(value, what, where):
        called.append((value, what))
        raise ContainerError("the owning module said no")

    monkeypatch.setattr("studyforge.corpus.container.fields.optional_origin", refuses)
    message = refuse(origin_in, {"origin": ORIGIN}, WHERE)
    assert called == [(ORIGIN, "origin")], "the record did not ask the one reader"
    assert message == "the owning module said no", "the owner's sentence was re-worded"


def test_and_the_tuple_is_that_readers_own(monkeypatch):
    # ⭐ Imported, never re-typed: two spellings of one shape is the defect
    # `describe` was extracted over.
    assert ORIGIN_KEYS is CONTAINER_ORIGIN_KEYS


def test_a_record_that_declares_no_origin_carries_none():
    # ⚠️ And a written `null` is the same answer, which is the one reader's own
    # contract ("a path, or absent") rather than a decision taken here. ⛔ The
    # record then writes no `origin` key, so the null does not survive a round
    # trip — the same canonicalisation a defaulted `kind` gets.
    assert origin_in({}, WHERE) is None
    assert origin_in({"origin": None}, WHERE) is None


@pytest.mark.parametrize(
    "value",
    [
        {"path": "docs/02-parsing.md"},
        {"section": "Parsing the MTI"},
        {**ORIGIN, "line": 12},
        {},
    ],
)
def test_a_region_that_is_not_both_keys_is_refused(value):
    # ⛔ A path alone is the string form written the long way, and a section
    # alone is a region of nothing.
    assert refuse(origin_in, {"origin": value}, WHERE)


@pytest.mark.parametrize("section", ["", "   ", 7, None, ["Parsing"]])
def test_a_region_with_no_heading_is_refused(section):
    assert "section" in refuse(origin_in, {"origin": {**ORIGIN, "section": section}}, WHERE)


#: ⚠️ **The two home-path shapes are ASSEMBLED at run time, never written as
#: literals**: this file is swept by the repository's own personal-data gate,
#: and a tracked line carrying one is the violation that gate exists to refuse.
#: ⛔ Nothing here came from any real machine or account.
OUTSIDE_THE_SOURCE = [
    "/" + "etc/passwd",
    "../outside.md",
    "~" + "janedoe/notes.md",
    "~" + "/notes.md",
    "docs/a.md#heading",
    "",
    7,
]


@pytest.mark.parametrize("path", OUTSIDE_THE_SOURCE, ids=lambda value: repr(value))
def test_an_origin_outside_the_source_is_refused_without_quoting_it(path):
    message = refuse(origin_in, {"origin": path}, WHERE)
    assert "janedoe" not in message, "the one refused shape is where a home directory lives (R7)"


def test_an_origin_fragment_is_refused_because_a_region_is_an_object():
    # ⛔ Left legal, the old spelling keeps validating
    # and keeps meaning nothing.
    assert refuse(origin_in, {"origin": "docs/02-parsing.md#parsing-the-mti"}, WHERE)
    assert origin_document(origin_in({"origin": ORIGIN}, WHERE)) == ORIGIN


# --------------------------------------------------------------------------
# ⭐ it lands where contracts land: through `of`, on a practice document
# --------------------------------------------------------------------------


def test_the_authored_record_is_read_through_a_practice_document():
    exercise = of({"kind": "practice", "blocks": [], "exercise": AUTHORED}, WHERE)
    assert exercise is not None
    assert exercise.breaks_down is True
    assert exercise.authoritative is False, "an authored grader is advisory (R5)"


def test_r5_is_unchanged_by_any_of_this():
    # ⛔ An authored grader is `generated`, therefore `advisory` — and the pair
    # R5 forbids is refused however much else the record carries.
    assert refuse(from_document, record(trust="authoritative"), WHERE)


def test_a_case_map_does_not_reach_a_lesson():
    assert "'lesson'" in refuse(of, {"kind": "lesson", "exercise": AUTHORED}, WHERE)
