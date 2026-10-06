r"""The part of the library a learner's copy of a course serves with, found by its imports.

**What it does.** Starts at the modules the study server runs (`ROOTS`: the
command, and its `serve` and `preflight` verbs) and follows every `import`
statement it reads, at module level and inside functions alike, with each
module's enclosing packages, to the set of modules serving can load.
`DEFERRED` names the few edges it does not follow, each with the reason the
served app never takes it. `vendored(src)` is every file the served runtime
needs: those modules and the data files their packages ship.

**How you use it.**

    modules = served(src)           # dotted names, sorted
    files = vendored(src)           # paths relative to `src`, sorted
    forbidden(modules)              # empty, or what a learner's runtime must not carry
    stale(src)                      # declared deferred edges the tree no longer has

`src` is the directory holding the `studyforge` package.

**Depends on.** `ast` and `pathlib`. ⛔ It imports nothing it reads: the
closure is computed over source text, so a module that would fail to import is
still one whose imports are counted.

## ⛔ Every import statement, not only the module-level ones

⚠️ A function-local import runs the moment the function does, so a closure
over module-level imports alone is a runtime that breaks on the first request
that reaches one. ⭐ So every `import` and `from … import` anywhere in a module is
an edge, and the few this refuses to follow are DECLARED in `DEFERRED` with
their reason, never inferred. ⛔ A declared edge the tree no longer has is a
finding (`stale`), so the list cannot outlive what it excuses.

## ⛔ What a learner's runtime never carries

`FORBIDDEN`: the skills (how a course is built), narration synthesis and its
client and wire, packing a narration release, and the `narrate`, `build` and
`exercises` verbs. ⭐ The served app is proved to import and serve from the vendored tree
alone in `tests/studyforge/skills/execution/standalone/test_closure.py`.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from pathlib import Path

#: The package every module here belongs to.
PACKAGE = "studyforge"

#: ⭐ What the course's site container runs: `python3 -m studyforge.cli serve`,
#: and `preflight` before it.
ROOTS = ("studyforge.cli.__main__", "studyforge.cli.serve", "studyforge.cli.preflight")

#: Why the dispatcher's loaders for the other verbs are not followed.
VERB = (
    "the dispatcher imports a verb's module only when that verb is dispatched, and a "
    "learner's server dispatches serve and preflight alone"
)

#: Why the validator's two skill imports are not followed.
VALIDATE = (
    "a check of `studyforge validate` that only an archive validation runs, and serving "
    "never validates an archive"
)

#: ⛔ The edges this closure does not follow, and why the served app never takes each.
DEFERRED: Mapping[tuple[str, str], str] = {
    ("studyforge.cli.dispatch", "studyforge.cli.narrate.cli"): VERB,
    ("studyforge.cli.dispatch", "studyforge.cli.site.cli"): VERB,
    ("studyforge.cli.dispatch", "studyforge.cli.exercises"): VERB,
    ("studyforge.validate.ledger", "studyforge.skills.exercises"): VALIDATE,
    ("studyforge.validate.ledger", "studyforge.skills.exercises.scan"): VALIDATE,
    ("studyforge.validate.source.curriculum", "studyforge.skills.adapter"): VALIDATE,
}

#: ⛔ The packages a learner's runtime never carries, and why.
FORBIDDEN: Mapping[str, str] = {
    "studyforge.skills": "the skills are how a course is built, and a learner builds nothing",
    "studyforge.narrate.synth": "narration synthesis: the clips arrive already made",
    "studyforge.narrate.client": "the narration service's client: nothing is synthesised",
    "studyforge.narrate.wire": "the narration service's wire: nothing is synthesised",
    "studyforge.narrate.release": "packing a narration release is the builder's",
    "studyforge.cli.narrate": "the narrate verb synthesises",
    "studyforge.cli.site": "the build verb writes a site, and the learner's is built",
    "studyforge.cli.exercises": "the exercises verb reads how a course was authored",
}

#: Directories a package may hold that carry nothing the runtime reads.
SKIPPED = ("__pycache__",)

#: File suffixes that are never vendored: the interpreter writes its own.
SKIPPED_SUFFIXES = (".pyc", ".pyo")

#: ⭐ The commit stamp a wheel carries. Never copied from the library that runs
#: the export: the export writes the one it read (`runtime.write`).
STAMP = "COMMIT"


def path_of(src: Path, module: str) -> Path | None:
    """Return the file `module` is read from under `src`, or `None` when it is not there."""
    base = Path(src).joinpath(*module.split("."))
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    return None


def imported(src: Path, module: str) -> frozenset[str]:
    """Every `studyforge` module one module's import statements name, wherever they sit."""
    path = path_of(src, module)
    if path is None:
        return frozenset()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(package, node.level, node.module)
            found.add(base)
            found.update(f"{base}.{alias.name}" for alias in node.names)
    return frozenset(
        name for name in found if name.split(".")[0] == PACKAGE and path_of(src, name) is not None
    )


def served(src: Path, roots: Iterable[str] = ROOTS) -> tuple[str, ...]:
    """Every module serving can load: the roots, what they import, and their packages."""
    seen: set[str] = set()
    todo = list(roots)
    while todo:
        module = todo.pop()
        if module in seen or path_of(src, module) is None:
            continue
        seen.add(module)
        parts = module.split(".")
        todo.extend(".".join(parts[:end]) for end in range(1, len(parts)))
        todo.extend(name for name in imported(src, module) if (module, name) not in DEFERRED)
    return tuple(sorted(seen))


def forbidden(modules: Iterable[str]) -> tuple[str, ...]:
    """Return the modules among `modules` that a learner's runtime never carries."""
    return tuple(
        sorted(
            module
            for module in modules
            if any(module == name or module.startswith(name + ".") for name in FORBIDDEN)
        )
    )


def stale(src: Path) -> tuple[tuple[str, str], ...]:
    """Every declared deferred edge whose import the tree no longer makes."""
    return tuple(sorted(edge for edge in DEFERRED if edge[1] not in imported(src, edge[0])))


def vendored(src: Path, roots: Iterable[str] = ROOTS) -> tuple[str, ...]:
    """Every file the served runtime needs, relative to `src`: its modules and their data.

    ⭐ A package's data is every file beneath it that is not Python and sits in
    no sub-package of its own, so `render/templates/` travels with `render` and
    `narrate/release/scripts/` does not travel with `narrate`.
    """
    src = Path(src)
    modules = served(src, roots)
    files: set[str] = set()
    for module in modules:
        path = path_of(src, module)
        if path is None:  # pragma: no cover - `served` keeps only modules it found
            continue
        files.add(path.relative_to(src).as_posix())
        if path.name == "__init__.py":
            files.update(_data(src, path.parent))
    return tuple(sorted(files))


def _data(src: Path, package: Path) -> set[str]:
    """Return the non-Python files a package ships, not descending into a sub-package."""
    found: set[str] = set()
    for entry in sorted(package.iterdir()):
        if entry.name in SKIPPED or entry.suffix in SKIPPED_SUFFIXES:
            continue
        if entry.is_dir():
            if not (entry / "__init__.py").is_file():
                found.update(_data(src, entry))
        elif entry.suffix != ".py" and entry.name != STAMP:
            found.add(entry.relative_to(src).as_posix())
    return found


def _absolute(package: str, level: int, module: str | None) -> str:
    """Return the absolute name a `from` import names, relative levels resolved in `package`."""
    if not level:
        return module or ""
    parts = package.split(".")
    base = parts[: len(parts) - (level - 1)]
    return ".".join(base + ([module] if module else []))
