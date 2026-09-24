r"""`W199/3` tree-wide: a name one package takes from another reaches a DECLARED surface.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout. It began as a copy of the developer tooling's check; that tooling, and its
records, live on the branch `archive/process`, and nothing here depends on them.

**What it does.** Reads every cross-package import under `src/studyforge` and asks
Ruling 101's producer-half question of each one: is the name the importer takes on the
OWNING package's `__all__`? ⛔ Each package's surface is read from THAT PACKAGE, never
from a table here, so the check cannot disagree with the tree about what is exported.

**How you use it.** `check_producer_half(root)` is registered in `tests.floor.CHECKS`
and `surface_census(root)` in `NOTICES`. `reaches(root)` is the reading both are built
on, and `packages(root)` is every package under `src/studyforge` with the surface it
declares (`None` when it declares none).

**Depends on.** `ast`, `dataclasses` and `pathlib`; `config` for the walk's exclusions
and repo-relative paths, `report` for the answer, and `deviations` for the declared
population — `DECLARED` and `Declaration` are re-exported here so a caller needs one
import. ⛔ The seam runs ONE WAY: this module reads that one, and that one reads nothing
back. Standard library only.

## ⛔ THE PIN ARM IS THE HALF THAT DOES NOT DEPEND ON A CONSUMER'S SPELLING

⚠️ **Ruling 101 has two remedies and they are IN TENSION** (measured on the change that
hit it). Its table tells a consumer to import from the PACKAGE once the name is
exported — and a sweep defined over SUBMODULE imports can only hold a name while some
consumer still spells it the deviating way. ⛔ **So fixing a spelling removes the name
from the only instrument holding it on the surface, and nothing goes red.**

⭐ **This module answers that by reading BOTH spellings and asking the same question of
each.** `from studyforge.validate.corpus import Held` and `from studyforge.validate
import Held` both require `Held` on `studyforge.validate.__all__`. ⛔ **A spelling fix
therefore MOVES a name between this module's two arms and never out of its grip**, which
is the property a tree-wide sweep had to land BEFORE any spelling is touched.

## ⛔ THE POPULATION IS CLOSED AT THE REF IT WAS TAKEN AT

⭐ **`deviations.DECLARED` carries the deviations this tree already had, each with the
ground it stands declared on.** ⛔ **A pair that is NOT declared is a finding, and a
declared pair that is GONE is also a finding** — so clearing a deviation is a deliberate
edit that deletes its entry, and the declaration cannot outlive the thing it excuses.
⚠️ **Adding an entry to quiet a red is declaring a defect, not fixing one** (`W199`'s
rule, inherited unchanged).

## ⚠️ WHAT THIS INSTRUMENT CANNOT SEE, SAID BY IT RATHER THAN DISCOVERED

⛔ **It reads a NAME against a surface; it never reads a VALUE.** A package exporting the
wrong object under the right name passes here, exactly as `W298`'s mint scan stayed green
under a value-change plant. ⭐ The behavioural pins are what answer that, and retiring one
because this is green would be reading this as a guard it is not.

⛔ **And it does not fail Ruling 101's FIRST row.** A name that IS exported and is taken
by the submodule spelling is a one-line deviation; it is counted and PRINTED by
`surface_census` and never turned into a finding. ⚠️ The ground: that
population is landed code no office has been assigned, and a red run for a condition
nobody may clear is a red run that gets muted.

## ⚠️ WHAT IT DECIDES, AND WHAT IT DECLARES

⭐ **Decided:** a `from studyforge.<…> import <name>` with no leading dot, in a module
under `src/studyforge`, whose owning package is neither the importer's own package nor an
ancestor segment of it. ⛔ **A sub-package is its own owner** — `validate.source` states
its own `__all__`, so importing from it reaches no past surface — and a name that is a
MODULE of the package it is taken from is an import of that module, not of a surface name.

⚠️ **Declared, not decided, and each is asserted in the mirror:**

1. `import studyforge.a.b` and the attribute expressions after it. ⛔ MEASURED at
   `2827409`: this tree writes that form nowhere, and every cross-package import is a
   `from` import. A tree that started writing it would be read by nothing here.
2. A re-export: a package whose `__init__` takes the name and lists it is ON its surface,
   and this module cannot tell that from a definition. ⭐ That is Ruling 101's own answer
   (`W199`'s rider), not a gap in the reading.
3. `tests/`. R1 binds framework source and Ruling 101 governs packages; a
   test reaching into a module is a test of that module.
4. A conditional or function-local import. The walk reads every `ImportFrom` in the tree,
   so one inside a function IS read — what is not read is whether it ever runs.
5. An EMPTY population is reported through the notice rather than failed. The floor runs
   over a corpus, a consumer repository and an installed tree, and none of those owes a
   `src/studyforge` (an empty population is a disclosure, never a pass). ⛔ The real tree's
   population is pinned in the mirror instead, so a walk that reads nothing cannot pass
   here as a clean bill.
6. A declaration whose package is absent from the walked tree is not read at all, so a
   synthetic tree is never failed for lacking this repository's packages.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from tests.floor import config
from tests.floor.deviations import DECLARED, Declaration
from tests.floor.report import Finding

RULE_UNDECLARED = "surface-undeclared"
RULE_REACHED_PAST = "surface-reached-past"
RULE_DECLARATION = "surface-declaration"

#: The package tree Ruling 101 governs, relative to the repository root.
PACKAGE_ROOT = "studyforge"


@dataclass(frozen=True)
class Reach:
    """One name a package takes from another package, and the spelling it was taken by."""

    importer: str
    line: int
    owner: str
    module: str
    name: str
    on_surface: bool


def _surface(init: Path) -> frozenset[str] | None:
    """Return the names a package declares on `__all__`, or None when it declares none.

    ⛔ None and an EMPTY frozenset are different answers and are kept apart: a package
    with no `__all__` has no surface to be reached past, which is a different defect from
    one whose surface omits a name.
    """
    try:
        tree = ast.parse(init.read_text(encoding="utf-8"))
    except OSError, SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    return frozenset(ast.literal_eval(node.value))
                except TypeError, ValueError:
                    return None
    return None


def packages(root: Path) -> dict[str, frozenset[str] | None]:
    """Return every package under `src/studyforge`, mapped to the surface it declares."""
    source = root / "src"
    top = source / PACKAGE_ROOT
    found: dict[str, frozenset[str] | None] = {}
    if not top.is_dir():
        return found
    for init in sorted(top.rglob("__init__.py")):
        if config.is_excluded(config.relative(init, root)):
            continue
        found[".".join(init.parent.relative_to(source).parts)] = _surface(init)
    return found


def _owner_of(dotted: str, known: dict[str, frozenset[str] | None]) -> tuple[str, str]:
    """Return the package that owns `dotted`, and the module it names, or two empties.

    ⭐ A dotted name that IS a package is its own owner and names no module; one whose
    parent is a package is that package's module. Anything else belongs to no package here.
    """
    if dotted in known:
        return dotted, ""
    parent = dotted.rpartition(".")[0]
    return (parent, dotted) if parent in known else ("", "")


def _is_submodule(root: Path, owner: str, name: str) -> bool:
    """Report whether `name` is a module or sub-package of `owner` rather than a surface name."""
    directory = root / "src" / Path(*owner.split("."))
    return (directory / f"{name}.py").is_file() or (directory / name / "__init__.py").is_file()


def reaches(root: Path) -> list[Reach]:
    """Return every name a package under `src/studyforge` takes from another package.

    ⛔ BOTH spellings, and that is the module's whole point — see the contract above.
    A `Reach` whose `module` is empty was taken from the package itself.
    """
    known = packages(root)
    source = root / "src"
    found: list[Reach] = []
    if not known:
        return found
    for path in sorted((source / PACKAGE_ROOT).rglob("*.py")):
        relative = config.relative(path, root)
        if config.is_excluded(relative):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except OSError, SyntaxError:
            continue
        importer = ".".join(path.relative_to(source).parts[:-1])
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
                continue
            owner, module = _owner_of(node.module, known)
            if not owner or importer == owner or importer.startswith(owner + "."):
                continue
            surface = known[owner]
            for alias in node.names:
                on_surface = surface is not None and alias.name in surface
                if not module and not on_surface and _is_submodule(root, owner, alias.name):
                    continue
                found.append(Reach(relative, node.lineno, owner, module, alias.name, on_surface))
    return found


def _undeclared(reach: Reach) -> Finding:
    """Return the finding for a name taken from a package that does not export it."""
    return Finding(
        path=reach.importer,
        line=reach.line,
        rule=RULE_UNDECLARED,
        message=(
            f"{reach.name!r} is taken from {reach.owner} and is not on that package's "
            f"__all__. Ruling 101's producer half: export it from {reach.owner}, or the "
            f"two packages do not share it."
        ),
    )


def _reached_past(reach: Reach) -> Finding:
    """Return the finding for a name taken from a MODULE of a package that does not export it."""
    return Finding(
        path=reach.importer,
        line=reach.line,
        rule=RULE_REACHED_PAST,
        message=(
            f"{reach.name!r} is taken from the module {reach.module} and is on no surface "
            f"of {reach.owner}. Ruling 101: export it, or the two packages do not share "
            f"it. ⛔ Declaring it in deviations.DECLARED to quiet this is declaring a "
            f"defect, not fixing one (W199, W300)."
        ),
    )


def _stale(known: dict[str, frozenset[str] | None], live: set[tuple[str, str]]) -> list[Finding]:
    """Return a finding for every declared deviation this tree no longer has.

    ⛔ This is what CLOSES the population at its ref: a fix deletes its own entry, so a
    declaration can never outlive the deviation it excuses. ⚠️ A declaration whose package
    is absent from the walked tree is skipped, so a synthetic tree is never failed here.
    """
    findings: list[Finding] = []
    for owner, declaration in sorted(DECLARED.items()):
        if owner not in known:
            continue
        for name in sorted(declaration.names - {n for o, n in live if o == owner}):
            findings.append(
                Finding(
                    path="src/" + owner.replace(".", "/") + "/__init__.py",
                    line=0,
                    rule=RULE_DECLARATION,
                    message=(
                        f"deviations.DECLARED still declares {name!r} off {owner}'s "
                        f"surface and nothing takes it from a module there any more. "
                        f"Delete the entry: the population is closed at the ref it is "
                        f"taken at, and a declaration that outlives its deviation "
                        f"excuses nothing (W300)."
                    ),
                )
            )
    return findings


def check_producer_half(root: Path) -> list[Finding]:
    """Return a finding for every name shared between packages that is on no declared surface.

    ⛔ Two arms and one question. The PIN arm binds the PACKAGE spelling, so it holds a
    name on its owner's surface however a consumer spells the import. The SWEEP
    arm binds the MODULE spelling against `DECLARED`, both ways.
    """
    known = packages(root)
    findings: list[Finding] = []
    live: set[tuple[str, str]] = set()
    for reach in reaches(root):
        if reach.on_surface:
            continue
        if not reach.module:
            findings.append(_undeclared(reach))
            continue
        live.add((reach.owner, reach.name))
        declared = DECLARED.get(reach.owner)
        if declared is None or reach.name not in declared.names:
            findings.append(_reached_past(reach))
    return findings + _stale(known, live)


def surface_census(root: Path) -> list[str]:
    """Print the walked population, the declared deviations, and the spelling backlog.

    ⛔ A sweep states its denominator: `0 findings` is `0 = 0` until it says out of how
    many. ⭐ The spelling backlog is printed here and failed nowhere — see the contract's
    account of what this instrument deliberately does not fail.
    """
    known = packages(root)
    if not known:
        return [
            "producer half (W199/3): no src/studyforge under this root, so no package was "
            "read. This is not a failure — the floor runs over trees that are not this one."
        ]
    found = reaches(root)
    off = {(reach.owner, reach.name) for reach in found if reach.module and not reach.on_surface}
    spelling = {(reach.owner, reach.name) for reach in found if reach.module and reach.on_surface}
    surfaced = sum(1 for surface in known.values() if surface is not None)
    lines = [
        f"producer half (W199/3): {len(known)} package(s) under src/{PACKAGE_ROOT}, "
        f"{surfaced} declaring a surface; {len(found)} cross-package import(s) read, "
        f"{len(off)} (package, name) pair(s) off a surface and declared, "
        f"{len(spelling)} on a surface by the SUBMODULE spelling. ⚠️ A name is read "
        f"against a surface and never a VALUE: this is not a value guard (W298/3)."
    ]
    for owner, declaration in sorted(DECLARED.items()):
        if owner not in known:
            continue
        lines.append(f"  {owner}: {len(declaration.names)} declared — {declaration.ground}")
    if spelling:
        lines.append(
            "  Ruling 101's FIRST row, printed and never failed — the name IS exported and "
            "only the spelling deviates (W299/3), one line each:"
        )
        for owner in sorted({owner for owner, _ in spelling}):
            names = ", ".join(sorted(name for holder, name in spelling if holder == owner))
            lines.append(f"    {owner}: {names}")
    return lines


__all__ = [
    "DECLARED",
    "PACKAGE_ROOT",
    "RULE_DECLARATION",
    "RULE_REACHED_PAST",
    "RULE_UNDECLARED",
    "Declaration",
    "Reach",
    "check_producer_half",
    "packages",
    "reaches",
    "surface_census",
]
