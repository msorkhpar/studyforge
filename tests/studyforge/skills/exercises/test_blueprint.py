"""Mirror of `skills.exercises.blueprint` (R12): the methods to write, shown and stubbed."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import parse
from studyforge.skills.exercises import AuthoringError
from studyforge.skills.exercises.blueprint import (
    Lesson,
    Method,
    blueprint_markdown,
    stubbed,
    undefined,
)

METHOD = Method(
    "pkg/model.py",
    "def caps(lots: list, room: int) -> tuple:",
    "Returns the lots that fit.",
    "A cap is one constraint per year.",
    Lesson("Budget caps", "../caps.html"),
    stub="return ()",
)


def test_the_blueprint_shows_signature_contract_idea_and_lesson_and_the_archive_reads_it():
    text = blueprint_markdown((METHOD,))
    assert "#### `caps` in `pkg/model.py`" in text
    assert "def caps(lots: list, room: int) -> tuple\n" in text
    assert "- **Contract.** Returns the lots that fit." in text
    assert "- **Modeling idea.** A cap is one constraint per year." in text
    assert "- **Taught in** [Budget caps](../caps.html)." in text
    assert [block["type"] for block in parse(text)][:2] == ["heading", "para"]
    assert blueprint_markdown(()) == ""


def test_a_method_the_starter_lacks_is_stubbed_and_one_it_has_is_left_alone():
    starters = stubbed({"pkg/model.py": "import x\n"}, (METHOD,))
    assert starters["pkg/model.py"] == (
        'import x\n\n\ndef caps(lots: list, room: int) -> tuple:\n'
        '    """Returns the lots that fit."""\n    return ()\n'
    )
    again = stubbed(starters, (METHOD,))
    assert again == starters
    new = stubbed({}, (Method("pkg/new.py", "def f()", "c", "i", Lesson("t", "h")),))
    assert new["pkg/new.py"].endswith("    raise NotImplementedError\n")


def test_undefined_names_a_method_the_reference_does_not_define():
    assert undefined({"pkg/model.py": "def caps():\n    pass\n"}, (METHOD,)) == []
    assert undefined({"pkg/model.py": "x = 1\n"}, (METHOD,)) == [
        "the reference's 'pkg/model.py' does not define 'caps'"]
    assert "not a source file" in undefined({}, (METHOD,))[0]


def test_a_signature_that_names_no_function_is_refused():
    with pytest.raises(AuthoringError):
        Method("a.py", "caps(x)", "c", "i", Lesson("t", "h")).name
