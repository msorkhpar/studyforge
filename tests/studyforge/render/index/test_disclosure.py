"""Mirror of `src/studyforge/render/index/disclosure.py` (R12).

⭐ **Ruling 164's fork, the anchors, and the escaping** — the seams the page as a
whole cannot tell apart from a page that happened to look right.
"""

from __future__ import annotations

import pytest

from studyforge.render.index import (
    LEVEL_KIND,
    LIST_LABEL,
    NUMBERING_KIND,
    READABLE_ATTRIBUTE,
    Document,
    Item,
    PageError,
    Section,
    anchor,
    disclosure,
)
from studyforge.render.markup import safe_href
from tests.studyforge.render.index.indexes import A_HOME_PATH, cases, planted, rows


def a_document(*items: Item, level: str = "module", title: str = "A Module") -> Document:
    """One section holding exactly these units, so a test names only its subject."""
    return Document(
        title="A Corpus",
        levels=("module",),
        sections=(Section(level=level, key="a", title=title, items=items),),
    )


def a_unit(**overrides) -> Item:
    return Item(**{"key": "a/unit-01", "numbering": "1", "title": "One", **overrides})


def test_the_tree_is_labelled_with_this_frameworks_own_structural_word():
    # ⛔ R1: every string on the page that names the MATERIAL comes out of the
    # document; the word for "this is a list of contents" is the framework's.
    assert f'<nav aria-label="{LIST_LABEL}">' in disclosure.render(a_document(a_unit()))


def test_a_refused_href_raises_rather_than_dropping_the_row():
    # ⛔ Ruling 164. This page is nothing but this tree, so a silently dropped
    # anchor is every title present, nothing logged, and not one unit openable
    # from the page a reader lands on first.
    for refused in ("javascript:alert(1)", "x:alert(1)", "/rooted/page.html", "data:text/html,x"):
        assert safe_href(refused) is None, f"{refused} is not refused, so this row proves nothing"
        with pytest.raises(PageError) as raised:
            disclosure.render(a_document(a_unit(href=refused)))
        assert "refused rather than dropped" in str(raised.value)


def test_the_refusal_names_the_position_and_never_the_link():
    # ⛔ R7: this branch fires precisely because the value is not a permitted
    # relative reference, which is where an absolute path arrives — and it runs
    # over every unit in a corpus, into a build log.
    document = Document(
        title="A Corpus",
        levels=("section", "module"),
        sections=(
            Section(
                level="section",
                key="a",
                title="A",
                sections=(
                    Section(
                        level="module",
                        key="a/b",
                        title="B",
                        items=(a_unit(), a_unit(key="a/b/unit-02", href=A_HOME_PATH)),
                    ),
                ),
            ),
        ),
    )
    with pytest.raises(PageError) as raised:
        disclosure.render(document)
    assert "position 1.1.2" in str(raised.value)
    assert A_HOME_PATH not in str(raised.value)
    assert "jane" not in str(raised.value)


def test_a_unit_with_no_page_is_listed_unlinked_and_raises_nothing():
    # ⭐ §7's third state, and the reason the fork above is applicable rather
    # than a coin toss: a renderer that could not tell "no page yet" from "bad
    # href" would always pick the wrong one of drop-or-raise.
    markup = disclosure.render(a_document(a_unit(href=None)))
    assert f'{READABLE_ATTRIBUTE}="false"' in markup
    assert "<a href=" not in markup


def test_a_permitted_relative_href_survives_verbatim():
    markup = disclosure.render(a_document(a_unit(href="a/one.unit.html")))
    assert '<a href="a/one.unit.html">' in markup
    assert f'{READABLE_ATTRIBUTE}="true"' in markup


def test_a_row_is_addressed_by_its_key_and_anchor_is_the_one_composer():
    assert anchor("a/unit-01") == "#a/unit-01"
    markup = disclosure.render(a_document(a_unit()))
    assert f'id="{anchor("a/unit-01")[1:]}"' in markup


def test_the_corpus_own_word_for_a_depth_is_rendered_and_an_absent_one_takes_its_space():
    # ⚠️ A conditional separator left in the caller is a page that differs from
    # its golden by one character on every corpus that names nothing.
    assert f'<span data-kind="{LEVEL_KIND}">module</span> A Module' in disclosure.render(
        a_document(a_unit())
    )
    bare = disclosure.render(a_document(a_unit(), level=""))
    assert "<summary>A Module</summary>" in bare
    assert LEVEL_KIND not in bare


def test_the_numbering_is_wrapped_and_an_absent_one_takes_its_space():
    assert f'<span data-kind="{NUMBERING_KIND}">1</span> One' in disclosure.render(
        a_document(a_unit())
    )
    assert NUMBERING_KIND not in disclosure.render(a_document(a_unit(numbering="")))


def test_what_the_corpus_wrote_is_escaped_on_its_way_to_the_page():
    # ⛔ R13's escaping gate, through the one routine — never a second one.
    markup = disclosure.render(a_document(a_unit(title="a < b & c"), title='Ampersands & "quotes"'))
    assert "a &lt; b &amp; c" in markup
    assert "Ampersands &amp; &quot;quotes&quot;" in markup


def test_an_inline_marker_in_a_title_becomes_markup_rather_than_a_literal():
    assert "<code>x</code>" in disclosure.render(a_document(a_unit(title="a `x` b")))


def test_a_key_with_a_quote_in_it_cannot_break_out_of_the_attribute():
    markup = disclosure.render(a_document(a_unit(key='a/unit"01')))
    assert 'id="a/unit&quot;01"' in markup


def test_the_declared_order_is_used_and_never_re_derived():
    # ⛔ R10, structurally: reversing the document reverses the page, so nothing
    # here sorts. `contents` is the framework's one orderer and this is not it.
    forward = disclosure.render(a_document(a_unit(), a_unit(key="a/unit-02", title="Two")))
    backward = disclosure.render(a_document(a_unit(key="a/unit-02", title="Two"), a_unit()))
    assert forward != backward
    assert forward.index("One") < forward.index("Two")
    assert backward.index("Two") < backward.index("One")


def test_the_disclosure_chain_above_a_row_is_exactly_the_prefixes_of_its_key():
    # ⭐ Subtask (c)'s whole claim, read out of the markup by a parser: a deep
    # link's own fragment says which disclosures stand between it and the page.
    for built in (*cases(), planted((3, 3, 3))):
        found = rows(built.render().decode("utf-8"))
        for key, row in found.items():
            if "/" not in key:
                continue
            parts = key.split("/")
            expected = ["/".join(parts[: depth + 1]) for depth in range(len(parts) - 1)]
            assert [name for name, _ in row.ancestors] == expected


def test_an_empty_deepest_section_renders_as_an_empty_disclosure_rather_than_vanishing():
    document = Document(
        title="A Corpus",
        levels=("module",),
        sections=(
            Section(level="module", key="a", title="Empty"),
            a_document(a_unit()).sections[0],
        ),
    )
    markup = disclosure.render(document)
    assert markup.count("<details") == 2
    assert '<summary><span data-kind="level">module</span> Empty</summary><ol></ol>' in markup
