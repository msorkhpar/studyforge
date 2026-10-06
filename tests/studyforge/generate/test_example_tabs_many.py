"""An example block may have a tab for any number of languages, one to eight.

⭐ The row's claims, end to end through `write_site`: a block has a tab and a panel for each
language it is written in, in the default mode's order, whatever the number (one, two, three and
four languages are built), and a block of every declared language says nothing about a missing one.
Validation refuses a ninth tab and an undeclared language (`test_example_blocks`).
"""

from __future__ import annotations

import re

import pytest

from tests.studyforge.generate import four_corpus as corpus


def text(out, where):
    return (out / where).read_text(encoding="utf-8")


def block(page: str, ident: str) -> str:
    """One example block's markup: from its opening tag to the next block, or the page's end."""
    start = page.index(f'<div data-example="{ident}"')
    following = page.find('<div data-example="', start + 1)
    return page[start : following if following != -1 else len(page)]


def tabs(markup: str) -> list[tuple[str, bool]]:
    """`(language, disabled)` of each tab in a block's markup, in order."""
    return [
        (m.group(1), 'aria-disabled="true"' in m.group(0))
        for m in re.finditer(r'<button[^>]*role="tab"[^>]*data-lang="([^"]+)"[^>]*>', markup)
    ]


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_a_block_has_a_tab_for_each_language_it_is_written_in_in_the_default_modes_order(
    tmp_path, count
):
    chosen = corpus.LANGS[:count]
    units = (
        (
            1,
            "Shared ideas",
            [("lesson", None, [corpus.example("each", chosen)], None)],
        ),
    )
    out = corpus.build(tmp_path, "c", corpus.declared(count, mixed=count > 1), units=units)
    markup = text(out, corpus.PAGES[1])
    assert tabs(markup) == [(x, False) for x in chosen]
    assert len(re.findall(r'role="tabpanel"', markup)) == count
    assert markup.count("aria-controls=") == count


def test_the_four_tab_block_lists_every_language_and_no_sentence(tmp_path):
    out = corpus.build(tmp_path, "c", corpus.declared(mixed=True), units=corpus.UNITS[:1])
    quad = block(text(out, corpus.PAGES[1]), "quad")
    assert tabs(quad) == [(x, False) for x in corpus.LANGS]
    assert "data-missing" not in quad and "Available in" not in quad
