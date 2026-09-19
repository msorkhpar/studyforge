"""`W366`: which test files a changed path can reach — an import map, and the tree readers.

**What it does.** Parses every Python file under `src/`, `tools/` and `tests/` with `ast`,
records what each one imports, and answers the question the merge gate's selection asks of
a changed module: *which test files import it, transitively* (`TestMap.dependents`).

**How you use it.**

    tests = TestMap.build(root).dependents({"studyforge.render.page"})

`module_of(path)` names the module a repository path is, or `""` when it is none.

**Depends on.** `ast`, `dataclasses` and `pathlib` — the standard library, and nothing else:
it is on the merge path, which may import neither `studyforge` nor `tools.quality` (`W310`).

## ⛔ WHAT COUNTS AS AN IMPORT — deliberately MORE than the `import` statement

- ⭐ `import a.b.c` imports `a`, `a.b` and `a.b.c`: every parent package's `__init__` runs.
- ⭐ `from a.b import c` imports `a.b`, and `a.b.c` whenever that names a module.
- ⭐ A STRING equal to a module's name counts — `["python3", "-m", "tools.quality"]` and
  `import_module("studyforge.cli")` reach the module no less than an import does.
- ⭐ An f-string that STARTS with a package's name and a dot reaches every module under it.
- ⛔ A name that no longer resolves is KEPT when it is repository-local: a test importing a
  module the branch DELETED is exactly the test that must run.

## ⛔ WHAT IT CANNOT SEE

⭐ A test that READS a file rather than importing it. `tools/treereaders.py` finds those —
the `reads_tree` population — and the full-suite AUDIT (`tools/selection.py`) exists for
whatever both miss.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

#: The directories whose Python files are modules, and the prefix `src/` drops from a name.
MODULE_ROOTS = ("src", "tools", "tests")

#: The top-level packages that are this repository's own. ⭐ A name under one is kept even
#: when it no longer resolves, because the module that went missing is the change.
LOCAL = ("studyforge", "tools", "tests")

#: ⛔ Never parsed as modules: fixture corpora are data, and shared machinery besides.
NOT_MODULES = ("tests/fixtures/",)


def module_of(path: str) -> str:
    """Return the dotted module a repository-relative `path` is, or `""` when it is none."""
    if not path.endswith(".py") or path.startswith(NOT_MODULES):
        return ""
    parts = path[: -len(".py")].split("/")
    if parts[0] not in MODULE_ROOTS:
        return ""
    if parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def is_test_file(path: str) -> bool:
    """Report whether `path` is a file pytest collects under this repository's `testpaths`."""
    name = path.rsplit("/", 1)[-1]
    return (
        path.startswith(("tests/", "tools/tests/"))
        and name.startswith("test_")
        and (name.endswith(".py"))
    )


def is_conftest(path: str) -> bool:
    """Report whether `path` is a pytest conftest, which every test beneath it loads."""
    return path.rsplit("/", 1)[-1] == "conftest.py"


def _parse(path: Path) -> ast.Module | None:
    """Parse `path`, or return None when it cannot be read or is not valid Python."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except OSError, SyntaxError, UnicodeDecodeError, ValueError:
        return None


def absolute(node: ast.ImportFrom, module: str, package: bool) -> str:
    """Resolve a `from … import` to the absolute name it imports from."""
    if not node.level:
        return node.module or ""
    anchor = module.split(".") if package else module.split(".")[:-1]
    anchor = anchor[: len(anchor) - (node.level - 1)] if node.level > 1 else anchor
    return ".".join([*anchor, *([node.module] if node.module else [])])


def _with_parents(names: Iterable[str]) -> set[str]:
    """Every name with every parent package, because importing `a.b` runs `a` too."""
    return {
        ".".join(name.split(".")[:end]) for name in names for end in range(1, name.count(".") + 2)
    }


def imports(tree: ast.Module, module: str, package: bool, known: frozenset[str] | None) -> set[str]:
    """Return every repository-local module name `tree` reaches (see the docstring).

    ⭐ `known=None` keeps EVERY `from a import b` as a candidate `a.b` and reads no string:
    the answer a caller that has not parsed the whole tree can still check on disk.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            base = absolute(node, module, package)
            names.add(base)
            candidates = {f"{base}.{alias.name}" for alias in node.names}
            names |= candidates if known is None else candidates & known
        elif known is None:
            continue
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in known:
            # ⚠️ A BARE package name is prose far more often than a target: `"studyforge"` in
            #    a message would make every module that says it depend on the whole package.
            if "." in node.value or module.split(".")[-1].startswith("test_"):
                names.add(node.value)
        elif isinstance(node, ast.JoinedStr) and node.values:
            head = node.values[0]
            if isinstance(head, ast.Constant) and str(head.value).endswith("."):
                prefix = str(head.value)
                names |= {name for name in known if name.startswith(prefix)}
    # ⭐ The tree's own top-level packages are local too, whatever `src/` holds.
    local = set(LOCAL) | {name.split(".")[0] for name in known or ()}
    return {name for name in _with_parents(n for n in names if n) if name.split(".")[0] in local}


def _python_files(root: Path) -> list[str]:
    """Every module file under `MODULE_ROOTS`, repository-relative, caches and fixtures skipped."""
    found = []
    for top in MODULE_ROOTS:
        for path in sorted((root / top).rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            if "__pycache__" in relative or relative.startswith(NOT_MODULES):
                continue
            found.append(relative)
    return found


@dataclass
class TestMap:
    """The import graph of one tree: module → the modules it imports, and the test files."""

    #: Module name → repository-relative file.
    files: dict[str, str] = field(default_factory=dict)
    #: Module name → the names it imports (repository-local, parents included).
    edges: dict[str, set[str]] = field(default_factory=dict)
    #: The collected test files, repository-relative.
    tests: tuple[str, ...] = ()

    __test__ = False  # ⛔ Not a pytest class, whatever its name says.

    @classmethod
    def build(cls, root: Path) -> TestMap:
        """Parse every module file under `root` and return its import graph."""
        paths = _python_files(root)
        files = {module_of(p) or p[: -len(".py")]: p for p in paths}
        known = frozenset(files)
        edges = {}
        for name, path in files.items():
            tree = _parse(root / path)
            package = path.endswith("__init__.py")
            edges[name] = set() if tree is None else imports(tree, name, package, known) - {name}
        return cls(
            files=files,
            edges=edges,
            tests=tuple(sorted(p for p in paths if is_test_file(p))),
        )

    def dependents(self, names: Iterable[str]) -> set[str]:
        """Every TEST FILE that is one of `names` or imports one of them, transitively."""
        reverse: dict[str, set[str]] = {}
        for importer, imported in self.edges.items():
            for name in imported:
                reverse.setdefault(name, set()).add(importer)
        seen: set[str] = set()
        pending = list(names)
        while pending:
            name = pending.pop()
            if name not in seen:
                seen.add(name)
                pending.extend(reverse.get(name, ()))
        tests = set(self.tests)
        return {self.files[name] for name in seen if self.files.get(name) in tests}
