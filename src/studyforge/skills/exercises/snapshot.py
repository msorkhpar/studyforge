r"""A project snapshot read off disk: its files sorted into roles, and the tests it declares.

**What it does.** `read_snapshot(folder, tests=)` reads one complete snapshot of a growing project
(the package, its entry point, its data and its tests) and sorts every file into the role a
project practice gives it: a **source** file the reader may edit, a **test** file, or a
**read-only** file (a fixture, a data file, an expected report). `declared_tests(snapshot)` lists
test the tests folder declares, by the pytest node id a JUnit report spells, with its own source
and the first line of its docstring.

**How you use it.**

    before = read_snapshot(Path("steps/02"), tests="tests")
    after = read_snapshot(Path("steps/03"), tests="tests")
    after.sources                 # {"planner/model.py": "...", "main.py": "..."}
    declared_tests(after)         # {"tests/test_model.py::test_caps_hold": Declared(...)}

**Depends on.** `ast`, `pathlib` and this package's `drafts.AuthoringError`. Standard library only.

## ⭐ THE ROLE IS READ OFF THE PATH, AND THREE RULES DECIDE IT

1. Everything under the tests folder is the grade: its `test_*.py` files are **tests**, and every
   other file there (a `conftest.py`, a fixture) is **read-only**.
2. Every other `.py` file is **source**, which the reader may edit, the entry point included.
3. Every other file (data, an expected report) is **read-only**, except `pytest.ini` at the root,
   which is the **build** file that makes the workspace pytest's root.

⛔ A cache or a dot-file is not part of a snapshot: `__pycache__`, `.pytest_cache`, a run's
`target/` and every name starting with `.` are skipped. ⛔ A file that is not UTF-8 text is
refused by name, because the archive and the workspace carry text.

## ⛔ A TEST ID IS READ STATICALLY, AND A PARAMETRISED TEST IS DECLARED BY HAND

⭐ A test function at module level, or a method of a `Test*` class, is one node id:
`tests/test_model.py::test_caps_hold` or `tests/test_model.py::TestCaps::test_holds`. ⚠️ A
parametrised test reports one id per parameter, which no static reading can spell, so
`declared_tests` names it in `parametrised` and the manifest declares its ids itself.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.skills.exercises.drafts import AuthoringError

#: The build file a snapshot may carry at its root: it makes the workspace pytest's root.
BUILD_FILE = "pytest.ini"

#: ⭐ The build file a snapshot that carries none is given: the workspace is the root pytest
#: reads ids from, and the package beside the tests is importable from it.
DEFAULT_BUILD = "[pytest]\npythonpath = .\n"

#: Names that are never part of a snapshot, at any depth.
SKIPPED = ("__pycache__", ".pytest_cache", "target")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """One step of a project, its files sorted into the four roles a practice gives them."""

    sources: dict[str, str]
    tests: dict[str, str]
    read_only: dict[str, str]
    build: dict[str, str]
    tests_dir: str


@dataclass(frozen=True, slots=True)
class Declared:
    """One test as a snapshot declares it: its own source text and its docstring's first line."""

    source: str
    summary: str


@dataclass(frozen=True, slots=True)
class Ids:
    """Every test id a snapshot's tests declare, and the parametrised tests it cannot spell."""

    declared: dict[str, Declared] = field(default_factory=dict)
    parametrised: tuple[str, ...] = ()


def read_snapshot(folder: Path, *, tests: str = "tests") -> Snapshot:
    """Read every file of the snapshot at `folder` and sort it into its role."""
    root = Path(folder)
    if not (root / tests).is_dir():
        raise AuthoringError(
            "a snapshot has no tests folder of the name the manifest gives, and a project "
            "practice is graded by the tests of its snapshot"
        )
    sources: dict[str, str] = {}
    graded: dict[str, str] = {}
    read_only: dict[str, str] = {}
    build: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or _skipped(relative):
            continue
        text = _text(path, relative)
        if relative == BUILD_FILE:
            build[relative] = text
        elif relative.startswith(f"{tests}/"):
            name = relative.rsplit("/", 1)[-1]
            is_test = name.startswith("test_") and name.endswith(".py")
            (graded if is_test else read_only)[relative] = text
        elif relative.endswith(".py"):
            sources[relative] = text
        else:
            read_only[relative] = text
    return Snapshot(sources, graded, read_only, build or {BUILD_FILE: DEFAULT_BUILD}, tests)


def declared_tests(snapshot: Snapshot) -> Ids:
    """Return every test id the snapshot's test files declare, in file and line order."""
    declared: dict[str, Declared] = {}
    parametrised: list[str] = []
    for path, text in snapshot.tests.items():
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as error:
            raise AuthoringError(
                f"the test file '{path}' does not parse, at line {error.lineno}"
            ) from None
        for owner, node in _tests_in(tree):
            node_id = "::".join([path, *owner, node.name])
            if any(_parametrises(one) for one in node.decorator_list):
                parametrised.append(node_id)
                continue
            source = ast.get_source_segment(text, node) or ""
            decorators = [ast.get_source_segment(text, one) or "" for one in node.decorator_list]
            declared[node_id] = Declared("\n".join([*decorators, source]), _summary(node))
    return Ids(declared, tuple(parametrised))


def _tests_in(tree: ast.Module):
    """Yield `(class path, function)` for every test pytest collects by its default names."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith(
            "test"
        ):
            yield (), node
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for inner in node.body:
                if isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef) and (
                    inner.name.startswith("test")
                ):
                    yield (node.name,), inner


def _parametrises(decorator: ast.expr) -> bool:
    """Answer whether a decorator is `pytest.mark.parametrize(...)` or `mark.parametrize(...)`."""
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute) and target.attr == "parametrize"


def _summary(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """The first line of a test's docstring, or its name read as words."""
    docstring = ast.get_docstring(node)
    if docstring and docstring.strip():
        return docstring.strip().splitlines()[0].strip().rstrip(".")
    return node.name.removeprefix("test_").replace("_", " ")


def _skipped(relative: str) -> bool:
    """Answer whether a path is a cache, a run's output or a dot-file, at any depth."""
    return any(part in SKIPPED or part.startswith(".") for part in relative.split("/"))


def _text(path: Path, relative: str) -> str:
    """Read one file as UTF-8 text, refusing a binary one by its path inside the snapshot."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise AuthoringError(
            f"a snapshot holds '{relative}', which is not UTF-8 text; a project "
            f"practice's files are text"
        ) from None
