"""Mirror of `src/studyforge/exercise/spelling.py` (R12): which id a testcase spells, and
whether an assertion failed it.

⭐ Each element below is the shape a real runner wrote (pytest's default family with no `file`
attribute, pytest's older family with one, surefire and Gradle's `type`), and the whole-report
reading over a real pytest run is `skills/exercises/test_pytest_practice.py`.
"""

from __future__ import annotations

from xml.etree import ElementTree

import pytest

from studyforge.exercise.report import PASSING_CHILDREN
from studyforge.exercise.spelling import asserted, file_level_failure, spells


def case(**attributes) -> ElementTree.Element:
    return ElementTree.Element("testcase", attributes)


def failing(tag: str = "failure", **attributes) -> ElementTree.Element:
    element = case(name="t")
    ElementTree.SubElement(element, tag, attributes)
    return element


@pytest.mark.parametrize(
    "declared",
    ["test_x", "pkg.test_a#test_x", "pkg/test_a.py::test_x", "pkg/test_a.py::TestG::test_y"],
)
def test_every_spelling_that_names_this_testcase_is_read(declared):
    name = declared.rpartition("::")[2].rpartition("#")[2]
    classname = "pkg.test_a.TestG" if "TestG" in declared else "pkg.test_a"
    assert spells(case(classname=classname, name=name), declared)


@pytest.mark.parametrize(
    "declared",
    [
        "test_other",
        "pkg/test_b.py::test_x",
        "pkg/test_a.py::TestH::test_x",
        "pkg/test_a::test_x",
        "pkg/test_a.py::",
        "::test_x",
        "pkg.test_a::test_x",
        "other.test_a#test_x",
    ],
)
def test_a_spelling_that_names_another_testcase_is_refused(declared):
    assert not spells(case(classname="pkg.test_a", name="test_x"), declared)


def test_the_file_attribute_still_rebuilds_the_node_id():
    element = case(classname="pkg.test_a.TestG", name="test_y", file="pkg/test_a.py")
    assert spells(element, "pkg/test_a.py::TestG::test_y")


@pytest.mark.parametrize(
    "attributes",
    [
        {"message": "assert 1 == 2"},
        {"message": "AssertionError: words"},
        {"message": "Failed: DID NOT RAISE <class 'ValueError'>"},
        {"type": "org.opentest4j.AssertionFailedError", "message": "expected 1"},
        {"type": "java.lang.AssertionError"},
        {"type": "org.junit.ComparisonFailure"},
    ],
)
def test_a_failure_that_says_an_assertion_failed_is_one(attributes):
    assert asserted(failing(**attributes), PASSING_CHILDREN)


@pytest.mark.parametrize(
    "element",
    [
        failing(message="NotImplementedError: write me"),
        failing(message="TypeError: unsupported operand"),
        failing(type="java.lang.NullPointerException", message="x"),
        failing("error", type="org.opentest4j.AssertionFailedError"),
        failing("skipped", message="s"),
        failing(),
        case(name="t"),
    ],
    ids=["nie", "type-error", "npe", "error-element", "skipped", "bare-failure", "passing"],
)
def test_anything_else_is_not_an_assertion(element):
    assert not asserted(element, PASSING_CHILDREN)


@pytest.mark.parametrize(
    ("declared", "classname"),
    [
        ("tests/a/test_x.py::test_f", "tests.b.test_x"),
        ("tests/a/test_x.py::test_f", "other.test_x"),
        ("tests/a/test_x.py::TestC::test_f", "tests.b.test_x.TestC"),
        ("tests/a/test_x.py::TestC::test_f", "tests.a.test_x.TestD"),
        ("tests/a/test_x.py::test_f", "b.tests.a.test_x"),
        ("test_x.py::test_f", "tests.test_x"),
    ],
)
def test_a_node_id_from_another_module_or_package_is_refused(declared, classname):
    assert not spells(case(classname=classname, name="test_f"), declared)


def test_the_same_node_id_from_the_same_module_is_read():
    assert spells(case(classname="tests.a.test_x", name="test_f"), "tests/a/test_x.py::test_f")
    assert spells(
        case(classname="tests.a.test_x.TestC", name="test_f"), "tests/a/test_x.py::TestC::test_f"
    )


# --- `node --test`: every failure is `testCodeFailure`, told apart by the cause in its text ----


def node_failure(cause: str, message: str = "m") -> ElementTree.Element:
    element = case(name="t", classname="test")
    child = ElementTree.SubElement(
        element, "failure", {"type": "testCodeFailure", "message": message}
    )
    child.text = (
        f"[Error [ERR_TEST_FAILURE]: {message}] {{\n  code: 'ERR_TEST_FAILURE',\n"
        f"  failureType: 'testCodeFailure',\n  cause: {cause}\n      at x\n}}"
    )
    return element


@pytest.mark.parametrize(
    "cause",
    ["AssertionError [ERR_ASSERTION]: words", "AssertionError [ERR_ASSERTION]: Missing expected"],
)
def test_a_node_failure_caused_by_an_assertion_is_one(cause):
    assert asserted(node_failure(cause), PASSING_CHILDREN)


@pytest.mark.parametrize(
    ("cause", "message"),
    [
        ("TypeError: x is null", "x is null"),
        ("Error: NotImplementedError: write", "NotImplementedError: write"),
        ("Error: boom", "AssertionError: pretend"),
        ("Error: AssertionError: pretend", "AssertionError: pretend"),
    ],
    ids=["type-error", "not-implemented", "message-says-assertion", "cause-says-assertion"],
)
def test_a_node_failure_caused_by_anything_else_is_not_an_assertion(cause, message):
    assert not asserted(node_failure(cause, message), PASSING_CHILDREN)


def test_a_node_failure_never_reads_as_an_assertion_from_its_message_alone():
    element = node_failure("Error: boom", "AssertionError: pretend")
    assert not asserted(element, PASSING_CHILDREN)


def test_the_pytest_and_surefire_readings_are_unchanged():
    assert asserted(failing(message="assert 1 == 2"), PASSING_CHILDREN)
    assert asserted(failing(type="org.opentest4j.AssertionFailedError"), PASSING_CHILDREN)
    assert not asserted(failing(message="NotImplementedError: x"), PASSING_CHILDREN)


def file_case(name: str, file: str, failed: bool = True) -> ElementTree.Element:
    element = case(name=name, classname="test", file=file)
    if failed:
        ElementTree.SubElement(element, "failure", {"type": "testCodeFailure", "message": "f"})
    return element


@pytest.mark.parametrize(
    "element",
    [
        file_case("normalise.test.ts", "/w/practice/normalise.test.ts"),
        file_case("practice/normalise.test.ts", "/w/practice/normalise.test.ts"),
        file_case("a.test.mjs", "C:\\w\\a.test.mjs"),
    ],
)
def test_a_test_file_that_failed_to_load_is_told(element):
    assert file_level_failure(element)


@pytest.mark.parametrize(
    "element",
    [
        file_case("normalise.test.ts", "/w/normalise.test.ts", failed=False),
        file_case("plain", "/w/normalise.test.ts"),
        file_case("other.test.ts", "/w/normalise.test.ts"),
        file_case("test.ts", "/w/normalise.test.ts"),
        case(name="normalise.test.ts", classname="test"),
    ],
    ids=["passed", "a-test", "another-file", "tail-not-at-a-boundary", "no-file"],
)
def test_nothing_else_is_a_file_that_failed_to_load(element):
    assert not file_level_failure(element)
