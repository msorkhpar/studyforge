"""The three isolation assertions, as predicates something can be planted against.

**What it does.** Answers three questions about the framework, each of which is
one careless line away from being false, and each as a **population** rather than
a boolean so that a reader can see what was looked at before they read a verdict:

| Question | Here | Given teeth by |
|---|---|---|
| Does the serving package name a way to start a process? | `spawn_reach` | a plant per door |
| Does a module import outside the standard library and itself? | `foreign_imports` | a plant |
| Does a framework module reach a module **by name at run time**? | `dynamic_imports` | a plant |

⚠️ **The index's isolation is not here**, because it cannot be answered by reading
source: a renderer that reads a file produces identical bytes and imports nothing
unusual. It is observed instead — `tests/harness/probes/audit.py`, and
`outside_roots` below is the verdict half of it.

**How you use it.**

    from tests.harness import isolation

    isolation.spawn_reach(isolation.serve_modules())     # [] — the serving package
    isolation.foreign_imports(isolation.framework_modules())
    isolation.dynamic_imports(isolation.framework_modules())

**Depends on.** `ast` and `sys` — the standard library; the tree walk is its own.
⛔ Nothing from `studyforge`: a check on what the framework imports may not begin
by importing the framework.

## ⛔ Why a dynamic-import door exists at all

⚠️ R1's import form is enumerated positively — *every import root is in the
standard library or is `studyforge`* — and that is a closed set nobody can argue
with. ⛔ But `importlib.import_module(name)` is in the standard library, so a
framework module could reach a corpus-specific package with **no** import
statement to catch, and both the closed-set check and the floor's
source-name sweep would be silent. ⭐ The third door is the one that is open
today; it is asserted empty rather than policed, because a framework that never
needs a run-time import is a stronger statement than a list of permitted ones.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from tests.support import repository_root

#: Where the framework lives, and the whole of what these predicates bind.
FRAMEWORK = "src"

#: The serving package, relative to the repository root. ⚠️ A skeleton today
#: (spec §8.3's rule arrives before the routes do), which is why the population
#: is printed: a check over nothing returns the pass reading.
SERVE = "src/studyforge/serve"

#: Modules whose mere import is a way to start a process.
SPAWN_MODULES = ("subprocess", "multiprocessing", "pty")

#: `os` members that start one. ⛔ Prefixes, because the family is wide: `execv`,
#: `execve`, `execlp`, `spawnv`, `posix_spawnp` are one door each.
SPAWN_PREFIXES = ("system", "popen", "exec", "fork", "spawn", "startfile")

#: `asyncio` members that start one.
ASYNC_SPAWN = ("create_subprocess_exec", "create_subprocess_shell")

#: How a module is reached by name at run time. ⛔ The door no import check sees.
DYNAMIC = ("importlib", "__import__")

#: Import roots the framework may take: the standard library, and itself. ⭐ A
#: closed, positive set — the one shape of this rule that cannot be evaded by
#: spelling, unlike a list of what is forbidden.
ALLOWED_ROOTS = frozenset(sys.stdlib_module_names) | {"studyforge"}


@dataclass(frozen=True)
class Module:
    """One Python file under the framework, with its path relative to the root.

    ⛔ The relative name is what every message carries: an absolute one would put
    somebody's home directory into a failure (R7).
    """

    name: str
    text: str

    @property
    def tree(self) -> ast.Module:
        """The parsed module."""
        return ast.parse(self.text, filename=self.name)


def framework_modules(root: Path | None = None) -> tuple[Module, ...]:
    """Every Python module under `src/`, sorted by name."""
    return _modules(root, FRAMEWORK + "/")


def serve_modules(root: Path | None = None) -> tuple[Module, ...]:
    """Every Python module of the serving package, sorted by name."""
    return _modules(root, SERVE + "/")


def spawn_reach(modules: tuple[Module, ...]) -> list[str]:
    """Every place one of `modules` names a way to start a process.

    Three doors, because a check that watched one would be walked around by
    whichever of the other two the next author happened to reach for:

    1. `import subprocess` — the module itself;
    2. `os.system(...)`, `os.execv(...)` — an attribute on an imported module;
    3. `from os import system` then `system(...)` — the name, imported bare.

    ⛔ Reported by line, with the spelling that was found, so the message names
    the module and not the subsystem.
    """
    found: list[str] = []
    for module in modules:
        tree = module.tree
        bare = _names_imported_from(tree)
        for node in ast.walk(tree):
            door = _spawn_door(node, bare)
            if door is not None:
                found.append(f"{module.name}:{node.lineno}: {door}")
    return sorted(found)


def foreign_imports(modules: tuple[Module, ...]) -> list[str]:
    """Every import in `modules` whose root is neither standard library nor `studyforge`.

    ⭐ R1's import form, and the reason the whole source-agnostic claim is
    checkable rather than aspirational: a corpus-specific package cannot be
    imported without appearing here.
    """
    found: list[str] = []
    for module in modules:
        for node in ast.walk(module.tree):
            for root in _import_roots(node):
                if root not in ALLOWED_ROOTS:
                    found.append(f"{module.name}:{node.lineno}: {root}")
    return sorted(found)


def dynamic_imports(modules: tuple[Module, ...]) -> list[str]:
    """Every place `modules` reach a module by name at run time rather than by import."""
    found: list[str] = []
    for module in modules:
        tree = module.tree
        bare = _names_imported_from(tree)
        for node in ast.walk(tree):
            spelling = _dynamic_door(node, bare)
            if spelling is not None:
                found.append(f"{module.name}:{node.lineno}: {spelling}")
    return sorted(found)


def outside_roots(opened: tuple[str, ...], allowed: tuple[Path, ...]) -> list[str]:
    """Every observed read whose path sits under none of `allowed`.

    ⚠️ The input is `tests/harness/probes/audit.py`'s record: one `event\\tpath`
    per line. ⛔ A record entry that is not a path at all — `os.open` on an
    already-open descriptor reports the integer — is *not* a read of a file and
    is not reported, which is stated here because silence needs a reason.
    """
    roots = tuple(str(path) for path in allowed)
    found: list[str] = []
    for entry in opened:
        event, _, where = entry.partition("\t")
        if not where.startswith("/"):
            continue
        if not any(where.startswith(root) for root in roots):
            found.append(f"{event}: {where}")
    return sorted(found)


#: ⭐ What the walk never reads — build output, tool caches and version control, the
#: floor's own `TOOL_OUTPUT_DIRS` — so the walk needs no tooling. Every prefix walked here is
#: under `src/`, where the floor's other exclusion (`tests/fixtures`) cannot occur.
WALK_SKIPS = frozenset(
    {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        ".pytest_cache",
        ".ruff_cache",
        "build",
        "dist",
        "node_modules",
    }
)


def _modules(root: Path | None, prefix: str) -> tuple[Module, ...]:
    """Every module under `prefix`, read once, sorted by relative name."""
    where = repository_root() if root is None else root
    found = []
    for path in (where / prefix).rglob("*.py"):
        name = path.relative_to(where).as_posix()
        if path.is_file() and not WALK_SKIPS & set(name.split("/")):
            found.append(Module(name=name, text=path.read_text(encoding="utf-8")))
    return tuple(sorted(found, key=lambda module: module.name))


def _import_roots(node: ast.AST) -> list[str]:
    """The root package of every module an import node names."""
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.level == 0:
        return [(node.module or "").split(".")[0]]
    return []


def _names_imported_from(tree: ast.Module) -> dict[str, str]:
    """`bare name -> module it came from`, for every `from x import y` in `tree`."""
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                found[alias.asname or alias.name] = node.module
    return found


def _spawn_door(node: ast.AST, bare: dict[str, str]) -> str | None:
    """Which of the three doors `node` is, or None."""
    for root in _import_roots(node):
        if root in SPAWN_MODULES:
            return f"imports {root}"
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == "os" and node.attr.startswith(SPAWN_PREFIXES):
            return f"os.{node.attr}"
        if node.value.id == "asyncio" and node.attr in ASYNC_SPAWN:
            return f"asyncio.{node.attr}"
    if isinstance(node, ast.Name) and _is_spawn_name(node.id, bare):
        return f"{bare[node.id]}.{node.id}, imported bare"
    return None


def _is_spawn_name(name: str, bare: dict[str, str]) -> bool:
    """Whether `name` was imported bare out of a module that can start a process."""
    came_from = bare.get(name)
    if came_from is None:
        return False
    root = came_from.split(".")[0]
    if root in SPAWN_MODULES:
        return True
    return (root == "os" and name.startswith(SPAWN_PREFIXES)) or (
        root == "asyncio" and name in ASYNC_SPAWN
    )


def _dynamic_door(node: ast.AST, bare: dict[str, str]) -> str | None:
    """Whether `node` reaches a module by name at run time."""
    for root in _import_roots(node):
        if root in DYNAMIC:
            return f"imports {root}"
    if isinstance(node, ast.Name):
        if node.id == "__import__":
            return "calls __import__"
        if bare.get(node.id, "").split(".")[0] in DYNAMIC:
            return f"{bare[node.id]}.{node.id}, imported bare"
    return None
