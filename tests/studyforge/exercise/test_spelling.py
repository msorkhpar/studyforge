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
from studyforge.exercise.spelling import asserted, spells


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
