"""A case id may carry ONE interior space, and everything that touches an id still holds.

⭐ **The widening, read as a table** — every id valid before is valid now and every
refusal before is a refusal now — and then **every place that prints, splits or
compares an id** gets one test with a spaced id in it: the case map, the report
fold, the gate role, the panel, the stream line and its parser, the progress
record, and the plant's directory. ⛔ The gates G1 to G5 are read over real
`pytest` runs of an exercise whose ids are spelled with spaces.
"""

from __future__ import annotations

import re
import time
from dataclasses import replace
from pathlib import Path

import pytest

from studyforge.exercise import (
    EDGE,
    MAIN,
    Case,
    ExerciseError,
    breakdown_of,
    cases_document,
    cases_of,
    from_document,
)
from studyforge.exercise.bundle.layout import plant_dirname, plant_positions
from studyforge.exercise.cases import CASE_ID
from studyforge.exercise.gates import G1, G2, G3, G4, G5, plant_role, require_role
from studyforge.exercise.gates.runs import FIRST, STARTER
from studyforge.progress.document import next_entry
from studyforge.serve.routes.breakdown import CASE_LINE, fold, said
from tests.studyforge.exercise.gates.workspace import (
    EMPTY_EDGE,
    NEGATIVE_EDGE,
    NONE,
    VACUOUS_TEST,
    Bundle,
)
from tests.studyforge.render.page.test_practice import GENERATED, panel, section

WHERE = "iso/02-parsing/unit-02/practice-1"

#: What Gradle writes for a parameterised test, and a backticked Kotlin sentence.
PARAMETERISED = "practice.ParamTest#adds(int, int, int)"
SENTENCE = "practice.SentenceTest#an empty basket totals zero"


def case(cid: str, kind: str = MAIN) -> dict:
    return {"id": cid, "kind": kind, "says": "one sentence"}


def refused(call, *args) -> str:
    with pytest.raises(ExerciseError) as raised:
        call(*args)
    return str(raised.value)


# --------------------------------------------------------------------------
# Item 1 and 2: the pattern, as a table of accepted and refused values
# --------------------------------------------------------------------------

#: ⭐ Every spelling the existing tests and corpus use, and each stays valid.
TODAY_ACCEPTED = [
    "com.example.ParserTest#parsesTheMti",
    "tests/test_parser.py::test_parses_the_mti",
    "ParserTest.parses[1]",
    "ParserTest.adds(int,int)",
    "suite:parser+edge",
    "m",
    "m()",
    "a$b@c=d,e",
]

#: ⛔ Every refusal of today, each stays one.
TODAY_REFUSED = ["", "   ", " ", "a\ttest", "Test#x\n", "café", "a;b", "a|b", "a b", "a\nb"]

NEWLY_ACCEPTED = [
    "adds(int, int, int)",
    PARAMETERISED,
    SENTENCE,
    "a b",
    "a b c d",
    "test_x[an empty list]",
]

STILL_REFUSED = [
    " a",  # leading
    "a ",  # trailing
    "a  b",  # two in a row
    "a   b",
    " ",
    "a b ",
    " a b",
    "a\tb",  # tab
    "a b\n",  # newline, the `$` hazard
    "a\nb",
    "a\r\nb",
    "a b",  # not an ASCII space
    "a b",
]


@pytest.mark.parametrize("spelling", TODAY_ACCEPTED + NEWLY_ACCEPTED)
def test_an_id_with_at_most_single_interior_spaces_is_accepted(spelling):
    assert CASE_ID.match(spelling)
    assert cases_of([case(spelling)], WHERE)[0].id == spelling


@pytest.mark.parametrize("spelling", TODAY_REFUSED + STILL_REFUSED)
def test_every_other_id_is_refused_and_the_refusal_is_not_the_value(spelling):
    message = refused(cases_of, [case(spelling)], WHERE)
    assert "id" in message


# --------------------------------------------------------------------------
# The case map round-trips a spaced id
# --------------------------------------------------------------------------


def test_the_case_map_round_trips_a_spaced_id_in_its_written_order():
    written = [case(SENTENCE), case(PARAMETERISED, EDGE)]
    assert cases_document(cases_of(written, WHERE)) == written


def test_a_spaced_id_repeated_is_still_a_repeated_id():
    message = refused(cases_of, [case(PARAMETERISED), case(PARAMETERISED, EDGE)], WHERE)
    assert "more than once" in message


# --------------------------------------------------------------------------
# Item 4: the report fold
# --------------------------------------------------------------------------

DIRECTORY = "practice/target/test-results/test"

GRADED = {
    "main_path": "practice/src/main/kotlin/Calc.kt",
    "run_command": ["gradle", "-q", "run"],
    "test_path": "practice/src/test/kotlin/ParamTest.kt",
    "test_command": ["gradle", "-q", "test"],
    "provenance": "generated",
    "trust": "advisory",
}


def exercise(cases):
    return from_document(
        {**GRADED, "cases": cases, "report": {"format": "junit", "path": DIRECTORY}}, WHERE
    )


def junit(*tests: tuple[str, str, str]) -> str:
    rows = "\n".join(
        f'  <testcase classname="{owner}" name="{name}">{body}</testcase>'
        for owner, name, body in tests
    )
    head = f'<testsuite name="s" tests="{len(tests)}">'
    return f'<?xml version="1.0"?>\n{head}\n{rows}\n</testsuite>\n'


def fold_report(root: Path, text: str, cases) -> object:
    started = time.time()
    target = root / DIRECTORY
    target.mkdir(parents=True, exist_ok=True)
    (target / "TEST-practice.xml").write_text(text, encoding="utf-8")
    return breakdown_of(exercise(cases), root, WHERE, started=started)


def test_a_test_named_with_its_parameter_types_folds_to_the_id_the_map_names(tmp_path):
    cases = [case(PARAMETERISED), case(SENTENCE, EDGE)]
    report = junit(
        ("practice.ParamTest", "adds(int, int, int)", ""),
        ("practice.SentenceTest", "an empty basket totals zero", ""),
    )
    folded = fold_report(tmp_path, report, cases)
    assert folded.ask is True and (folded.edges_passed, folded.edges_total) == (1, 1)


def test_a_failed_spaced_edge_is_named_and_the_ask_is_not_counted_among_the_edges(tmp_path):
    cases = [case(PARAMETERISED), case(SENTENCE, EDGE)]
    report = junit(
        ("practice.ParamTest", "adds(int, int, int)", ""),
        ("practice.SentenceTest", "an empty basket totals zero", "<failure/>"),
    )
    folded = fold_report(tmp_path, report, cases)
    assert folded.ask is True and folded.edges_passed == 0
    assert folded.failed_edges == ("one sentence",)


def test_a_bare_spaced_name_is_read_by_its_bare_spelling(tmp_path):
    cases = [case("adds(int, int, int)")]
    folded = fold_report(tmp_path, junit(("practice.ParamTest", "adds(int, int, int)", "")), cases)
    assert folded.ask is True


def test_the_space_is_compared_byte_for_byte_and_never_repaired(tmp_path):
    # ⛔ One space in the id against two in the report is a different test.
    cases = [case("adds(int, int, int)")]
    with pytest.raises(ExerciseError, match="does not"):
        fold_report(tmp_path, junit(("practice.ParamTest", "adds(int,  int, int)", "")), cases)


def test_an_unnamed_test_is_still_refused_beside_a_spaced_one(tmp_path):
    cases = [case(PARAMETERISED)]
    report = junit(
        ("practice.ParamTest", "adds(int, int, int)", ""),
        ("practice.ParamTest", "subtracts(int, int, int)", ""),
    )
    with pytest.raises(ExerciseError, match="'cases' does not"):
        fold_report(tmp_path, report, cases)


def test_a_testcase_with_no_name_is_still_refused(tmp_path):
    cases = [case(PARAMETERISED)]
    with pytest.raises(ExerciseError, match="no 'name'"):
        fold_report(tmp_path, junit(("practice.ParamTest", "", "")), cases)


# --------------------------------------------------------------------------
# Item 3: every place that prints, splits or compares an id
# --------------------------------------------------------------------------


def test_the_gate_role_of_a_spaced_plant_is_one_the_record_can_carry():
    role = plant_role(Case(id=PARAMETERISED, kind=EDGE, says="s"))
    assert role == f"plant:{PARAMETERISED}"
    assert require_role(role, WHERE) == role


@pytest.mark.parametrize(
    "role",
    [
        "has space",  # the role set outside a plant stays whitespace-free
        "question:a b",
        "plant: a",
        "plant:a ",
        "plant:a  b",
        "plant:a\tb",
        "plant:a\nb",
    ],
)
def test_no_other_role_gains_a_space(role):
    with pytest.raises(ExerciseError, match="names what the file is"):
        require_role(role, WHERE)


def test_the_panel_carries_a_spaced_id_whole_in_its_attribute():
    workspace = {
        **GENERATED,
        "cases": [case(PARAMETERISED), case(SENTENCE, EDGE)],
        "report": {"format": "junit", "path": "reports"},
        "origin": {"path": "basics/01.md", "section": "What a class is"},
    }
    drawn = panel(sections=[section(workspace=workspace)])
    assert f'data-practice-case="{PARAMETERISED}"' in drawn
    assert f'data-practice-case="{SENTENCE}"' in drawn


def test_the_stream_line_says_a_spaced_id_unscathed_and_the_panel_s_parser_reads_it_back():
    # ⭐ The panel's own regular expression is read out of the shipped script, so
    # a change to either side that stops them meeting turns this red.
    script = (Path(__file__).parents[3] / "src/studyforge/render/assets/practice.js").read_text(
        encoding="utf-8"
    )
    source = re.search(r"var CASE_LINE = /(.+)/;", script)
    assert source is not None
    parser = re.compile(source.group(1))
    for passed in (True, False):
        line = said(PARAMETERISED, passed)
        assert line == CASE_LINE.format(id=PARAMETERISED, verdict="passed" if passed else "failed")
        found = parser.match(line)
        assert found is not None and found.group(1) == PARAMETERISED
        assert (found.group(2) == "passed") is passed


def test_the_run_fold_records_a_spaced_id_as_a_key_and_says_it(tmp_path):
    started = time.time()
    target = tmp_path / DIRECTORY
    target.mkdir(parents=True)
    (target / "TEST-practice.xml").write_text(
        junit(("practice.ParamTest", "adds(int, int, int)", "")), encoding="utf-8"
    )
    workspace = {**GRADED, "cases": [case("adds(int, int, int)")]}
    workspace["report"] = {"format": "junit", "path": DIRECTORY}
    verdicts, lines = fold("test", workspace, tmp_path, started)
    assert verdicts == {"adds(int, int, int)": True}
    assert lines == ("--- case adds(int, int, int): passed ---",)


def test_the_progress_record_keeps_a_spaced_id_as_its_key():
    entry = next_entry(
        None,
        mode="test",
        exit_code=0,
        commands=["gradle test"],
        when="2026-01-01T00:00:00Z",
        cases={PARAMETERISED: True},
    )
    assert entry["last"]["cases"] == {PARAMETERISED: True}


def test_a_plant_is_filed_by_ordinal_so_a_spaced_id_never_reaches_a_path():
    cases = cases_of([case(SENTENCE), case(PARAMETERISED, EDGE)], WHERE)
    positions = plant_positions(cases)
    assert positions == {PARAMETERISED: 1}
    assert plant_dirname(positions[PARAMETERISED]) == "edge-1"
    assert " " not in plant_dirname(1)


def test_a_spaced_id_is_never_a_token_of_the_test_command():
    # ⛔ argv: the record's commands are authored, whole-token lists; an id is
    # data beside them and is never spliced into one.
    record = exercise([case(PARAMETERISED)])
    assert all(PARAMETERISED not in part and " " not in part for part in record.test_command)


# --------------------------------------------------------------------------
# G1 to G5, over real runs of an exercise whose ids carry a space
# --------------------------------------------------------------------------

MAIN_SPACED = Case(id="test_total[totals a list]", kind=MAIN, says="a basket adds up")
EMPTY_SPACED = Case(id="test_total_empty[an empty list]", kind=EDGE, says="an empty basket is zero")
NEGATIVE_SPACED = Case(
    id="test_total_negative[a negative price]", kind=EDGE, says="a negative is refused"
)

SPACED_CASES = (MAIN_SPACED, EMPTY_SPACED, NEGATIVE_SPACED)

SPACED_TESTS = """import pytest
from solution import total


@pytest.mark.parametrize("prices, want", [([2, 3, 5], 10)], ids=["totals a list"])
def test_total(prices, want):
    assert total(prices) == want


@pytest.mark.parametrize("prices, want", [([], 0)], ids=["an empty list"])
def test_total_empty(prices, want):
    assert total(prices) == want


@pytest.mark.parametrize("prices, want", [([2, -1], None)], ids=["a negative price"])
def test_total_negative(prices, want):
    try:
        total(prices)
    except ValueError:
        return
    raise AssertionError("a negative price should have been refused")
"""


class SpacedBundle(Bundle):
    """The gates' real exercise, with every case id spelled the way pytest spells a parameter."""

    @property
    def exercise(self):
        return replace(Bundle.exercise.fget(self), cases=SPACED_CASES)

    @property
    def files(self):
        renamed = {
            plant_role(EMPTY_EDGE): plant_role(EMPTY_SPACED),
            plant_role(NEGATIVE_EDGE): plant_role(NEGATIVE_SPACED),
        }
        return tuple((renamed.get(role, role), path) for role, path in Bundle.files.fget(self))

    def _solutions(self):
        plain = Bundle._solutions(self)
        return {
            "reference": plain["reference"],
            "starter": plain["starter"],
            plant_role(EMPTY_SPACED): plain[plant_role(EMPTY_EDGE)],
            plant_role(NEGATIVE_SPACED): plain[plant_role(NEGATIVE_EDGE)],
        }

    def _tests(self):
        if self.plant == VACUOUS_TEST:
            return SPACED_TESTS.replace(
                "def test_total(prices, want):\n    assert total(prices) == want",
                "def test_total(prices, want):\n    assert True",
            )
        return SPACED_TESTS


@pytest.fixture(scope="module")
def spaced_clean(tmp_path_factory):
    return SpacedBundle(tmp_path_factory.mktemp("spaced")).read()


def test_the_spaced_control_clears_every_gate_off_real_runs(spaced_clean):
    assert all(" " in case.id for case in SPACED_CASES)
    assert spaced_clean.refused() == ()
    assert [verdict.id for verdict in spaced_clean.verdicts] == [G1, G2, G3, G4, G5]
    assert all(run.reported for run in spaced_clean.evidence.runs)
    roles = [run.role for run in spaced_clean.evidence.runs]
    assert f"plant:{EMPTY_SPACED.id}" in roles and " " in EMPTY_SPACED.id


def test_a_vacuous_spaced_main_test_is_refused_by_g2_naming_it(tmp_path):
    reading = SpacedBundle(tmp_path, VACUOUS_TEST).read()
    assert reading.evidence.of(STARTER, FIRST).passed(MAIN_SPACED)
    assert reading.refused() == (G2,)
    assert MAIN_SPACED.says in reading.verdict(G2).says


def test_the_unplanted_spaced_bundle_is_the_control_for_the_plant_above(tmp_path):
    assert SpacedBundle(tmp_path, NONE).read().refused() == ()
