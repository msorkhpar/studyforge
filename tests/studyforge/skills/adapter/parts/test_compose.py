"""Mirror of `src/studyforge/skills/adapter/parts/compose.py` (R12)."""

from __future__ import annotations

import ast

import pytest

from studyforge.skills.adapter.parts.compose import CONTRACT_PARTS, DQ, Part, module
from tests.support import CONTRACT_PARTS as WHAT_R17_WANTS


def rendered(**changes):
    """One composed module, with `changes` applied to a working set of pieces."""
    pieces = {
        "summary": "A summary line.",
        "does": "It does a thing.",
        "uses": "Call it.",
        "depends": "Nothing.",
        "body": ["x = 1"],
    }
    pieces.update(changes)
    return module(**pieces)


def test_the_three_questions_are_the_ones_r17_asks():
    # ⛔ Pinned against `tests.support`, which is where the rest of this
    # repository states R17's shape — not against a literal retyped here.
    assert CONTRACT_PARTS == WHAT_R17_WANTS


def test_a_composed_module_carries_a_contract_and_parses():
    text = rendered()
    tree = ast.parse(text)
    doc = ast.get_docstring(tree)
    assert doc is not None, "a generated module shipped with no docstring"
    for question in CONTRACT_PARTS:
        assert question in doc, f"the generated contract does not say {question!r}"


def test_a_missing_piece_raises_here_rather_than_shipping():
    # ⛔ A contract inside a string literal is a contract no rule reaches, so
    # the check has to be at composition time.
    for piece in ("summary", "does", "uses", "depends"):
        with pytest.raises(ValueError) as refused:
            rendered(**{piece: "   "})
        assert piece in str(refused.value)
        with pytest.raises(ValueError):
            rendered(**{piece: None})


def test_the_delimiter_is_a_value_and_appears_once_at_each_end():
    text = rendered()
    assert text.startswith(DQ)
    assert text.count(DQ) == 2, "the composed contract is not exactly one docstring"


def test_the_body_follows_the_future_import():
    text = rendered(body=["MARKER = 1"])
    assert text.index("from __future__ import annotations") < text.index("MARKER = 1")


def test_a_part_fills_its_package_name_in(monkeypatch):
    part = Part(where="{package}/read.py", step=5, why="why", generated=False, render=rendered)

    class Fake:
        package = "somewhere"

    assert part.path_for(Fake()) == "somewhere/read.py"
