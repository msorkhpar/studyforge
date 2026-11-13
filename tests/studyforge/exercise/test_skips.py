"""Mirror of `src/studyforge/exercise/skips.py` (R12): a case may skip only where it says so."""

from __future__ import annotations

from xml.etree import ElementTree

import pytest

from studyforge.exercise import PASSING_CHILDREN, ExerciseError
from studyforge.exercise.skips import SKIPS_WITHOUT, skipped_only, skips_without_of

WHERE = "course/unit-01/practice-1"


def test_no_key_is_no_capability():
    assert skips_without_of({"id": "t", "kind": "edge", "says": "s"}, "edge", WHERE) is None


@pytest.mark.parametrize("kind", ["edge", "kept"])
def test_an_edge_or_a_kept_case_may_name_a_capability(kind):
    assert skips_without_of({SKIPS_WITHOUT: "gpu"}, kind, WHERE) == "gpu"


@pytest.mark.parametrize("value", ["", "GPU", "a gpu", "gpu!", 7, None, "x" * 33])
def test_a_capability_that_is_not_a_short_lowercase_token_is_refused(value):
    with pytest.raises(ExerciseError, match="names a capability"):
        skips_without_of({SKIPS_WITHOUT: value}, "edge", WHERE)


def test_the_main_ask_may_never_skip():
    with pytest.raises(ExerciseError, match="always runs"):
        skips_without_of({SKIPS_WITHOUT: "gpu"}, "main", WHERE)


@pytest.mark.parametrize(
    ("body", "skipped"),
    [
        ("<skipped/>", True),
        ('<skipped message="no GPU"/><system-out>x</system-out>', True),
        ("", False),
        ('<skipped/><failure message="m"/>', False),
        ("<skipped/><error/>", False),
        ("<rerunFailure/>", False),
    ],
)
def test_only_a_skip_and_nothing_else_reads_as_skipped(body, skipped):
    element = ElementTree.fromstring(f'<testcase name="t">{body}</testcase>')
    assert skipped_only(element, PASSING_CHILDREN) is skipped
