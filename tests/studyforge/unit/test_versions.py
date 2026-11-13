"""Mirror of `src/studyforge/unit/versions.py` (R12): the word before a number makes it a release.

⛔ **Every expectation is a literal**, written before the run.
"""

from __future__ import annotations

import pytest

from studyforge.unit.versions import VERSION_WORDS, follows_version_word


@pytest.mark.parametrize(
    "before",
    [
        "the pinned PuLP ",
        "solved by HiGHS ",
        "OR-Tools ",
        "CUDA ",
        "an OpenAPI ",
        "the cuOpt ",
        "since version ",
        "Version ",
        "tagged v ",
        "PuLP ",
        "PuLP   ",
    ],
)
def test_a_word_that_names_a_version_is_read_as_one(before):
    assert follows_version_word(before)


@pytest.mark.parametrize(
    "before",
    [
        "",
        "as ",
        "lesson ",
        "Lesson ",
        "Lessons ",
        "See ",
        "Gurobi ",
        "highspy ",
        "(",
        "PuLP, ",
        "HiGHS: ",
        "on HiGHS. ",
        "the PuLP",
        "a title*; ",
        "`PuLP` ",
    ],
)
def test_any_other_word_or_none_is_not(before):
    assert not follows_version_word(before)


def test_the_words_that_name_a_version_on_their_own_are_two():
    assert VERSION_WORDS == frozenset({"version", "v"})


def test_only_the_tail_is_read():
    # ⭐ A long run of prose in front of the word changes nothing.
    assert follows_version_word("word " * 10_000 + "PuLP ")
    assert not follows_version_word("PuLP " + "word " * 10_000)
