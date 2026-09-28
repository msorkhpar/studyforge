"""Mirror of `src/studyforge/skills/execution/emit.py` (R12).

⛔ **Quoting is the whole subject.** YAML 1.1 reads `no` as false and a bare
colon as a mapping, so a value this emitter wrote unquoted would produce a file
that parses and does the wrong thing — silently. ⭐ Every rule is asserted with
its counter-example beside it.
"""

from __future__ import annotations

import json

import pytest

from studyforge.skills.execution import emit


@pytest.mark.parametrize("word", emit.RESERVED)
def test_a_word_yaml_would_read_as_something_else_is_quoted(word):
    assert emit.scalar(word) == f'"{word}"'


def test_an_ordinary_word_is_not_quoted():
    # ⭐ The other direction: an emitter that quoted everything would be
    # correct and unreadable, and nothing would be testing the rule.
    assert emit.scalar("editor-config") == "editor-config"


def test_booleans_numbers_and_null_are_never_quoted():
    assert emit.emit({"a": True, "b": 3, "c": None}) == "a: true\nb: 3\nc: null\n"


def test_a_boolean_is_not_emitted_as_a_number():
    # ⚠️ `True == 1` in Python, and `1` in a compose file is not `true`.
    assert emit.scalar(True) == "true" and emit.scalar(1) == "1"


@pytest.mark.parametrize("value", ["a:b", "a#b", "with'quote", "line\nbreak", " padded", ""])
def test_an_ambiguous_scalar_is_quoted(value):
    assert emit.scalar(value).startswith('"')


def test_a_quote_and_a_backslash_are_escaped_inside_a_quoted_scalar():
    assert emit.scalar('say "x"') == '"say \\"x\\""'
    # ⚠️ Only inside one: a backslash is an ordinary character in a bare YAML
    # scalar, and quoting it to escape it would be inventing an ambiguity.
    assert emit.scalar("back\\slash") == "back\\slash"
    assert emit.scalar("a:back\\slash") == '"a:back\\\\slash"'


def test_an_empty_collection_is_written_inline_so_the_document_stays_valid():
    assert emit.emit({"volumes": {"one": {}}, "ports": []}) == "volumes:\n  one: {}\nports: []\n"


def test_nesting_is_two_spaces_deep_per_level():
    assert emit.emit({"a": {"b": ["c"]}}) == "a:\n  b:\n    - c\n"


def test_a_list_of_mappings_nests_under_its_dash():
    assert emit.emit([{"a": 1}]) == "-\n  a: 1\n"


def test_a_bare_scalar_document_is_one_line():
    assert emit.emit("word") == "word\n"


def test_a_line_break_and_a_tab_are_escaped_so_a_multi_line_value_reads_back_whole():
    # ⛔ Raw, a YAML reader folds the break into a space: a build argument listing
    # one file per line would arrive as one line.
    assert emit.scalar("one\ntwo") == '"one\\ntwo"'
    assert emit.scalar("a\tb") == '"a\\tb"'
    assert "\n" not in emit.scalar("one\ntwo\nthree")
    assert json.loads(emit.scalar('x\n"y"\\z')) == 'x\n"y"\\z'
