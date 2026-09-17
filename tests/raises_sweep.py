"""Read the `RAISES` convention's subject off the tree: who exports, who catches.

⛔ **This module DERIVES; it asserts nothing.** ⭐ The assertions, the reach
floor and the plants live in
[`test_raises_convention.py`](test_raises_convention.py), and the seam between
the two is why this file exists: ⚠️ **the derivation grew past R11's test ceiling
when the floor learned to survive a move (`W219`), and the split is at the line
where reading the tree stops and judging it starts** (Ruling 261).

⭐ What is derived here, and why each derivation rather than a typed list:

- **the exporters** — every module that assigns a `RAISES` tuple or re-exports
  one on a package surface, so the exporter that lands next week is inside the
  sweep with no edit anywhere;
- **each package's readers** — the public routines whose own source can raise
  one of that package's members, so a path join that raises nothing does not
  drag the `try` around it into the sweep;
- **the catch sites** — every `try` outside a package that wraps one of its
  readers, with the tuples its handlers fail to name WHOLE.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path

from tests.support import repository_root

#: The package whose readers let out nothing but exceptions it defines itself,
#: which is why the convention exempts it. Derived nowhere — it is the SUBJECT
#: of the exemption guard, and the guard derives everything it checks about it.
ARCHIVE = "studyforge.archive"


def source_root(root: Path | None = None) -> Path:
    """The package tree a sweep reads: `src/studyforge` under `root`."""
    return (root or repository_root()) / "src" / "studyforge"


def module_name(src: Path, path: Path) -> str:
    """The importable name of `path` inside the package tree rooted at `src`."""
    parts = list(path.relative_to(src.parent).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _assigns(node: ast.stmt, name: str) -> bool:
    """Whether `node` is a module-level assignment binding `name`."""
    if isinstance(node, ast.AnnAssign):
        return isinstance(node.target, ast.Name) and node.target.id == name
    if isinstance(node, ast.Assign):
        return any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
    return False


def exporting_modules(src: Path) -> list[str]:
    """Every module that exports a `RAISES` tuple, read off the tree.

    ⛔ Two shapes, because both are in use: the module that ASSIGNS the tuple
    (`serve/discovery.py`), and the package `__init__.py` that re-exports one it
    imported and names it in `__all__` (`serve/__init__.py`). ⚠️ A module that
    merely imports `RAISES` to catch it — `cli/site/cli.py` — is a CALLER and
    must not read as an exporter, which is why the second shape wants `__all__`.
    """
    found = []
    for path in sorted(src.rglob("*.py")):
        body = ast.parse(path.read_text("utf-8")).body
        exported = any(_assigns(node, "RAISES") for node in body)
        if not exported and path.name == "__init__.py":
            exported = any(
                isinstance(element, ast.Constant) and element.value == "RAISES"
                for node in body
                if isinstance(node, ast.Assign) and _assigns(node, "__all__")
                for element in ast.walk(node.value)
            )
        if exported:
            found.append(module_name(src, path))
    return found


def _raising_routines(package: str, members: set[str]) -> set[tuple[str, str]]:
    """`(module, function)` for every top-level def in `package` that can raise a member.

    ⭐ Direct raises first, then a fixpoint over calls made inside the package,
    so `load` counts because it calls `parse`. ⚠️ Subclasses of a member defined
    in the package count as the member, since catching the tuple catches them.
    """
    origin = Path(importlib.import_module(package).__file__)
    inside = origin.name == "__init__.py"
    files = sorted(origin.parent.rglob("*.py")) if inside else [origin]
    trees = {}
    for path in files:
        tree = ast.parse(path.read_text("utf-8"))
        parts = list(path.relative_to(origin.parent).with_suffix("").parts) if inside else []
        if parts and parts[-1] == "__init__":
            parts.pop()
        trees[".".join([package, *parts])] = tree
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Name) and base.id in members for base in node.bases
            ):
                members = members | {node.name}
    raises, calls, by_name = {}, {}, {}
    for where, tree in trees.items():
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            key = (where, node.name)
            raises[key] = any(
                (
                    isinstance(thrown.exc, ast.Call)
                    and isinstance(thrown.exc.func, ast.Name)
                    and thrown.exc.func.id in members
                )
                or (isinstance(thrown.exc, ast.Name) and thrown.exc.id in members)
                for thrown in ast.walk(node)
                if isinstance(thrown, ast.Raise) and thrown.exc is not None
            )
            calls[key] = {
                call.func.id
                for call in ast.walk(node)
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            }
            by_name.setdefault(node.name, []).append(key)
    settled = False
    while not settled:
        settled = True
        for key, already in list(raises.items()):
            if already:
                continue
            if any(raises[other] for callee in calls[key] for other in by_name.get(callee, ())):
                raises[key], settled = True, False
    return {key for key, thrown in raises.items() if thrown}


def readers_of(package: str, members: set[str]) -> set[str]:
    """The public routines `package` exports that can raise one of `members`."""
    module = importlib.import_module(package)
    raising = _raising_routines(package, members)
    public = getattr(module, "__all__", None) or [n for n in dir(module) if not n.startswith("_")]
    return {
        name
        for name in public
        if inspect.isroutine(getattr(module, name, None))
        and (getattr(module, name).__module__, getattr(module, name).__name__) in raising
    }


@dataclass(frozen=True)
class Population:
    """Which modules export a tuple, under which name, and what their readers are."""

    #: Every exporting module, mapped to the canonical name of its tuple. ⭐ Two
    #: modules that export the SAME tuple object — `serve` and `serve.discovery`
    #: — share one canonical name, so a caller importing the reader from one and
    #: the tuple from the other still reads as naming it.
    canonical: dict[str, str]
    #: Canonical name → the reader names a caller may wrap in a `try`.
    readers: dict[str, frozenset[str]]


def population(src: Path) -> Population:
    """Derive the sweep's subject from the tree: who exports a tuple, and their readers."""
    groups: dict[int, list[str]] = {}
    tuples: dict[int, tuple] = {}
    for name in exporting_modules(src):
        thrown = getattr(importlib.import_module(name), "RAISES", None)
        if not isinstance(thrown, tuple) or not thrown:
            continue
        groups.setdefault(id(thrown), []).append(name)
        tuples[id(thrown)] = thrown
    canonical, readers = {}, {}
    for key, names in groups.items():
        # ⭐ The shortest name in the group is the package surface a caller meets.
        chosen = min(names, key=lambda name: (len(name), name))
        members = {kind.__name__ for kind in tuples[key]}
        found: set[str] = set()
        for name in names:
            canonical[name] = chosen
            found |= readers_of(name, members)
        readers[chosen] = frozenset(found)
    return Population(canonical, readers)


def names_the_tuple(held: ast.expr, bound: dict[str, frozenset[str]]) -> set[str]:
    """The tuples an expression names WHOLE, by the local names in `bound`.

    ⛔ The `W219` predicate, and the point of the whole row. A bare `RAISES`
    counts, and so does `*RAISES` inside a tuple literal — the two forms the
    tree uses. ⚠️ `RAISES[:1]` is an `ast.Subscript` and counts as naming
    NOTHING: a narrowed tuple is the defect, so it may not read as the tuple.

    ⭐ Asked of a handler's exception expression, and of the right-hand side of
    a module-level assignment, which is how a widened alias is read — see
    `tuple_names_bound_in`.
    """
    named: set[str] = set()
    for element in held.elts if isinstance(held, ast.Tuple) else [held]:
        inner = element.value if isinstance(element, ast.Starred) else element
        if isinstance(inner, ast.Name) and inner.id in bound:
            named |= bound[inner.id]
    return named


def tuple_names_bound_in(tree: ast.Module, imported: dict[str, str]) -> dict[str, frozenset[str]]:
    """Every local name that carries a whole tuple: the imports, plus the aliases.

    ⛔ **A caller may widen the tuple before catching it**, and
    `skills/onboarding/standing.py` does: `REFUSED = (*RAISES, ContentError,
    ArchiveError)`, then `except REFUSED`. ⭐ That names the tuple WHOLE and must
    read as naming it — the widening adds arms, it removes none. ⚠️ **The alias is
    read by the same predicate as the handler**, so `(*RAISES[:1], ...)` binds
    nothing and the narrowing is not laundered through a module constant.
    """
    bound = {name: frozenset({chosen}) for name, chosen in imported.items()}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and node.value is not None:
            targets: list[ast.expr] = [node.target]
        elif isinstance(node, ast.Assign):
            targets = list(node.targets)
        else:
            continue
        carried = names_the_tuple(node.value, bound)
        if not carried:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                bound[target.id] = frozenset(carried)
    return bound


@dataclass(frozen=True)
class CatchSite:
    """One `try` around another package's reader: what it catches, what it fails to name."""

    #: Canonical names of the packages whose reader is called inside the `try`.
    caught: frozenset[str]
    #: Of those, the ones no handler names WHOLE — the convention's failure.
    retyped: frozenset[str]


def catch_sites(src: Path, subject: Population) -> dict[str, CatchSite]:
    """`{path:function: CatchSite}` for every `try` around a reader of an exporting package."""
    sites: dict[str, CatchSite] = {}
    for path in sorted(src.rglob("*.py")):
        rel = path.relative_to(src).as_posix()
        me = module_name(src, path)
        tree = ast.parse(path.read_text("utf-8"))
        readers, imported = {}, {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module not in subject.canonical:
                continue
            chosen = subject.canonical[node.module]
            # ⛔ A package's own modules are not callers of its surface.
            if me == chosen or me.startswith(f"{chosen}."):
                continue
            for alias in node.names:
                local = alias.asname or alias.name
                if alias.name in subject.readers[chosen]:
                    readers[local] = chosen
                elif alias.name == "RAISES":
                    imported[local] = chosen
        bound = tuple_names_bound_in(tree, imported)
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for node in ast.walk(function):
                if not isinstance(node, ast.Try):
                    continue
                called = {
                    readers[call.func.id]
                    for statement in node.body
                    for call in ast.walk(statement)
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id in readers
                }
                if not called:
                    continue
                named: set[str] = set()
                for handler in node.handlers:
                    if handler.type is not None:
                        named |= names_the_tuple(handler.type, bound)
                sites[f"{rel}:{function.name}"] = CatchSite(
                    frozenset(called), frozenset(called - named)
                )
    return sites


def reach(sites: dict[str, CatchSite]) -> dict[str, int]:
    """How many catch sites the sweep reaches for each subject package.

    ⛔ **The floor's key, and everything a legitimate move changes is absent from
    it** (`W219`). A declared split moves a reader between modules and may rename
    it, so neither the path nor the function name can identify a site across one;
    what survives is WHICH package's tuple is being caught, and how many callers
    the sweep still finds catching it.
    """
    counted: dict[str, int] = {}
    for site in sites.values():
        for chosen in site.caught:
            counted[chosen] = counted.get(chosen, 0) + 1
    return counted


def population_report(sites: dict[str, CatchSite]) -> str:
    """Every site the sweep found and what it caught, for a failure to print.

    ⛔ A count alone hides WHICH site vanished, so no assertion over `reach`
    reports a shortfall without this beside it.
    """
    return "; ".join(f"{where} -> {sorted(site.caught)}" for where, site in sorted(sites.items()))
