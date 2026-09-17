r"""`W199/3` tree-wide: a name one package takes from another reaches a DECLARED surface.

**What it does.** Reads every cross-package import under `src/studyforge` and asks
Ruling 101's producer-half question of each one: is the name the importer takes on the
OWNING package's `__all__`? ⛔ Each package's surface is read from THAT PACKAGE, never
from a table here, so the check cannot disagree with the tree about what is exported.

**How you use it.** `check_producer_half(root)` is registered in `tools.quality.CHECKS`;
`reaches(root)` is the reading it is built on, and `packages(root)` is every package
under `src/studyforge` with the surface it declares (`None` when it declares none).

**Depends on.** `ast`, `dataclasses` and `pathlib`; `config` for the walk's exclusions
and repo-relative paths, `report` for the answer. Standard library only.

## ⛔ THE PIN ARM IS THE HALF THAT DOES NOT DEPEND ON A CONSUMER'S SPELLING

⚠️ **Ruling 101 has two remedies and they are IN TENSION** (`W299/1`, measured on the
row that hit it). Its table tells a consumer to import from the PACKAGE once the name is
exported — and a sweep defined over SUBMODULE imports can only hold a name while some
consumer still spells it the deviating way. ⛔ **So fixing a spelling removes the name
from the only instrument holding it on the surface, and nothing goes red.**

⭐ **This module answers that by reading BOTH spellings and asking the same question of
each.** `from studyforge.validate.corpus import Held` and `from studyforge.validate
import Held` both require `Held` on `studyforge.validate.__all__`. ⛔ **A spelling fix
therefore MOVES a name between this module's two arms and never out of its grip**, which
is the property `W299/1` said a tree-wide row had to land BEFORE any spelling is touched.

## ⚠️ WHAT IT DECIDES, AND WHAT IT DECLARES (Ruling 292)

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
3. `tests/` and `tools/`. R1 binds framework source and Ruling 101 governs packages; a
   test reaching into a module is a test of that module.
4. A conditional or function-local import. The walk reads every `ImportFrom` in the tree,
   so one inside a function IS read — what is not read is whether it ever runs.
5. An EMPTY population is reported through the notice rather than failed. The floor runs
   over a corpus, a consumer repository and an installed tree, and none of those owes a
   `src/studyforge` (Ruling 191's split, `reach.py`'s precedent). ⛔ The real tree's
   population is pinned in the mirror instead, so a walk that reads nothing cannot pass
   here as a clean bill.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_UNDECLARED = "surface-undeclared"

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
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    return frozenset(ast.literal_eval(node.value))
                except (TypeError, ValueError):
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
        except (OSError, SyntaxError):
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
                found.append(
                    Reach(relative, node.lineno, owner, module, alias.name, on_surface)
                )
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
            f"two packages do not share it. ⛔ Adding it to a declaration to quiet this "
            f"is declaring a defect, not fixing one (W199)."
        ),
    )


def check_producer_half(root: Path) -> list[Finding]:
    """Return a finding for every name a package shares from its own surface without declaring it.

    ⛔ This is the PIN arm: it binds the PACKAGE spelling, so it holds a name on its
    owner's surface however the consumer spells the import, and a later row fixing a
    spelling cannot silently release what this was holding (`W299/1`).
    """
    return [
        _undeclared(reach)
        for reach in reaches(root)
        if not reach.module and not reach.on_surface
    ]


__all__ = [
    "PACKAGE_ROOT",
    "RULE_UNDECLARED",
    "Reach",
    "check_producer_half",
    "packages",
    "reaches",
]
