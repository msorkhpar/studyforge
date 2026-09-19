"""`W366`: which TESTS read the working tree — the `reads_tree` population, test by test.

**What it does.** An import map cannot see a test that OPENS a file: a document, a sweep over
the tree. This module finds those tests from their source, per top-level test function or
class, so a change to a document runs the tests that read documents and not their
neighbours. ⭐ `conftest.py` applies the `reads_tree` marker from THIS rule and the merge
gate's selection uses the same one, so the marker and the selection cannot disagree.

**How you use it.**

    readers = TreeReaders(root)
    readers.nodes("tests/test_repository.py")    # {"test_x", …}, or {WHOLE}
    readers.reads("tests/test_repository.py", "test_x")

**Depends on.** `ast`, `re` and `pathlib` — the standard library — and `tools.testmap` for
module names and imports. ⛔ Nothing from `studyforge` or `tools.quality` (`W310`).

## ⛔ WHAT READS THE TREE

⭐ Source that names one of `TREE_TOKENS` — the root finder, a module's `__file__`, the working
directory, `git ls-files`, or the marker itself, which is how a test the tokens miss is
marked by hand — outside its import lines, and not as a path into `tests/fixtures/` (shared
machinery, which selects everything anyway). ⚠️ It is CONSERVATIVE: `__file__` reading only
`src/` counts too.

## ⛔ HOW A TOKEN REACHES A TEST — by NAME, inside one file

⭐ A top-level function, class or assignment whose own source names a token is TAINTED; so is
every top-level definition that names a tainted one (a helper, a constant, a fixture taken as
an argument), until nothing changes. ⭐ A test is a reader when it is tainted. ⛔ The WHOLE file
reads the tree when a token sits in any other top-level statement, a tainted fixture is
`autouse`, or the file cannot be parsed. ⭐ Names imported from a `tests.` helper that reads
the tree are tainted (never `tests.support`, which DEFINES the root finder), and so are the
tainted names of every conftest above the file, which is how a fixture reaches its tests.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tools.testmap import absolute, imports, is_test_file, module_of

#: What a source names when it reads the working tree rather than an import.
TREE_TOKENS = (
    "repository_root",
    "__file__",
    ".cwd()",
    "ls-files",
    "Path()",
    'Path(".")',
    "mark.reads_tree",
)

#: The helper that DEFINES the root finder; importing it is not reading the tree.
ROOT_FINDER = "tests.support"

#: ⭐ A root finder spelled into the FIXTURE tree is not reading the tree: `tests/fixtures/`
#: is shared machinery, so any change there already selects everything.
FIXTURE_ROOTS = re.compile(
    r'repository_root\(\)\s*/\s*"tests(?:"\s*/\s*"|/)fixtures'
    r'|Path\(__file__\)(?:\.resolve\(\))?(?:\.parent)+\s*/\s*"fixtures"'
)

#: The reading that reaches every test in a file.
WHOLE = "*"

_DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
_ASSIGNMENTS = (ast.Assign, ast.AnnAssign, ast.AugAssign)


def names_a_token(text: str) -> bool:
    """Report whether `text` names a `TREE_TOKENS` entry anywhere but a fixture path."""
    return any(token in FIXTURE_ROOTS.sub("", text) for token in TREE_TOKENS)


def _segment(lines: list[str], node: ast.stmt) -> str:
    """Return the source of `node`, its decorators included."""
    first = min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", ()))])
    return "\n".join(lines[first - 1 : node.end_lineno or node.lineno])


def _referenced(node: ast.AST) -> set[str]:
    """Every name `node` mentions: loads, attributes' bases, and argument (fixture) names."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | {
        n.arg for n in ast.walk(node) if isinstance(n, ast.arg)
    }


def _absolute_from(node: ast.Import | ast.ImportFrom, module: str, path: str) -> str:
    """Return the module a `from … import` names, resolved; `""` for a plain `import`."""
    if not isinstance(node, ast.ImportFrom):
        return ""
    return absolute(node, module, path.endswith("__init__.py"))


def _collectable(node: ast.stmt, lines: list[str]) -> bool:
    """Report whether pytest collects the top-level `node`: a `test*` function or `Test*` class."""
    if isinstance(node, ast.ClassDef):
        return node.name.startswith("Test")
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    decorators = _segment(lines, node).split("def ", 1)[0]
    return node.name.startswith("test") and "fixture" not in decorators


def _targets(node: ast.stmt) -> set[str]:
    """Return the names a top-level definition or assignment binds."""
    if isinstance(node, _DEFINITIONS):
        return {node.name}
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return {n.id for target in targets for n in ast.walk(target) if isinstance(n, ast.Name)}


class TreeReaders:
    """Answers *which tests in this file read the working tree*, parsing only what it must."""

    def __init__(self, root: Path) -> None:
        """Remember `root`; nothing is read until a file is asked about."""
        self.root = root
        self._tainted: dict[str, frozenset[str]] = {}
        #: ⛔ Only what pytest COLLECTS may be named: `file::name` for anything else — a
        #:    `test_cases` list, a fixture called `test_root` — is an error, not a selection.
        self._collected: dict[str, frozenset[str]] = {}

    def reads(self, path: str, name: str = "") -> bool:
        """Report whether test `name` in `path` reads the tree; `""` asks about any test."""
        found = self.nodes(path)
        return WHOLE in found or (name in found if name else bool(found))

    def nodes(self, path: str) -> frozenset[str]:
        """Return the top-level tests in `path` that read the tree, or `{WHOLE}`."""
        tainted = self.tainted(path)
        if WHOLE in tainted:
            return frozenset({WHOLE})
        return frozenset(tainted & self._collected.get(path, frozenset()))

    def tainted(self, path: str) -> frozenset[str]:
        """Every top-level name in `path` that reads the tree, or `{WHOLE}` (see docstring)."""
        if path not in self._tainted:
            self._tainted[path] = frozenset()  # ⭐ A cycle ends here, not in a recursion.
            self._tainted[path] = self._analyse(path)
        return self._tainted[path]

    def _analyse(self, path: str) -> frozenset[str]:
        try:
            source = (self.root / path).read_text(encoding="utf-8")
            tree = ast.parse(source)
        except OSError, SyntaxError, UnicodeDecodeError, ValueError:
            return frozenset({WHOLE})
        lines = source.splitlines()
        self._collected[path] = frozenset(
            node.name for node in tree.body if _collectable(node, lines)
        )
        imported = self._from_helpers(path, tree)
        seeds = set(self._from_conftests(path)) | imported
        if WHOLE in seeds:
            return frozenset({WHOLE})
        bound: list[tuple[set[str], set[str], ast.stmt]] = []
        tainted = set(seeds)
        for node in tree.body:
            prose = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            if isinstance(node, (ast.Import, ast.ImportFrom)) or prose:
                continue  # ⭐ A docstring that MENTIONS the root finder reads nothing.
            own = names_a_token(_segment(lines, node))
            if not isinstance(node, (*_DEFINITIONS, *_ASSIGNMENTS)):
                if own or _referenced(node) & tainted:
                    return frozenset({WHOLE})
                continue
            names = _targets(node)
            if own and "pytestmark" in names:
                return frozenset({WHOLE})
            bound.append((names, _referenced(node), node))
            tainted |= names if own else set()
        grew = True
        while grew:
            grew = False
            for names, refs, _ in bound:
                if refs & tainted and not names <= tainted:
                    tainted |= names
                    grew = True
        for names, _, node in bound:
            if names & tainted and "autouse" in _segment(lines, node).split(":", 1)[0]:
                return frozenset({WHOLE})
        # ⛔ Only what THIS file binds or re-exports: a conftest's names are its own, and a
        #    helper that merely sits beneath one reads nothing by being there.
        local = {n for names, _, _ in bound for n in names} | imported
        return frozenset(tainted & local)

    def _from_conftests(self, path: str) -> frozenset[str]:
        """Return the tainted names of every conftest above `path` (fixtures reach by name)."""
        found: set[str] = set()
        parts = path.split("/")[:-1]
        for depth in range(len(parts) + 1):
            conftest = "/".join([*parts[:depth], "conftest.py"])
            if conftest != path and (self.root / conftest).is_file():
                found |= self.tainted(conftest)
        return frozenset(found)

    def _from_helpers(self, path: str, tree: ast.Module) -> set[str]:
        """Return the names `path` imports from a `tests.` helper that reads the tree."""
        module = module_of(path)
        found: set[str] = set()
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            one = ast.Module(body=[node], type_ignores=[])
            reached = imports(one, module, path.endswith("__init__.py"), None)
            helpers = {n for n in reached if n.startswith("tests.") and n != ROOT_FINDER}
            read = set().union(*(self._helper_reads(helper) for helper in helpers))
            for alias in node.names:
                # ⭐ BY NAME: `from helper import a` is tainted when `a` is, or the module is.
                bound = alias.asname or alias.name.split(".")[0]
                whole = isinstance(node, ast.Import) or WHOLE in read
                if (
                    (read and whole)
                    or alias.name in read
                    or self._helper_reads(f"{_absolute_from(node, module, path)}.{alias.name}")
                ):
                    found.add(bound)
        return found

    def _helper_reads(self, helper: str) -> frozenset[str]:
        """Return the tainted names of the non-test `tests.` module `helper`, or none."""
        stem = helper.replace(".", "/")
        for candidate in (f"{stem}.py", f"{stem}/__init__.py"):
            if (self.root / candidate).is_file() and not is_test_file(candidate):
                return self.tainted(candidate)
        return frozenset()
