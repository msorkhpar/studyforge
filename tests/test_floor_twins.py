"""The product floor under `tests/floor/` is still the tooling's floor, check for check.

⛔ **A PROCESS test, declared in `tests/harness/process.py`**: it exists only while both copies
do, and it leaves with the tooling, after which the product's copy is the only one.

**Why it exists.** The product's rules — R7, R11, R12, R17, R1, the producer half and the style
layer — were COPIED out of `tools/quality/` rather than moved, because the tooling is the merge
authority until it leaves and must go red exactly as before. ⚠️ **Two copies nobody compares
become two rules**, so two things are asserted here:

1. ⭐ **Each copied module's CODE is its original's.** Both files are parsed, every docstring is
   stripped, and the import statements are compared as a set after one declared rewrite —
   `tools.quality` is `tests.floor`, and `tools.reserved_addresses` is
   `tests.floor.reserved_addresses`. Prose may differ (the copies say what they are); code may
   not, down to a constant, a pattern or a message.
2. ⭐ **Every check and notice the tooling registers is SORTED**: it is in the product floor's
   registry, or it is named below as process with the reason, or as deferred with the task
   that homes it. A check added to the tooling without a side turns this red.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import tests.floor
import tools.quality
from tests.support import repository_root

#: `(product copy, tooling original)`, repository-relative. ⛔ Whole modules, never a subset.
TWINS = [
    ("tests/floor/config.py", "tools/quality/config.py"),
    ("tests/floor/report.py", "tools/quality/report.py"),
    ("tests/floor/size.py", "tools/quality/size.py"),
    ("tests/floor/mirror.py", "tools/quality/mirror.py"),
    ("tests/floor/docstrings.py", "tools/quality/docstrings.py"),
    ("tests/floor/style.py", "tools/quality/style.py"),
    ("tests/floor/source_names.py", "tools/quality/source_names.py"),
    ("tests/floor/surfaces.py", "tools/quality/surfaces.py"),
    ("tests/floor/deviations.py", "tools/quality/deviations.py"),
    ("tests/floor/personal_data/__init__.py", "tools/quality/personal_data/__init__.py"),
    ("tests/floor/personal_data/shapes.py", "tools/quality/personal_data/shapes.py"),
    ("tests/floor/personal_data/registry.py", "tools/quality/personal_data/registry.py"),
    ("tests/floor/personal_data/identity.py", "tools/quality/personal_data/identity.py"),
    ("tests/floor/reserved_addresses.py", "tools/reserved_addresses.py"),
]

#: The one rewrite a copy's imports may differ by: `(tooling module, product module)`.
REWRITES = (("tools.quality", "tests.floor"), ("tools", "tests.floor"))

#: ⛔ Tooling checks and notices that police the PROCESS, each with the reason. They stay with
#: the tooling and leave with it.
PROCESS = {
    "check_board": "the board is a register of rows, offices and rounds",
    "check_handoffs": "the handoff contract; handoffs leave for the archive branch",
    "check_handoff_existence": "reads which rows the board's register declares closed",
    "check_marker_patterns": "reads docs/conventions/ for a finding marker's pattern",
    "check_pointers": "the links between the process documents, most of which leave",
    "check_anchor_collisions": "the same document population as check_pointers",
    "check_rulings_index": "the rulings index is derived from ruling records",
    "check_rulings_reach": "whether the newest ruling reached a convention",
    "check_clause_counts": "reads docs/conventions/ headings for a stated clause count",
    "check_derived_counts": "a figure in prose must name the ref it was measured at",
    "check_owns_before_creator": "reads the plan's graph: rows, Owns and Depends on",
    "approach_notice": "R11's approach, read off branches and offices in git history",
    "pointer_coverage": "check_pointers' denominator",
    "collision_census": "check_anchor_collisions' denominator",
    "location_notice": "path:line citations in the process documents",
    "board_state": "the board's population",
    "handoff_existence": "check_handoff_existence's denominator",
    "handoff_citations": "check_handoffs' citation arm",
    "rulings_notice": "check_rulings_index's denominator",
    "reach_notice": "check_rulings_reach's backlog",
    "clause_census": "check_clause_counts' denominator",
    "count_census": "check_derived_counts' denominator",
    "creator_census": "check_owns_before_creator's denominator",
    "vacuity_notice": "the tooling's registry of its own checks; the product floor has its own",
    "lint_notice": "what the linter said; the product enforces lint in tests/test_repository.py",
}

#: ⚠️ Product checks whose home waits on another task, each with that task and why.
DEFERRED = {
    "check_rejected_palettes": (
        "REL-08: it reads docs/conventions/ui-design.md's table, and that convention's product "
        "home is REL-08's to decide; the check follows its table"
    ),
    "palette_census": "REL-08: check_rejected_palettes' denominator, and follows it",
}


def _rewritten(module: str) -> str:
    for tooling, product in REWRITES:
        if module == tooling or module.startswith(tooling + "."):
            return product + module[len(tooling) :]
    return module


def _strip_docstrings(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    node.body = body[1:] or [ast.Pass()]


def normalised(relative: str, rewrite: bool, text: str | None = None) -> tuple[str, frozenset]:
    """Return a module's code with docstrings and imports stripped, and its imports as a set."""
    if text is None:
        text = (repository_root() / relative).read_text(encoding="utf-8")
    tree = ast.parse(text)
    _strip_docstrings(tree)
    imports: set[tuple[str, str, str]] = set()
    kept = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = _rewritten(node.module or "") if rewrite else node.module or ""
            imports.update((module, alias.name, alias.asname or "") for alias in node.names)
        elif isinstance(node, ast.Import):
            imports.update(("", alias.name, alias.asname or "") for alias in node.names)
        else:
            kept.append(node)
    tree.body = kept
    return ast.dump(tree), frozenset(imports)


@pytest.mark.parametrize(("copy", "original"), TWINS, ids=[copy for copy, _ in TWINS])
def test_each_copy_is_its_originals_code(copy, original):
    ours = normalised(copy, rewrite=False)
    theirs = normalised(original, rewrite=True)
    assert ours[1] == theirs[1], f"{copy} imports differ from {original}'s"
    assert ours[0] == theirs[0], f"{copy}'s code differs from {original}'s"


def test_the_comparison_can_go_red():
    # ⛔ A comparison that cannot fail proves nothing. Plant a one-character drift in the
    #    copy's CODE and it must differ; plant the same drift in PROSE and it must not.
    copy = "tests/floor/config.py"
    text = (repository_root() / copy).read_text(encoding="utf-8")
    original = normalised("tools/quality/config.py", rewrite=True)
    assert "SOURCE_LINE_CEILING = 400\n" in text
    drifted = text.replace("SOURCE_LINE_CEILING = 400\n", "SOURCE_LINE_CEILING = 401\n")
    assert normalised(copy, False, drifted)[0] != original[0]
    reworded = text.replace("Every number and path", "Every figure and path", 1)
    assert reworded != text
    assert normalised(copy, False, reworded) == original


def _names(functions) -> set[str]:
    return {function.__name__ for function in functions}


def test_every_tooling_check_and_notice_is_sorted_onto_one_side():
    tooling = _names(tools.quality.CHECKS) | _names(tools.quality.NOTICES)
    product = _names(tests.floor.CHECKS) | _names(tests.floor.NOTICES)
    unsorted = tooling - product - set(PROCESS) - set(DEFERRED)
    assert unsorted == set(), f"a tooling check has no side: {sorted(unsorted)}"
    both = (product & set(PROCESS)) | (product & set(DEFERRED)) | (set(PROCESS) & set(DEFERRED))
    # ⚠️ `vacuity_notice` is named on both sides by design: the product floor has its OWN.
    assert both == {"vacuity_notice"}, sorted(both)
    stale = (set(PROCESS) | set(DEFERRED)) - tooling
    assert stale == set(), f"sorted but no longer registered: {sorted(stale)}"


def test_every_product_check_is_the_twin_of_a_tooling_check():
    # ⛔ The product floor carries no rule the tooling did not already enforce — it is a copy,
    #    never a second, stronger or weaker rule.
    tooling = {(f.__module__, f.__name__) for f in tools.quality.CHECKS}
    for check in tests.floor.CHECKS:
        original = check.__module__.replace("tests.floor", "tools.quality", 1)
        assert (original, check.__name__) in tooling, f"{check.__module__}.{check.__name__}"


def test_the_twins_cover_every_module_the_product_floor_copies():
    floor = Path(tests.floor.__file__).parent
    own = {"__init__.py", "__main__.py", "vacuity.py"}
    copies = {
        path.relative_to(repository_root()).as_posix()
        for path in floor.rglob("*.py")
        if not path.name.startswith("test_") and path.name not in own
    } | {"tests/floor/personal_data/__init__.py"}
    assert copies == {copy for copy, _ in TWINS}
