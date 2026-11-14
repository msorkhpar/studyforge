r"""The project helper's two commands: a manifest to fill in, and what a manifest would ship.

**What it does.** `skeleton(before, after)` reads a before/after pair of snapshots and answers with
a manifest whose every fact the pair already says is filled in: the two folders, the entry point
if one is obvious, the expected report if there is one, one case per test this step adds or
changes (worded by its docstring, `main` until the author says otherwise), and one blueprint entry
per function the step adds or changes, with the contract read off its docstring. ⛔ What only an
author knows, the modeling idea and the lesson, is left empty, and `project.read_manifest` refuses
an empty field, so a skeleton never ships unread. `summary(manifest)` builds the draft and says,
file by file and case by case, what it would ship, and which changed files the step's page shows
a change to (the copied candidate `H1` runs).

**How you use it.**

    python -m studyforge.skills.exercises.project new steps/02 steps/03 > project.json
    python -m studyforge.skills.exercises.project check project.json

**Depends on.** `ast`, `json`, and this package's `project`, `snapshot` and `drafts`. Standard
library only. ⛔ Nothing here runs a test: the gates do, in the pinned runner.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

from studyforge.exercise import EDGE, KEPT, MAIN, Origin
from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.project import (
    MANIFEST_FILENAME,
    PROJECT_API,
    project_draft,
    read_manifest,
)
from studyforge.skills.exercises.snapshot import read_snapshot, declared_tests

#: What `check` names the workspace it builds the draft for: a placeholder, never a real place.
CHECK_WORKSPACE = "practice/check"

#: ⭐ The origin `check` builds a draft with when the manifest names none: it checks nothing a
#: gate reads, and a real pass hands `project_draft` the page's own. ⛔ With no page there is no
#: page text either, and `check` says so rather than counting what an empty page shows.
_NO_ORIGIN = Origin("unset", None)

#: The entry point's usual names, tried in this order.
ENTRIES = ("main.py", "run.py", "__main__.py")


def skeleton(before: Path, after: Path, *, tests: str = "tests", relative_to: Path) -> dict:
    """Return a manifest for the pair, every path relative to `relative_to`."""
    old = read_snapshot(before, tests=tests)
    new = read_snapshot(after, tests=tests)
    earlier = declared_tests(old).declared
    now = declared_tests(new)
    cases = [
        [one, MAIN, test.summary]
        for one, test in now.declared.items()
        if one not in earlier or earlier[one].source != test.source
    ]
    cases += [[f"{one}[...]", MAIN, "declare each parametrised id"] for one in now.parametrised]
    entry = next((one for one in ENTRIES if one in new.sources), "")
    expected = next((one for one in new.read_only if one.startswith("expected/")), "")
    return {
        "project_api": PROJECT_API,
        "title": "",
        "before": _relative(before, relative_to),
        "after": _relative(after, relative_to),
        "tests": tests,
        "entry": entry,
        "statement": "statement.md",
        "expected": {"output": expected, "abs_tol": 1e-6, "rel_tol": 1e-9},
        "blueprint": [
            _entry(path, node, text)
            for path, text in new.sources.items()
            for node in _changed(text, old.sources.get(path, ""), path)
        ],
        "cases": cases,
        "plants": {},
    }


def summary(manifest: Path) -> list[str]:
    """Return the lines `check` prints: the files by role, the cases by kind, and the plants."""
    found = read_manifest(manifest)
    page = None if found.origin else ""
    draft = project_draft(found, CHECK_WORKSPACE, origin=found.origin or _NO_ORIGIN, page=page)
    edited = (draft.main_file, *draft.files)
    changed = [
        path
        for path in edited
        if path == draft.main_file or draft.files[path].starter != draft.files[path].reference
    ]
    lines = [found.title, f"  the reader edits {len(edited)} file(s), {len(changed)} changed:"]
    lines += [f"    {path}" for path in changed]
    if found.origin:
        lines += _shown(draft, changed)
    else:
        lines.append("  no page is cited, so what copying it gives away (H1) is not read")
    lines.append(f"  read-only: {len(draft.read_only) + 1} file(s), the tests and their fixtures")
    for kind in (MAIN, EDGE, KEPT):
        named = [case for case in draft.cases if case.kind == kind]
        lines.append(f"  {kind}: {len(named)} case(s)")
        lines += [f"    {case.id}: {case.says}" for case in named if kind != KEPT]
    edges = sum(1 for case in draft.cases if case.kind == EDGE)
    lines.append(f"  plants: {len(draft.plants)} for {edges} edge case(s)")
    return lines


def _shown(draft, changed: list[str]) -> list[str]:
    """The lines naming each changed file the page shows a change to, which `H1` will run."""
    starters = {draft.main_file: draft.starter} | {p: f.starter for p, f in draft.files.items()}
    shown = [path for path in changed if draft.copied[path] != starters[path]]
    lines = [f"  the page shows a change to {len(shown)} of {len(changed)} changed file(s):"]
    return lines + [f"    {path}" for path in shown]


def main(argv: list[str]) -> int:
    """`new <before> <after> [tests]` prints a manifest; `check <manifest>` prints a summary."""
    try:
        if len(argv) in (3, 4) and argv[0] == "new":
            tests = (argv[3:] or ["tests"])[0]
            made = skeleton(Path(argv[1]), Path(argv[2]), tests=tests, relative_to=Path.cwd())
            print(json.dumps(made, indent=2, ensure_ascii=False))
            return 0
        if len(argv) == 2 and argv[0] == "check":
            print("\n".join(summary(Path(argv[1]))))
            return 0
    except AuthoringError as error:
        print(f"refused: {error}")
        return 1
    print(
        "usage: python -m studyforge.skills.exercises.project new <before> <after> [tests]\n"
        f"       python -m studyforge.skills.exercises.project check <{MANIFEST_FILENAME}>"
    )
    return 2


def _changed(text: str, before: str, path: str) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """The module-level functions of `text` that `before` lacks or defines differently."""
    old = {node.name: ast.unparse(node) for node in _functions(before, path)}
    return [node for node in _functions(text, path) if old.get(node.name) != ast.unparse(node)]


def _functions(text: str, path: str) -> list:
    """Every module-level function of a source file."""
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as error:
        raise AuthoringError(f"'{path}' does not parse, at line {error.lineno}") from None
    return [node for node in tree.body if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)]


def _entry(path: str, node, text: str) -> dict:
    """One blueprint entry for a changed function: its signature and contract filled in."""
    lines = text.splitlines()
    signature = "\n".join(lines[node.lineno - 1 : node.body[0].lineno - 1]).strip()
    if ast.get_docstring(node) is not None:
        signature = signature.split('"""')[0].split("'''")[0].strip()
    return {
        "file": path,
        "signature": signature.removesuffix(":"),
        "contract": (ast.get_docstring(node) or "").strip(),
        "idea": "",
        "lesson": {"title": "", "href": ""},
    }


def _relative(path: Path, base: Path) -> str:
    """`path` as `base` reaches it, with forward slashes."""
    return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()
