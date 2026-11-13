r"""A project practice from a before/after pair of snapshots, declared in one small manifest.

**What it does.** Reads a project manifest (`project.json`), the two complete snapshots it names,
and answers with the `CodeDraft` the authoring gates read: the **before** snapshot's code is the
starter, the **after** snapshot's code is the reference, and the **after** snapshot's tests are the
grade. ⭐ It writes the expected-output check (`expected`), appends the blueprint to the statement
(`blueprint`), stubs each blueprint method the starter lacks, and derives a case for every test.

**How you use it.**

    draft = project_draft(Path("exercise-src/m/3.1/caps/project.json"), brief.places.workspace,
                          origin=Origin(brief.page.path, None))

`python -m studyforge.skills.exercises.project new <before> <after>` prints a manifest to fill in,
and `python -m studyforge.skills.exercises.project check <manifest>` builds the draft and says
what it would ship, without running anything (`projectcli`).

**Depends on.** `studyforge.exercise` for the case vocabulary, `exercise.bundle` for a plant,
and this package's `drafts`, `snapshot`, `blueprint` and `expected`. Standard library only.

## ⭐ EVERY TEST IS A CASE, AND A KEPT ONE IS DERIVED

⛔ A Submit's breakdown refuses a test its case map does not name, so a project declares a case
for every test. ⭐ The manifest declares the tests this step **adds or changes** (a test whose
source differs from the before snapshot's, or that the before snapshot lacks), each as `main` or
`edge` with the sentence a reader is shown; every **unchanged** test is a `kept` case, worded by
its docstring, which gate G2 proves passes on the starter. ⛔ A new or changed test the manifest
does not declare is refused by id, because guessing its kind would guess what the step asks.

## ⭐ WHAT THE READER EDITS IS EVERY SOURCE FILE

⭐ Every `.py` file outside the tests folder is the reader's to edit, the entry point included,
whether this step changes it or not: the grade is the tests and the report, never how close the
code is to the reference. ⛔ Tests, fixtures, data and the expected report are read-only.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from studyforge.exercise import EDGE, KEPT, MAIN, Case, Origin
from studyforge.exercise.bundle import PlantSpec, Replacement
from studyforge.skills.exercises.blueprint import (
    Lesson,
    Method,
    blueprint_markdown,
    stubbed,
    undefined,
)
from studyforge.skills.exercises.drafts import AuthoringError, CodeDraft, EditedFile
from studyforge.skills.exercises.expected import (
    CHECK_FILE,
    CHECK_SAYS,
    CHECK_TEST,
    Expected,
    check_source,
)
from studyforge.skills.exercises.snapshot import Snapshot, read_snapshot, declared_tests

#: The manifest format's version.
PROJECT_API = 1

#: The manifest's file name, beside the statement it names.
MANIFEST_FILENAME = "project.json"

#: ⛔ Every key a manifest may carry, in the order `new` writes them; an unknown one is refused.
MANIFEST_KEYS = (
    "project_api",
    "title",
    "before",
    "after",
    "tests",
    "entry",
    "statement",
    "expected",
    "blueprint",
    "cases",
    "plants",
    "assertions_only",
    "origin",
)

#: The keys a manifest may leave out, with what leaving one out means.
OPTIONAL = {"tests": "tests", "plants": {}, "assertions_only": True, "origin": None}

#: Where every run's report lands, inside the workspace.
REPORT = "target/report.xml"


@dataclass(frozen=True, slots=True)
class Manifest:
    """One project practice as its manifest declares it, every path resolved from the manifest."""

    title: str
    before: Path
    after: Path
    tests: str
    entry: str
    statement: str
    expected: Expected
    expected_kind: str
    expected_says: str
    methods: tuple[Method, ...]
    cases: tuple[Case, ...]
    plants: dict[str, tuple[tuple[str, str, str], ...]]
    assertions_only: bool
    origin: Origin | None


def read_manifest(path: Path) -> Manifest:
    """Read a project manifest, refusing every way it can be wrong, by key."""
    where = Path(path).name
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError:
        raise AuthoringError(f"{where}: the manifest cannot be read") from None
    except json.JSONDecodeError as error:
        raise AuthoringError(f"{where}: the manifest is not JSON, at line {error.lineno}") from None
    if not isinstance(value, dict):
        raise AuthoringError(f"{where}: a project manifest is a JSON object")
    unknown = sorted(set(value) - set(MANIFEST_KEYS))
    missing = [key for key in MANIFEST_KEYS if key not in value and key not in OPTIONAL]
    if unknown or missing:
        raise AuthoringError(
            f"{where}: a project manifest carries {list(MANIFEST_KEYS)}; this one is missing "
            f"{missing} and carries {unknown}, which the format does not define"
        )
    if value["project_api"] != PROJECT_API:
        raise AuthoringError(f"{where}: 'project_api' is {PROJECT_API}")
    value = {**OPTIONAL, **value}
    base = Path(path).parent
    expected = _object(value["expected"], "expected", where)
    return Manifest(
        title=_text(value["title"], "title", where),
        before=base / _text(value["before"], "before", where),
        after=base / _text(value["after"], "after", where),
        tests=_text(value["tests"], "tests", where),
        entry=_text(value["entry"], "entry", where),
        statement=_read(base / _text(value["statement"], "statement", where), where),
        expected=Expected(
            _text(expected.get("output"), "expected.output", where),
            float(expected.get("abs_tol", 1e-6)),
            float(expected.get("rel_tol", 1e-9)),
        ),
        expected_kind=_kind(expected.get("kind", MAIN), (MAIN, EDGE), "expected.kind", where),
        expected_says=_text(expected.get("says", CHECK_SAYS), "expected.says", where),
        methods=tuple(_method(one, where) for one in _list(value["blueprint"], "blueprint", where)),
        cases=tuple(_case(one, where) for one in _list(value["cases"], "cases", where)),
        plants={
            case: tuple(_edit(one, where) for one in _list(edits, f"plants.{case}", where))
            for case, edits in _object(value["plants"], "plants", where).items()
        },
        assertions_only=bool(value["assertions_only"]),
        origin=_origin(value["origin"], where),
    )


def project_draft(
    manifest: Manifest | Path, workspace: str, *, origin: Origin | None = None
) -> CodeDraft:
    """Return the code draft a project manifest declares, for the practice at `workspace`."""
    found = manifest if isinstance(manifest, Manifest) else read_manifest(manifest)
    where = found.title
    before = read_snapshot(found.before, tests=found.tests)
    after = read_snapshot(found.after, tests=found.tests)
    check = f"{found.tests}/{CHECK_FILE}"
    _require_project(found, before, after, check, where)
    references = dict(after.sources)
    starters = stubbed({p: before.sources.get(p, "") for p in references}, found.methods)
    main = found.methods[0].file
    depth = check.count("/")
    return CodeDraft(
        title=found.title,
        lang="python",
        main_file=main,
        test_file=check,
        run_command=("python3", f"{workspace}/{found.entry}"),
        test_command=(
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--junitxml={workspace}/{REPORT}",
            f"{workspace}/{found.tests}",
        ),
        cases=project_cases(found, before, after),
        report=REPORT,
        origin=_required_origin(origin or found.origin, where),
        statement=_statement(found),
        starter=starters[main],
        reference=references[main],
        tests=check_source(found.expected, found.entry, depth=depth),
        plants={
            case: PlantSpec(tuple(Replacement(*edit) for edit in edits))
            for case, edits in found.plants.items()
        },
        build=after.build,
        assertions_only=found.assertions_only,
        files={
            path: EditedFile(starters[path], text)
            for path, text in references.items()
            if path != main
        },
        read_only={**after.tests, **after.read_only},
    )


def project_cases(found: Manifest, before: Snapshot, after: Snapshot) -> tuple[Case, ...]:
    """Every case of the step: the declared ones, each unchanged test as kept, then the check."""
    earlier = declared_tests(before).declared
    now = declared_tests(after)
    declared = {case.id: case for case in found.cases}
    stray = [one for one in declared if not _names_a_test(one, now)]
    if stray:
        raise AuthoringError(
            f"{found.title}: {len(stray)} declared case(s) name no test of the after snapshot, "
            f"starting at '{stray[0]}'"
        )
    changed = [
        one
        for one, test in now.declared.items()
        if one not in declared and (one not in earlier or earlier[one].source != test.source)
    ]
    if changed:
        raise AuthoringError(
            f"{found.title}: {len(changed)} test(s) are new or changed in this step and the "
            f"manifest declares no case for them, starting at '{changed[0]}'; declare each as "
            f"'main' or 'edge' with the sentence a reader is shown"
        )
    cases = list(found.cases)
    cases += [
        Case(one, KEPT, test.summary) for one, test in now.declared.items() if one not in declared
    ]
    check = f"{found.tests}/{CHECK_FILE}::{CHECK_TEST}"
    return (*cases, Case(check, found.expected_kind, found.expected_says))


def _require_project(
    found: Manifest, before: Snapshot, after: Snapshot, check: str, where: str
) -> None:
    """Refuse a pair of snapshots, or a manifest, that cannot become a project practice."""
    problems = []
    if found.entry not in after.sources:
        problems.append(f"the entry point '{found.entry}' is not a source file of the after step")
    if found.expected.output not in after.read_only:
        problems.append(f"the expected report '{found.expected.output}' is not in the after step")
    if check in after.tests or check in after.read_only:
        problems.append(f"the after step already holds '{check}', the check this practice writes")
    gone = sorted(set(before.sources) - set(after.sources))
    if gone:
        problems.append(f"the after step drops the source file '{gone[0]}'")
    if not found.methods:
        problems.append("the blueprint names no method, and a reader is owed one")
    problems += undefined(after.sources, found.methods)
    kinds = {case.id: case.kind for case in found.cases}
    for case in found.plants:
        if kinds.get(case) != EDGE:
            problems.append(f"a plant is filed for '{case}', which is not a declared edge case")
    if problems:
        raise AuthoringError(f"{where}: " + "; ".join(problems))


def _names_a_test(case_id: str, ids) -> bool:
    """Answer whether a declared id is a test of the snapshot, or one of a parametrised test."""
    if case_id in ids.declared:
        return True
    base, bracket, _ = case_id.partition("[")
    return bool(bracket) and base in ids.parametrised


def _statement(found: Manifest) -> str:
    """The manifest's statement, then the blueprint, as one Markdown text."""
    return f"{found.statement.rstrip()}\n\n{blueprint_markdown(found.methods)}"


def _method(value: object, where: str) -> Method:
    """Read one blueprint entry; every field but `stub` is required."""
    entry = _object(value, "blueprint[]", where)
    lesson = _object(entry.get("lesson"), "blueprint[].lesson", where)
    return Method(
        file=_text(entry.get("file"), "blueprint[].file", where),
        signature=_text(entry.get("signature"), "blueprint[].signature", where),
        contract=_text(entry.get("contract"), "blueprint[].contract", where),
        idea=_text(entry.get("idea"), "blueprint[].idea", where),
        lesson=Lesson(
            _text(lesson.get("title"), "blueprint[].lesson.title", where),
            _text(lesson.get("href"), "blueprint[].lesson.href", where),
        ),
        stub=entry.get("stub"),
    )


def _case(value: object, where: str) -> Case:
    """Read one declared case, `[id, kind, says]`."""
    if not isinstance(value, list) or len(value) != 3:
        raise AuthoringError(f"{where}: a declared case is [id, kind, says]")
    case_id, kind, says = value
    return Case(
        _text(case_id, "cases[].id", where),
        _kind(kind, (MAIN, EDGE, KEPT), "cases[].kind", where),
        _text(says, "cases[].says", where),
    )


def _edit(value: object, where: str) -> tuple[str, str, str]:
    """Read one plant edit, `[file, old, new]`."""
    if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, str) for v in value):
        raise AuthoringError(f"{where}: a plant edit is [file, old, new], three strings")
    return value[0], value[1], value[2]


def _origin(value: object, where: str) -> Origin | None:
    """Read `origin`: absent is none; present is `{"path": ..., "section": ...}`."""
    if value is None:
        return None
    entry = _object(value, "origin", where)
    section = entry.get("section")
    return Origin(_text(entry.get("path"), "origin.path", where), section)


def _required_origin(origin: Origin | None, where: str) -> Origin:
    """Refuse a draft with no origin: gate G5 resolves it against the ledger."""
    if origin is None:
        raise AuthoringError(
            f"{where}: a project practice cites the lesson it practises; pass 'origin' to "
            f"project_draft or declare it in the manifest"
        )
    return origin


def _kind(value: object, allowed: tuple[str, ...], field: str, where: str) -> str:
    """Refuse a kind outside `allowed`."""
    if value not in allowed:
        raise AuthoringError(f"{where}: '{field}' is one of {list(allowed)}")
    return str(value)


def _text(value: object, field: str, where: str) -> str:
    """Refuse a missing or empty text field, naming it."""
    if not isinstance(value, str) or not value.strip():
        raise AuthoringError(f"{where}: '{field}' is a non-empty string")
    return value


def _list(value: object, field: str, where: str) -> list:
    """Refuse a field that is not a JSON array."""
    if not isinstance(value, list):
        raise AuthoringError(f"{where}: '{field}' is an array")
    return value


def _object(value: object, field: str, where: str) -> dict:
    """Refuse a field that is not a JSON object."""
    if not isinstance(value, dict):
        raise AuthoringError(f"{where}: '{field}' is an object")
    return value


def _read(path: Path, where: str) -> str:
    """Read the statement the manifest names."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        raise AuthoringError(f"{where}: the statement '{path.name}' cannot be read") from None


if __name__ == "__main__":
    from studyforge.skills.exercises.projectcli import main

    sys.exit(main(sys.argv[1:]))
