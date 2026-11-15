"""Mirror of `src/studyforge/skills/exercises/projectfields.py` (R12).

`test_project` reads these through `read_manifest`; this pins each reader on its own: what
it returns, and that a refusal names the field and the manifest, never the value it was given.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import EDGE, KEPT, MAIN, Case, Origin
from studyforge.skills.exercises.blueprint import Lesson, Method
from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.projectfields import (
    kind_of,
    list_of,
    object_of,
    read_case,
    read_cited,
    read_edit,
    read_method,
    text_of,
)

WHERE = "project.json"
SECRET = "value-that-must-not-be-echoed"

METHOD = {
    "file": "src/caps.py",
    "signature": "def caps(lots, room)",
    "contract": "Returns the lots that fit.",
    "idea": "Greedy by size.",
    "lesson": {"title": "Knapsack", "href": "knapsack.unit.html"},
}


def _refused(call, *field_words: str) -> str:
    with pytest.raises(AuthoringError) as caught:
        call()
    said = str(caught.value)
    assert said.startswith(f"{WHERE}: ")
    for word in field_words:
        assert word in said
    assert SECRET not in said
    return said


def test_the_shape_checks_return_the_value_or_name_the_field():
    assert text_of("x", "title", WHERE) == "x"
    assert list_of([1], "cases", WHERE) == [1]
    assert object_of({"a": 1}, "plants", WHERE) == {"a": 1}
    assert kind_of(MAIN, (MAIN, EDGE), "expected.kind", WHERE) == MAIN
    _refused(lambda: text_of("  ", "title", WHERE), "'title'", "non-empty string")
    _refused(lambda: text_of(7, "title", WHERE), "'title'")
    _refused(lambda: list_of(SECRET, "cases", WHERE), "'cases'", "array")
    _refused(lambda: object_of([SECRET], "plants", WHERE), "'plants'", "object")
    _refused(lambda: kind_of(SECRET, (MAIN, EDGE), "expected.kind", WHERE), "'expected.kind'")


def test_a_blueprint_entry_reads_every_field_and_the_stub_is_optional():
    assert read_method(METHOD, WHERE) == Method(
        file="src/caps.py",
        signature="def caps(lots, room)",
        contract="Returns the lots that fit.",
        idea="Greedy by size.",
        lesson=Lesson("Knapsack", "knapsack.unit.html"),
        stub=None,
    )
    assert read_method({**METHOD, "stub": "return ()"}, WHERE).stub == "return ()"
    _refused(lambda: read_method({**METHOD, "idea": ""}, WHERE), "'blueprint[].idea'")
    _refused(lambda: read_method({**METHOD, "lesson": SECRET}, WHERE), "'blueprint[].lesson'")


def test_a_case_is_id_kind_and_says():
    assert read_case(["t1", KEPT, "keeps it"], WHERE) == Case("t1", KEPT, "keeps it")
    _refused(lambda: read_case(["t1", MAIN], WHERE), "[id, kind, says]")
    _refused(lambda: read_case(["t1", SECRET, "x"], WHERE), "'cases[].kind'")


def test_a_plant_edit_is_three_strings():
    assert read_edit(["a.py", "old", "new"], WHERE) == ("a.py", "old", "new")
    _refused(lambda: read_edit(["a.py", "old"], WHERE), "[file, old, new]")
    _refused(lambda: read_edit(["a.py", "old", 3], WHERE), "three strings")


def test_cites_is_optional_and_otherwise_a_path_and_a_section():
    assert read_cited(None, WHERE) is None
    assert read_cited({"path": "a.unit.md", "section": "Why"}, WHERE) == Origin("a.unit.md", "Why")
    _refused(lambda: read_cited({"section": "Why"}, WHERE), "'cites.path'")
