"""Mirror of `src/studyforge/exercise/casedetail.py` (R12): what a report says of each case.

⭐ **Every report is written under `tmp_path` by the test that reads it**, in the three shapes the
course's test
tools write: pytest (output and log per `<testcase>`), the Gradle/JUnit shape (one suite-level
`<system-err>` whose
log lines name their test) and Node's (a `<testsuites>` root with output at its level).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from studyforge.exercise import ExerciseError, from_document
from studyforge.exercise.casedetail import CASE_LINES, MAX_BYTES, MAX_LINES, detail_of

DECLARED = "reports/r.xml"
WHERE = "this test's record"


def record(*names: str) -> object:
    cases = [
        {"id": name, "kind": "main" if at == 0 else "edge", "says": f"says {name}"}
        for at, name in enumerate(names)
    ]
    return from_document(
        {
            "main_path": "practice/a.py",
            "run_command": ["python3", "a.py"],
            "test_path": "practice/t.py",
            "test_command": ["python3", "-m", "pytest", "practice/t.py"],
            "provenance": "bundled",
            "trust": "authoritative",
            "cases": cases,
            "report": {"format": "junit", "path": DECLARED},
        },
        WHERE,
    )


def report(root: Path, body: str, top: str = "testsuite") -> None:
    path = root / DECLARED
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"<{top}>{body}</{top}>", encoding="utf-8")


def read(root: Path, *names: str):
    return detail_of(record(*names), root, WHERE, started=time.time() - 5)


PYTEST_CASE = (
    '<testcase classname="t" name="m1">'
    '<failure message="AssertionError: assert 1 == 2">trace</failure>'
    "<system-out>{out}</system-out></testcase>"
    '<testcase classname="t" name="e1"/>'
)


def test_pytest_sections_split_the_log_from_what_was_printed(tmp_path):
    out = (
        "-------- Captured Log --------\n[log] DEBUG mod: input spec=1\n[log] INFO mod: second\n"
        "-------- Captured Out --------\nprinted line\n"
    )
    report(tmp_path, PYTEST_CASE.format(out=out), "testsuites")
    found = read(tmp_path, "m1", "e1")
    first, second = found.cases
    assert first.passed is False and first.message == "AssertionError: assert 1 == 2"
    assert first.log == ("DEBUG mod: input spec=1", "INFO mod: second")
    assert first.out == ("printed line",)
    assert second.passed is True and second.message == "" and second.log == ()
    assert found.per_case_out is True


def test_suite_level_log_lines_go_to_the_case_whose_name_they_carry(tmp_path):
    body = (
        '<testcase classname="T" name="m1()">'
        '<failure message="expected: &lt;a&gt; but was: &lt;b&gt;"/></testcase>'
        '<testcase classname="T" name="e1()"/>'
        "<system-out>printed once</system-out>"
        "<system-err>[log:e1()] DEBUG Foo: edge input\n[log:m1()] DEBUG Foo: main input\n"
        "[log:] DEBUG x: unowned\n</system-err>"
    )
    report(tmp_path, body)
    found = read(tmp_path, "m1()", "e1()")
    assert found.cases[0].log == ("DEBUG Foo: main input",)
    assert found.cases[1].log == ("DEBUG Foo: edge input",)
    assert found.cases[0].message == "expected: <a> but was: <b>"
    # ⭐ A line no case owns, and printed text this tool records once, stay with the whole run.
    assert found.log == ("DEBUG x: unowned",)
    assert found.out == ("printed once",)
    assert found.per_case_out is False


def test_a_testsuites_root_carries_its_own_output(tmp_path):
    body = (
        '<testcase classname="test" name="m1"/>'
        "<system-out>[log:m1] DEBUG p: hello\nplain\n</system-out>"
    )
    report(tmp_path, body, "testsuites")
    found = read(tmp_path, "m1")
    assert found.cases[0].log == ("DEBUG p: hello",)
    assert found.out == ("plain",)


def test_an_older_report_gives_messages_and_nothing_else(tmp_path):
    body = '<testcase name="m1"><failure message="boom"/></testcase><testcase name="e1"/>'
    report(tmp_path, body)
    found = read(tmp_path, "m1", "e1")
    assert [c.message for c in found.cases] == ["boom", ""]
    assert all(not (c.log or c.out or c.err) for c in found.cases)
    assert (found.log, found.out, found.err, found.truncated) == ((), (), (), False)


def test_what_is_kept_is_bounded_and_says_it_was_cut(tmp_path):
    lines = "\n".join(f"[log] INFO m: line {n}" for n in range(500))
    report(tmp_path, f'<testcase name="m1"><system-out>{lines}</system-out></testcase>')
    found = read(tmp_path, "m1")
    kept = found.cases[0].log
    assert len(kept) == CASE_LINES <= MAX_LINES
    assert kept[-1] == "INFO m: line 499"  # the last lines are the ones kept
    assert found.truncated is True


def test_the_byte_budget_holds_over_the_whole_run(tmp_path):
    big = "x" * 4000
    body = "".join(
        f'<testcase name="c{n}"><system-out>[log] INFO m: {big}\n[log] INFO m: {big}'
        "</system-out></testcase>"
        for n in range(8)
    )
    report(tmp_path, body)
    found = read(tmp_path, *[f"c{n}" for n in range(8)])
    total = sum(len(line.encode()) + 1 for c in found.cases for line in c.log)
    assert total <= MAX_BYTES and found.truncated is True


def test_a_marked_line_is_never_filed_as_printed_text(tmp_path):
    # ⛔ The two stay apart: debug logging must never be mistaken for output a practice grades.
    body = '<testcase name="m1"><system-out>[log] DEBUG m: a\nprinted</system-out></testcase>'
    report(tmp_path, body)
    case = read(tmp_path, "m1").cases[0]
    assert "DEBUG m: a" in case.log and "DEBUG m: a" not in case.out and case.out == ("printed",)


def test_no_report_is_no_detail_and_a_stale_one_is_refused(tmp_path):
    assert read(tmp_path, "m1") is None
    report(tmp_path, '<testcase name="m1"/>')
    with pytest.raises(ExerciseError):
        detail_of(record("m1"), tmp_path, WHERE, started=time.time() + 3600)


def test_a_test_no_case_names_is_refused_as_the_fold_refuses_it(tmp_path):
    report(tmp_path, '<testcase name="stranger"/>')
    with pytest.raises(ExerciseError):
        read(tmp_path, "m1")
