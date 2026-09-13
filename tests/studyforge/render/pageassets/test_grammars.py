"""Mirror of `src/studyforge/render/pageassets/grammars.py` (R12).

⭐ The runtime-free half. It reads the declaration and asserts what the
renderer does with it. Whether the declaration matches the grammars the bundle
really carries is `test_highlight_grammars.py`'s, which runs the bundle.
"""

from __future__ import annotations

import pytest

from studyforge.render.pageassets import AssetError, header_of
from studyforge.render.pageassets.grammars import (
    DECLARATION_MARKER,
    HIGHLIGHTER,
    PLAIN,
    declared_languages,
    falls_back,
    grammar_for,
    highlighted_languages,
)


def unvendored_language():
    """A language name minted so that no declaration can contain it."""
    return "x-" + "-".join(sorted(highlighted_languages()))


def test_the_real_header_declares_a_non_empty_set_that_includes_the_fallback():
    declared = highlighted_languages()
    assert declared, "the vendored highlighter declares no language at all"
    assert PLAIN in declared
    assert declared == declared_languages(header_of(HIGHLIGHTER))


def test_the_declaration_sits_inside_the_part_of_the_file_read_as_its_header():
    assert DECLARATION_MARKER in header_of(HIGHLIGHTER)


@pytest.mark.parametrize(
    "header,message",
    [
        ("/* Prism, no declaration at all */", "exactly one"),
        (f"/* {DECLARATION_MARKER}\n*/", "names no language"),
        (f"/* {DECLARATION_MARKER} .\n*/", "names no language"),
        (f"/* {DECLARATION_MARKER} java kotlin.\n*/", "does not declare 'plain'"),
        (f"/* {DECLARATION_MARKER} plain\n   {DECLARATION_MARKER} java */", "exactly one"),
    ],
)
def test_a_header_that_cannot_answer_is_refused(header, message):
    with pytest.raises(AssetError, match=message):
        declared_languages(header)


def test_a_declaration_is_read_as_names_and_its_closing_full_stop_is_not_one():
    assert declared_languages(f"/*\n   {DECLARATION_MARKER} java plain sql.\n*/") == {
        "java",
        "plain",
        "sql",
    }


@pytest.mark.parametrize("language", sorted(highlighted_languages()))
def test_every_declared_language_asks_for_its_own_grammar(language):
    assert grammar_for(language) == language
    assert grammar_for(language.upper()) == language
    assert not falls_back(language)


def test_an_undeclared_language_asks_for_the_plain_fallback():
    language = unvendored_language()
    assert falls_back(language)
    assert grammar_for(language) == PLAIN
    assert grammar_for(f"  {language.upper()} ") == PLAIN
