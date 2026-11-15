"""The fields of a project manifest, each read and refused by name.

**What it does.** Reads the parts of a `project.json` that are more than one value: a
blueprint entry (`read_method`), a declared case (`read_case`), a plant edit (`read_edit`)
and the lesson the practice cites (`read_cited`), on four shape checks (`text_of`,
`list_of`, `object_of`, `kind_of`) that refuse a wrong value with `AuthoringError`, naming
the field and never echoing the value.

**How you use it.** `project.read_manifest` calls them with the manifest's name as `where`;
each returns the value it read or raises.

**Depends on.** `studyforge.exercise` for a case and an origin, `blueprint` for a method,
and `drafts.AuthoringError`. Standard library otherwise; no I/O.
"""

from __future__ import annotations

from studyforge.exercise import EDGE, KEPT, MAIN, Case, Origin
from studyforge.skills.exercises.blueprint import Lesson, Method
from studyforge.skills.exercises.drafts import AuthoringError


def read_method(value: object, where: str) -> Method:
    """Read one blueprint entry; every field but `stub` is required."""
    entry = object_of(value, "blueprint[]", where)
    lesson = object_of(entry.get("lesson"), "blueprint[].lesson", where)
    return Method(
        file=text_of(entry.get("file"), "blueprint[].file", where),
        signature=text_of(entry.get("signature"), "blueprint[].signature", where),
        contract=text_of(entry.get("contract"), "blueprint[].contract", where),
        idea=text_of(entry.get("idea"), "blueprint[].idea", where),
        lesson=Lesson(
            text_of(lesson.get("title"), "blueprint[].lesson.title", where),
            text_of(lesson.get("href"), "blueprint[].lesson.href", where),
        ),
        stub=entry.get("stub"),
    )


def read_case(value: object, where: str) -> Case:
    """Read one declared case, `[id, kind, says]`."""
    if not isinstance(value, list) or len(value) != 3:
        raise AuthoringError(f"{where}: a declared case is [id, kind, says]")
    case_id, kind, says = value
    return Case(
        text_of(case_id, "cases[].id", where),
        kind_of(kind, (MAIN, EDGE, KEPT), "cases[].kind", where),
        text_of(says, "cases[].says", where),
    )


def read_edit(value: object, where: str) -> tuple[str, str, str]:
    """Read one plant edit, `[file, old, new]`."""
    if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, str) for v in value):
        raise AuthoringError(f"{where}: a plant edit is [file, old, new], three strings")
    return value[0], value[1], value[2]


def read_cited(value: object, where: str) -> Origin | None:
    """Read `cites`, the lesson the practice is built from: absent is none, else path and section.

    ⭐ Named `cites` rather than `origin`: the record's `origin` has one reader
    (`cases.origin_in`), and this is the manifest's own word for the value handed to it.
    """
    if value is None:
        return None
    entry = object_of(value, "cites", where)
    return Origin(text_of(entry.get("path"), "cites.path", where), entry.get("section"))


def kind_of(value: object, allowed: tuple[str, ...], field: str, where: str) -> str:
    """Refuse a kind outside `allowed`."""
    if value not in allowed:
        raise AuthoringError(f"{where}: '{field}' is one of {list(allowed)}")
    return str(value)


def text_of(value: object, field: str, where: str) -> str:
    """Refuse a missing or empty text field, naming it."""
    if not isinstance(value, str) or not value.strip():
        raise AuthoringError(f"{where}: '{field}' is a non-empty string")
    return value


def list_of(value: object, field: str, where: str) -> list:
    """Refuse a field that is not a JSON array."""
    if not isinstance(value, list):
        raise AuthoringError(f"{where}: '{field}' is an array")
    return value


def object_of(value: object, field: str, where: str) -> dict:
    """Refuse a field that is not a JSON object."""
    if not isinstance(value, dict):
        raise AuthoringError(f"{where}: '{field}' is an object")
    return value
