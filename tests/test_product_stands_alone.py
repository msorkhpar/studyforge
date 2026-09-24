"""No product test imports the tooling that built the framework.

**What it asserts.** Every Python file under `tests/`, and the root `conftest.py`, reaches the
tooling (`tools`, `tools.*`) by no import statement and by no literal handed to a run-time
importer. ⚠️ There is no declaration of excused files, because nothing on the main line may
need one.

⛔ **The proof that the product stands alone is the product suite running GREEN on the main
line**, where the tooling is absent. This file is the standing guard beside that run: a
checkout that still has the tooling beside it — the archive branch, or a stale working copy —
cannot show the regression by running, and this sweep refuses it by reading.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

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


def reaches_tooling(source: str) -> list[int]:
    """Return the lines where `source` reaches the tooling, static or through an importer."""
    return sorted(node.lineno for node in ast.walk(ast.parse(source)) if _names_tooling(node))


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
        if (lines := reaches_tooling((root / name).read_text(encoding="utf-8")))
    }
    assert found == {}, (
        f"a product test reaches the tooling: {found}. The tooling is not on the main line; "
        f"read what the test needs through a helper under tests/harness/"
    )


# --- the plants: each shape the sweep must refuse, and each it must not ---------------------


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
    assert reaches_tooling(planted) != []


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
    assert reaches_tooling(harmless) == []


def test_the_root_conftest_names_the_tooling_nowhere():
    text = (repository_root() / "conftest.py").read_text(encoding="utf-8")
    named = {
        node.value
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        if _is_tooling(node.value)
    }
    assert named == set(), named
