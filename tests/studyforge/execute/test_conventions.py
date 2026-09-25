"""Mirror of `src/studyforge/execute/conventions.py` (R12): the tools' own names, spelled once."""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import RUNTIMES
from studyforge.execute import conventions
from studyforge.execute.conventions import (
    SOURCE_SUFFIXES,
    is_a_test,
    source_suffixes,
)
from studyforge.execute.conventions import tested_stem as untested
from studyforge.skills.execution import prime, specimens


def test_the_prime_reads_the_same_spelling_and_keeps_none_of_its_own():
    # ⛔ Two spellings of one answer drift the day one learns a tool the other does not.
    for name in ("BUILD_FILES", "SKIPPED", "SOURCE_SUFFIXES"):
        assert getattr(prime, name) is getattr(conventions, name), name
    assert specimens.is_a_test is is_a_test


def test_every_source_suffix_is_keyed_on_a_declarable_runtime():
    assert set(SOURCE_SUFFIXES) <= set(RUNTIMES)


@pytest.mark.parametrize(
    "runtimes,suffixes",
    [
        (("java", "maven"), (".java",)),
        (("maven",), ()),
        (("java", "kotlin", "python"), (".java", ".kt", ".py")),
        ((), ()),
    ],
)
def test_a_declared_set_writes_exactly_its_languages_suffixes(runtimes, suffixes):
    assert source_suffixes(runtimes) == suffixes


@pytest.mark.parametrize(
    "stem,tested",
    [
        ("PrimitiveTypesTest", "PrimitiveTypes"),
        ("ParserTests", "Parser"),
        ("test_parse", "parse"),
        ("greet_test", "greet"),
        ("ShapeSpec", "Shape"),
        ("Types", "Types"),
        ("Test", "Test"),
    ],
)
def test_a_test_stem_names_what_it_tests_once_its_marking_is_off(stem, tested):
    assert untested(stem) == tested


@pytest.mark.parametrize(
    "where,test",
    [
        ("m/src/test/java/p/Helper.java", True),
        ("m/src/main/java/p/TypesTest.java", True),
        ("m/src/main/java/p/Types.java", False),
        ("tests/conftest.py", True),
        ("lib/testing.py", False),
    ],
)
def test_a_test_is_known_by_its_directory_or_its_stem(where, test):
    assert is_a_test(where) is test
