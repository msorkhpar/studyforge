"""Mirror of `src/studyforge/skills/adapter/parts/reading.py` (R12)."""

from __future__ import annotations

import ast
import json

from studyforge.corpus.manifest import parse
from studyforge.skills.adapter import plan_for, scaffold
from studyforge.skills.adapter.parts.reading import READ_PART
from tests.studyforge.skills.adapter import corpora


def read_module():
    """`read.py` as it is delivered, before anybody has written a line of it."""
    made = scaffold(plan_for(parse(json.dumps(corpora.MANIFEST))))
    return next(item.text for item in made.files if item.where.endswith("read.py"))


def test_this_is_the_part_that_is_not_generated():
    # ⛔ R19 is unusable unless a reader can tell which files it covers.
    assert READ_PART.generated is False
    assert READ_PART.where == "{package}/read.py"


def test_it_parses_and_states_a_contract():
    tree = ast.parse(read_module())
    assert ast.get_docstring(tree), "the module a person opens first has no contract (R17)"


def test_the_three_steps_are_all_here():
    named = [
        node.name for node in ast.parse(read_module()).body if isinstance(node, ast.FunctionDef)
    ]
    assert named == ["containers", "documents", "expected_units"]


def test_two_steps_refuse_and_the_third_reports_unwritten():
    # ⛔ An empty list would let the whole pipeline run and emit an archive
    # with no material in it — which validates, because nothing is wrong with it.
    text = read_module()
    assert text.count("raise NotImplementedError(") == 2
    assert "return None" in text


def test_the_refusal_names_what_to_return():
    text = read_module()
    assert "is not written yet" in text
    assert "Return a list of studyforge.corpus.container.Container." in text
    assert "Return a list of build() keyword dicts, one per document." in text


def test_the_refusal_says_why_a_guess_would_be_worse():
    assert "refuses rather than emitting an archive" in read_module()


def test_it_tells_the_reader_that_an_address_is_recorded_not_derived():
    # ⛔ §6, and the one rule a hand-written reader is most likely to break.
    text = read_module()
    assert "recorded, never derived" in text
    assert "do not slugify a title" in text


def test_the_source_side_count_is_told_not_to_read_the_archive():
    assert "never from the archive" in read_module()
