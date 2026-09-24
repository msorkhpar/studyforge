"""Mirror of `src/studyforge/skills/delivery/components.py` (R12).

⛔ What the pin document SAYS, and the reading it is turned into: which side
delivers a row (`W92`). ⚠️ What the index does with that reading — the column,
the legend, the derivation — is asserted next door, in `test_capability.py`.
"""

from __future__ import annotations

from studyforge.skills.delivery import ELSEWHERE, HERE, SIDES, UNDECLARED, Components
from tests.studyforge.skills.delivery import plans


def test_the_three_readings_are_the_whole_vocabulary_and_nothing_else_exists():
    # ⛔ A narrowed population, never a widened predicate. A fourth
    # value is a change to this tuple and to this test, never a passed string.
    assert SIDES == (HERE, ELSEWHERE, UNDECLARED)


def test_a_pin_document_that_is_not_readable_declares_no_component():
    # ⚠️ Whether the workspace's pin file is well formed is the workspace
    # check's question. This module answers *what is pinned* and says nothing.
    assert Components.read("not json at all", plans.SEQUENCE).names == frozenset()


def test_a_component_the_pin_document_marks_self_is_not_somewhere_else():
    # ⛔ The control for the reading above: `read` keeps only what `where` says
    # is not `self`, so this repository's own name never places a row away.
    declared = Components.read(plans.NO_PINS, plans.SEQUENCE)
    assert declared.names == frozenset()
    assert Components.read(plans.PINS, plans.SEQUENCE).names == frozenset({"elsewhere-component"})


def test_a_cell_naming_a_path_inside_a_pinned_component_reads_as_elsewhere():
    assert plans.components().side("`elsewhere-component/docker/` — the image", "") == ELSEWHERE


def test_a_cell_naming_a_path_that_reaches_no_component_reads_as_here():
    assert plans.components().side("`address/`", "") == HERE


def test_a_cell_naming_no_path_at_all_reads_as_undeclared_and_is_never_guessed():
    assert plans.components().side("the release record", "") == UNDECLARED


def test_a_preamble_places_a_row_only_when_it_names_exactly_one_component():
    # ⭐ The weak derivation, and it is deliberately weak: two named components
    # say nothing about which one delivers the row, so nothing is said.
    declared = plans.components()
    one = "It becomes **`elsewhere-component`**, its own repository."
    assert declared.side("the release record", one) == ELSEWHERE
    assert declared.side("the release record", "It becomes `elsewhere-component`.") == UNDECLARED


def test_a_workspace_that_pins_nothing_but_itself_reads_a_path_as_here():
    assert Components.none().side("`elsewhere-component/docker/`", "") == HERE


def test_the_reading_takes_the_two_cells_and_never_a_capability():
    # ⛔ The seam asserted rather than described: this module imports
    # nothing from the package, so it cannot close a cycle with the module that
    # indexes what it reads. ⚠️ Read off the parsed IMPORTS, never off the
    # text: the docstring's own example names the package and is prose.
    import ast
    import inspect

    from studyforge.skills.delivery import components

    tree = ast.parse(inspect.getsource(components))
    reached = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    reached |= {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(name.startswith("studyforge") for name in reached), reached
    assert inspect.signature(components.Components.side).parameters.keys() == {
        "self",
        "owns",
        "preamble",
    }
