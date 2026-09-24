"""The per-case verdicts: folding a run's JUnit report through the record's cases.

⭐ **The five clauses are five separate readings**, each with its own test: a
report folds to *main* plus *edge n/m*; a test the case map does not name is
refused rather than counted; a stale report is refused and never read; a
malformed report is a named failure; and a run that wrote no report yields no
breakdown and no error.

⛔ **The stale clause is a claim about TIME, so it is not asserted about.** The
report is written and then MADE older than the run — `os.utime`, an hour back —
and the plant is observed with `stat` before the fold is asked for anything. The
stale file's own bytes are then garbage, so a fold that read it would fail as
*malformed*: the refusal naming staleness is what proves it was never read.

⚠️ **No fixture is added and none is modified.** Every report here is written
into `tmp_path` by the test that reads it, because a report is a thing a RUN
leaves behind — a committed one is exactly what the stale clause refuses.
"""

import os
import time
from dataclasses import replace
from pathlib import Path

import pytest

from studyforge.exercise import (
    CLOCK_SLACK,
    EDGE,
    JUNIT,
    MAIN,
    PASSING_CHILDREN,
    REPORT_ROOTS,
    REPORT_SUFFIX,
    Breakdown,
    ExerciseError,
    breakdown_of,
    from_document,
)

WHERE = "iso/02-parsing/unit-02/practice-1"

#: The ids as surefire spells them, which is what the corpus writes down.
ASK = "com.example.ParserTest#parsesTheMti"
SHORT = "com.example.ParserTest#refusesAShortMessage"
EMPTY = "com.example.ParserTest#refusesAnEmptyMessage"

SAYS = {
    ASK: "It reads the MTI.",
    SHORT: "A message shorter than its header is refused.",
    EMPTY: "An empty message is refused.",
}

#: Surefire writes a directory of XML; pytest writes one file. Both are
#: declared the same way, and which one it is is read off the disk.
DIRECTORY = "practice/iso-02/target/surefire-reports"
ONE_FILE = "practice/iso-02/report.xml"

GRADED = {
    "main_path": "practice/iso-02/src/main/java/Parser.java",
    "run_command": ["mvn", "-q", "-pl", "practice/iso-02", "compile"],
    "test_path": "practice/iso-02/src/test/java/ParserTest.java",
    "test_command": ["mvn", "-q", "-pl", "practice/iso-02", "test"],
    "provenance": "generated",
    "trust": "advisory",
}

CASES = [
    {"id": ASK, "kind": MAIN, "says": SAYS[ASK]},
    {"id": SHORT, "kind": EDGE, "says": SAYS[SHORT]},
    {"id": EMPTY, "kind": EDGE, "says": SAYS[EMPTY]},
]

PASS = ""
FAILURE = '<failure message="expected 0200" type="java.lang.AssertionError">ParserTest:31</failure>'
ERROR = '<error message="no message" type="java.lang.NullPointerException">ParserTest:9</error>'
SKIPPED = "<skipped/>"

#: ⛔ A verdict element this build has never seen. Surefire writes it for a
#: test that failed and then passed on a rerun.
RERUN = '<rerunFailure message="flaked">ParserTest:31</rerunFailure>'


def exercise(*, path=DIRECTORY, cases=None):
    """The authored record, graded, with a breakdown pointing at `path`."""
    document = {
        **GRADED,
        "cases": CASES if cases is None else cases,
        "report": {"format": JUNIT, "path": path},
    }
    return from_document(document, WHERE)


def surefire(*results: tuple[str, str]) -> str:
    """One `testsuite` document, spelling each id the way surefire does."""
    cases = []
    for identifier, body in results:
        classname, _, name = identifier.partition("#")
        cases.append(f'  <testcase classname="{classname}" name="{name}">{body}</testcase>')
    inner = "\n".join(cases)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<testsuite name="com.example.ParserTest" tests="{len(results)}">\n{inner}\n</testsuite>\n'
    )


def written(root: Path, declared: str, text: str, name: str = "TEST-ParserTest.xml") -> Path:
    """Write a report where the record says one lands, and return the file."""
    target = root / declared
    if declared.endswith(REPORT_SUFFIX):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target
    target.mkdir(parents=True, exist_ok=True)
    path = target / name
    path.write_text(text, encoding="utf-8")
    return path


def run(root: Path, text: str, declared: str = DIRECTORY, **changes) -> Breakdown | None:
    """Start a run, let it write `text` as its report, and fold what it wrote."""
    started = time.time()
    written(root, declared, text)
    return breakdown_of(exercise(path=declared, **changes), root, WHERE, started=started)


def refuse(root: Path, text: str, declared: str = DIRECTORY, **changes) -> str:
    """The sentence a fold of `text` refuses with."""
    with pytest.raises(ExerciseError) as raised:
        run(root, text, declared, **changes)
    return str(raised.value)


# --------------------------------------------------------------------------
# ⭐ A report folds to main plus edge n/m
# --------------------------------------------------------------------------


def test_a_report_folds_to_the_main_ask_plus_edge_cases_n_of_m(tmp_path):
    breakdown = run(tmp_path, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS)))
    assert breakdown is not None
    assert breakdown.ask is True
    assert (breakdown.edges_passed, breakdown.edges_total) == (2, 2)
    assert breakdown.failed_edges == ()
    assert breakdown.complete is True


def test_a_failed_edge_is_named_by_what_the_corpus_says_about_it(tmp_path):
    breakdown = run(tmp_path, surefire((ASK, PASS), (SHORT, FAILURE), (EMPTY, PASS)))
    assert breakdown.ask is True
    assert (breakdown.edges_passed, breakdown.edges_total) == (1, 2)
    assert breakdown.failed_edges == (SAYS[SHORT],)
    assert breakdown.complete is False


def test_the_failed_edges_are_named_in_the_order_the_corpus_wrote_them(tmp_path):
    breakdown = run(tmp_path, surefire((ASK, PASS), (EMPTY, FAILURE), (SHORT, ERROR)))
    assert breakdown.failed_edges == (SAYS[SHORT], SAYS[EMPTY])


def test_a_failed_main_ask_is_not_counted_among_the_edges(tmp_path):
    breakdown = run(tmp_path, surefire((ASK, FAILURE), (SHORT, PASS), (EMPTY, PASS)))
    assert breakdown.ask is False
    assert (breakdown.edges_passed, breakdown.edges_total) == (2, 2)
    assert breakdown.failed_edges == ()
    assert breakdown.complete is False


def test_a_report_pytest_wrote_folds_by_the_node_id_it_spells(tmp_path):
    """⚠️ The other runner: one file, and ids that are node ids rather than `Class#method`."""
    node = "tests/test_parser.py::TestParser::test_reads_the_mti"
    cases = [{"id": node, "kind": MAIN, "says": SAYS[ASK]}]
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<testsuites><testsuite name="pytest" tests="1">'
        '<testcase classname="tests.test_parser.TestParser" file="tests/test_parser.py" '
        'name="test_reads_the_mti" line="11" time="0.01"/>'
        "</testsuite></testsuites>\n"
    )
    breakdown = run(tmp_path, document, ONE_FILE, cases=cases)
    assert breakdown.ask is True
    assert breakdown.edges_total == 0


def test_a_runner_that_reports_neither_a_file_nor_a_class_is_read_by_the_bare_name(tmp_path):
    cases = [{"id": "parsesTheMti", "kind": MAIN, "says": SAYS[ASK]}]
    document = '<testsuite name="s" tests="1"><testcase name="parsesTheMti"/></testsuite>\n'
    assert run(tmp_path, document, ONE_FILE, cases=cases).ask is True


def test_a_case_the_report_never_names_did_not_pass(tmp_path):
    """⚠️ A run that stops early names fewer tests, and a case with no result is not one
    that passed."""
    breakdown = run(tmp_path, surefire((ASK, PASS)))
    assert breakdown.ask is True
    assert (breakdown.edges_passed, breakdown.edges_total) == (0, 2)
    assert breakdown.failed_edges == (SAYS[SHORT], SAYS[EMPTY])


def test_a_directory_of_report_files_folds_as_one_run(tmp_path):
    started = time.time()
    written(tmp_path, DIRECTORY, surefire((ASK, PASS)), "TEST-A.xml")
    written(tmp_path, DIRECTORY, surefire((SHORT, PASS), (EMPTY, FAILURE)), "TEST-B.xml")
    breakdown = breakdown_of(exercise(), tmp_path, WHERE, started=started)
    assert breakdown.ask is True
    assert breakdown.failed_edges == (SAYS[EMPTY],)


def test_a_case_that_failed_in_any_file_did_not_pass(tmp_path):
    """⛔ A rerun that also reported a pass does not turn a failure into one."""
    started = time.time()
    written(tmp_path, DIRECTORY, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS)), "TEST-A.xml")
    written(tmp_path, DIRECTORY, surefire((SHORT, FAILURE)), "TEST-B.xml")
    breakdown = breakdown_of(exercise(), tmp_path, WHERE, started=started)
    assert breakdown.failed_edges == (SAYS[SHORT],)


# --------------------------------------------------------------------------
# ⭐ A test the case map does not name is refused
# --------------------------------------------------------------------------


def test_a_test_the_case_map_does_not_name_is_refused_rather_than_counted(tmp_path):
    stranger = "com.example.OtherTest#somethingElse"
    report = surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS), (stranger, PASS))
    message = refuse(tmp_path, report)
    assert "'cases' does not" in message
    assert DIRECTORY in message
    assert stranger not in message and "somethingElse" not in message


def test_the_unnamed_test_is_refused_even_where_every_named_case_passed(tmp_path):
    """⛔ The silent alternative is what this refuses: three greens and a result dropped."""
    stranger = "com.example.ParserTest#parsesTheBitmap"
    with pytest.raises(ExerciseError):
        run(tmp_path, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS), (stranger, PASS)))


def test_one_test_that_two_cases_each_claim_is_refused(tmp_path):
    """⚠️ The other direction: two spellings of one element, both declared."""
    cases = [
        {"id": "tests/test_parser.py::test_reads", "kind": MAIN, "says": SAYS[ASK]},
        {"id": "test_reads", "kind": EDGE, "says": SAYS[SHORT]},
    ]
    document = (
        '<testsuite name="pytest" tests="1"><testcase classname="tests.test_parser" '
        'file="tests/test_parser.py" name="test_reads"/></testsuite>\n'
    )
    message = refuse(tmp_path, document, ONE_FILE, cases=cases)
    assert "no result can be attributed" in message
    assert "test_reads" not in message


# --------------------------------------------------------------------------
# ⛔ A stale report is refused, and never read
# --------------------------------------------------------------------------


def age(path: Path, seconds: float) -> None:
    """Make `path` genuinely `seconds` older than it is — ⛔ the plant, not an assertion."""
    when = path.stat().st_mtime - seconds
    os.utime(path, (when, when))


def test_a_stale_report_is_refused_and_never_read(tmp_path):
    """⛔ The file is MADE an hour old, and its bytes would fail as malformed if read."""
    started = time.time()
    path = written(tmp_path, DIRECTORY, "this is not XML at all <<<")
    age(path, 3600)

    assert path.stat().st_mtime < started - CLOCK_SLACK, "the plant did not take"

    with pytest.raises(ExerciseError) as raised:
        breakdown_of(exercise(), tmp_path, WHERE, started=started)
    message = str(raised.value)
    assert "older than the run" in message
    assert "well-formed" not in message, "the stale report was parsed"
    assert DIRECTORY in message


def test_a_stale_report_is_refused_even_where_it_would_have_folded(tmp_path):
    started = time.time()
    path = written(tmp_path, DIRECTORY, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS)))
    age(path, 3600)

    assert path.stat().st_mtime < started - CLOCK_SLACK, "the plant did not take"

    with pytest.raises(ExerciseError, match="older than the run"):
        breakdown_of(exercise(), tmp_path, WHERE, started=started)


def test_one_stale_file_refuses_the_whole_directory(tmp_path):
    """⛔ Surefire does not always clean: a leftover beside fresh files is the real shape."""
    started = time.time()
    written(tmp_path, DIRECTORY, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS)), "TEST-A.xml")
    left = written(tmp_path, DIRECTORY, surefire((ASK, FAILURE)), "TEST-B.xml")
    age(left, 3600)

    assert left.stat().st_mtime < started - CLOCK_SLACK, "the plant did not take"

    with pytest.raises(ExerciseError, match="older than the run"):
        breakdown_of(exercise(), tmp_path, WHERE, started=started)


def test_a_report_written_inside_the_clock_slack_is_not_stale(tmp_path):
    """⚠️ `CLOCK_SLACK` is for a coarse filesystem clock, and this is the reading that says so."""
    started = time.time()
    path = written(tmp_path, DIRECTORY, surefire((ASK, PASS), (SHORT, PASS), (EMPTY, PASS)))
    age(path, CLOCK_SLACK / 2)

    assert path.stat().st_mtime < started, "the plant did not take"

    assert breakdown_of(exercise(), tmp_path, WHERE, started=started).complete is True


# --------------------------------------------------------------------------
# ⛔ A malformed report is a named failure
# --------------------------------------------------------------------------


def test_a_malformed_report_is_a_named_failure(tmp_path):
    message = refuse(tmp_path, '<testsuite name="s"><testcase name="x">')
    assert "is not well-formed XML" in message
    assert f"{DIRECTORY}/TEST-ParserTest.xml" in message
    assert "line" in message and "column" in message


def test_a_malformed_report_is_not_an_empty_breakdown(tmp_path):
    with pytest.raises(ExerciseError):
        run(tmp_path, "")


def test_a_document_that_is_well_formed_and_is_not_a_report_is_a_named_failure(tmp_path):
    message = refuse(tmp_path, "<html><body><p>surefire wrote nothing</p></body></html>")
    assert f"its root element is not one of {list(REPORT_ROOTS)}" in message
    assert "html" not in message


def test_a_testcase_that_names_no_test_is_a_named_failure(tmp_path):
    message = refuse(tmp_path, '<testsuite name="s" tests="1"><testcase time="0.1"/></testsuite>')
    assert "carries a testcase with no 'name'" in message


# --------------------------------------------------------------------------
# ⭐ A run that wrote no report is no breakdown and no error
# --------------------------------------------------------------------------


def test_a_run_that_wrote_no_report_yields_no_breakdown_and_no_error(tmp_path):
    assert breakdown_of(exercise(), tmp_path, WHERE, started=time.time()) is None


def test_a_report_directory_the_run_left_empty_is_a_run_that_wrote_no_report(tmp_path):
    (tmp_path / DIRECTORY).mkdir(parents=True)
    assert breakdown_of(exercise(), tmp_path, WHERE, started=time.time()) is None


def test_a_record_that_declares_no_breakdown_yields_no_breakdown_and_no_error(tmp_path):
    plain = from_document(GRADED, WHERE)
    assert plain.breaks_down is False
    assert breakdown_of(plain, tmp_path, WHERE, started=time.time()) is None


def test_an_ungraded_record_yields_no_breakdown_and_no_error(tmp_path):
    ungraded = from_document(
        {"main_path": GRADED["main_path"], "run_command": GRADED["run_command"]}, WHERE
    )
    assert breakdown_of(ungraded, tmp_path, WHERE, started=time.time()) is None


# --------------------------------------------------------------------------
# ⭐ a case passes only if the report says so
# --------------------------------------------------------------------------


@pytest.mark.parametrize("body", [FAILURE, ERROR, SKIPPED, RERUN])
def test_a_case_the_report_did_not_report_a_pass_for_did_not_pass(tmp_path, body):
    """⛔ Including `rerunFailure`, which is the verdict element this build has never seen."""
    breakdown = run(tmp_path, surefire((ASK, PASS), (SHORT, body), (EMPTY, PASS)))
    assert breakdown.failed_edges == (SAYS[SHORT],)


@pytest.mark.parametrize("child", PASSING_CHILDREN)
def test_a_child_that_is_not_a_verdict_leaves_the_pass_alone(tmp_path, child):
    body = f"<{child}>whatever the runner attached</{child}>"
    assert run(tmp_path, surefire((ASK, body), (SHORT, PASS), (EMPTY, PASS))).complete is True


def test_a_format_this_build_cannot_read_is_refused(tmp_path):
    """⛔ The set is closed at one, so the unforeseen format is refused rather than guessed at."""
    record = exercise()
    other = replace(record, report=replace(record.report, format="console"))
    written(tmp_path, DIRECTORY, surefire((ASK, PASS)))
    with pytest.raises(ExerciseError, match="reads 'junit' reports"):
        breakdown_of(other, tmp_path, WHERE, started=time.time() - 60)


def test_a_breakdown_answers_per_case_for_whoever_records_it(tmp_path):
    """⭐ The breakdown is recorded, so it reads the cases and their verdicts, not the prose."""
    breakdown = run(tmp_path, surefire((ASK, PASS), (SHORT, FAILURE), (EMPTY, PASS)))
    assert tuple(case.id for case in breakdown.cases) == (ASK, SHORT, EMPTY)
    assert tuple(breakdown.passed(case) for case in breakdown.cases) == (True, False, True)
    assert tuple(case.id for case in breakdown.edges) == (SHORT, EMPTY)
