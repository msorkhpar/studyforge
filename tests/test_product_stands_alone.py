"""`REL-02`: no product test imports the tooling, and the process tests are declared.

**What it asserts.** Every Python file under `tests/`, and the root `conftest.py`, reaches the
tooling (`tools`, `tools.*`) by no import statement and by no literal handed to a run-time
importer — unless the file, or the one test the import sits in, is declared process in
`tests/harness/process.py`. ⭐ The declaration itself is checked: every entry names a file and a
test that exist, so a renamed test cannot leave a stale entry that silently excuses nothing.

⛔ **The proof that the product stands alone is not this file**: it is the product suite run in
a scratch export with the tooling and the process documents REMOVED (`E15`'s second property).
This file is the standing guard between those runs — it refuses the one regression a working
checkout, where the tooling is always present, can never show by running.

⚠️ **A file that is another task's is named, not excused silently**: `process.DEFERRED` names
it with its reason, and a test below fails once it stops needing the entry, so the entry cannot
outlive its reason.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.harness import process
from tests.support import repository_root

#: The package whose top-level name is the tooling.
TOOLING = "tools"

#: The run-time importers a literal module name can be handed to.
IMPORTERS = ("import_module", "__import__")


def _is_tooling(name: str | None) -> bool:
    return bool(name) and (name == TOOLING or name.startswith(TOOLING + "."))


def _names_tooling(node: ast.AST) -> bool:
    """Report whether `node` is an import of the tooling, static or through an importer."""
    if isinstance(node, ast.Import):
        return any(_is_tooling(alias.name) for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return node.level == 0 and _is_tooling(node.module)
    if isinstance(node, ast.Call) and node.args:
        func = node.func
        called = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        first = node.args[0]
        return (
            called in IMPORTERS
            and isinstance(first, ast.Constant)
            and isinstance(first.value, str)
            and _is_tooling(first.value)
        )
    return False


def reaches_tooling(relative: str, source: str) -> list[int]:
    """Return the lines where `source` reaches the tooling and no declaration excuses it.

    ⭐ A declared FILE excuses every line; a declared TEST excuses the lines inside that test's
    own function body and nowhere else in the file.
    """
    if relative in process.uncollected():
        return []
    excused = {
        entry.partition("::")[2].split("[", 1)[0]
        for entry in process.TESTS
        if entry.partition("::")[0] == relative
    }
    tree = ast.parse(source)
    inside: set[int] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in excused:
            inside |= {id(child) for child in ast.walk(node)}
    return sorted(
        node.lineno for node in ast.walk(tree) if _names_tooling(node) and id(node) not in inside
    )


def product_files(root: Path) -> list[str]:
    """Every Python file the sweep reads: all of `tests/`, and the root `conftest.py`."""
    found = [p.relative_to(root).as_posix() for p in (root / "tests").rglob("*.py")]
    return sorted(name for name in [*found, "conftest.py"] if "__pycache__" not in name)


def test_no_product_test_reaches_the_tooling():
    root = repository_root()
    files = product_files(root)
    assert len(files) > 100, f"the sweep read {len(files)} file(s): a blind sweep, not a pass"
    found = {
        name: lines
        for name in files
        if (lines := reaches_tooling(name, (root / name).read_text(encoding="utf-8")))
    }
    assert found == {}, (
        f"a product test reaches the tooling: {found}. Read it through a helper under "
        f"tests/harness/, or — if what it guards is process — declare it in "
        f"tests/harness/process.py"
    )


# --- the plants: each shape the sweep must refuse, and each it must not ---------------------

PRODUCT = "tests/test_a_product_test.py"


@pytest.mark.parametrize(
    "planted",
    [
        "import tools\n",
        "import tools.quality\n",
        "from tools import treestate\n",
        "from tools.workspace import read\n",
        "def test_x():\n    from tools.mergegate import GATES\n",
        "import importlib\nimportlib.import_module('tools.treereaders')\n",
        "WHAT = __import__('tools.quality')\n",
    ],
    ids=["import", "dotted", "from", "from-dotted", "inside-a-test", "import_module", "dunder"],
)
def test_a_planted_import_of_the_tooling_is_refused(planted):
    assert reaches_tooling(PRODUCT, planted) != []


@pytest.mark.parametrize(
    "harmless",
    [
        "import toolsmith\n",
        "from toolshed import x\n",
        "from .tools import x\n",
        "import importlib\nimportlib.import_module('studyforge.tools')\n",
        "PATH = 'tools/quality'\n",
    ],
    ids=["prefix-name", "prefix-from", "relative", "not-the-tooling", "a-path-string"],
)
def test_what_merely_looks_like_the_tooling_is_not(harmless):
    assert reaches_tooling(PRODUCT, harmless) == []


def test_a_declared_process_file_may_import_the_tooling():
    declared = sorted(process.files())[0]
    assert reaches_tooling(declared, "import tools.quality\n") == []


def test_a_declared_process_TEST_is_excused_only_inside_its_own_body():
    entry = next(e for e in process.TESTS if "[" not in e)
    path, _, name = entry.partition("::")
    inside = f"def {name}():\n    import tools.quality\n"
    beside = f"import tools.quality\n\n\ndef {name}():\n    pass\n"
    assert reaches_tooling(path, inside) == []
    assert reaches_tooling(path, beside) == [1]


def test_the_root_conftest_names_the_tooling_only_through_its_one_seam():
    text = (repository_root() / "conftest.py").read_text(encoding="utf-8")
    named = {
        node.value
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        if _is_tooling(node.value)
    }
    assert named == {"tools.treereaders"}, named


# --- the declaration is true of the tree ----------------------------------------------------


@pytest.mark.parametrize("path", sorted(process.FILES))
def test_every_declared_process_file_exists(path):
    assert (repository_root() / path).is_file(), path


@pytest.mark.parametrize("entry", sorted(process.TESTS))
def test_every_declared_process_test_names_a_test_that_exists(entry):
    path, _, name = entry.partition("::")
    tree = ast.parse((repository_root() / path).read_text(encoding="utf-8"))
    defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert name.split("[", 1)[0] in defined, entry


def test_every_declaration_says_why():
    for entry, reason in {**process.FILES, **process.TESTS}.items():
        assert len(reason) > 30, entry


def test_each_deferred_file_still_needs_its_entry():
    # ⛔ An excuse that outlives its reason excuses the next regression instead.
    # ⭐ A loop, never a parametrisation: `DEFERRED` is empty since `REL-06`, and an empty
    # parameter set would print a skip every run for a population that is merely empty.
    for path in sorted(process.DEFERRED):
        source = (repository_root() / path).read_text(encoding="utf-8")
        assert any(_names_tooling(node) for node in ast.walk(ast.parse(source))), (
            f"{path} no longer reaches the tooling: remove it from process.DEFERRED"
        )


def test_a_deferred_file_is_never_marked_process():
    assert not set(process.DEFERRED) & process.files()
    assert all(process.declared(f"{path}::test_x") is None for path in process.DEFERRED)


# --- what the declaration means, one nodeid at a time -----------------------------------------


def test_a_declared_file_covers_every_test_in_it():
    path = sorted(process.files())[0]
    assert process.declared(f"{path}::test_anything[with-a-param]") == process.FILES[path]


def test_a_declared_test_covers_each_of_its_parametrisations_and_nothing_beside_it():
    entry = next(e for e in process.TESTS if "[" not in e)
    assert process.declared(entry) is not None
    assert process.declared(f"{entry}[one]") is not None
    assert process.declared(f"{entry}_and_more") is None


def test_a_declared_parametrisation_covers_itself_and_not_its_siblings():
    entry = next(e for e in process.TESTS if "[" in e)
    assert process.declared(entry) is not None
    assert process.declared(entry.split("[", 1)[0] + "[another]") is None


def test_an_undeclared_test_is_product():
    assert process.declared("tests/test_product_stands_alone.py::test_x") is None


def test_the_process_is_absent_exactly_when_the_tooling_directory_is(tmp_path):
    assert process.present(tmp_path) is False
    (tmp_path / process.TOOLING).mkdir()
    assert process.present(tmp_path) is True


def test_the_process_marker_is_registered_so_strict_markers_accepts_it(pytestconfig):
    registered = pytestconfig.getini("markers")
    assert any(line.startswith(f"{process.MARKER}:") for line in registered), registered


def test_the_summary_says_which_way_the_process_went():
    assert "none of" in process.population_line(True)
    absent = process.population_line(False)
    assert "ABSENT" in absent and "did not run" in absent
