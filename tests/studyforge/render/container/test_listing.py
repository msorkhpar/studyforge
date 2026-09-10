"""Mirror of `src/studyforge/render/container/listing.py` (R12).

⭐ The list is the page, so this module carries the assertions that matter most:
declared order is kept, an unlinkable unit is listed rather than dropped, and a
**refused** href raises instead of vanishing — the one place this package
deliberately differs from the between-units bar.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render.container import Item, PageError
from studyforge.render.container import listing as listing_module
from studyforge.render.markup import safe_href

#: ⛔ Synthetic, and assembled rather than written whole (R7).
POISON = "/" + "home/example/material/private-corpus"

#: Hrefs `safe_href` refuses, one per named reason in its own docstring.
REFUSED = {
    "rooted": "/units/unit-01.unit.html",
    "protocol-relative": "//example.invalid/x.html",
    "javascript": "javascript:alert(1)",
    "data": "data:text/html,<b>x</b>",
    "tab-smuggled-scheme": "java\tscript:alert(1)",
    "backslash-rooted": "/\\example.invalid/x.html",
    "home-path": POISON,
}


def an_item(**overrides) -> Item:
    """A valid, linked item, with one field replaced."""
    fields = {"numbering": "1.1", "title": "Your first class", "href": "unit-01-a.unit.html"}
    return Item(**{**fields, **overrides})


def test_the_declared_order_is_the_rendered_order():
    # ⛔ Never re-derived: the container reader has already refused a map whose
    # ordinals are not contiguous, so the declared order IS the ordinal order.
    # ⚠️ The titles here sort the other way on purpose, so a `sorted` slipped
    # into the renderer fails this rather than passing it.
    declared = ((1, "Zeta"), (2, "Alpha"))
    items = tuple(an_item(numbering=str(n), title=title) for n, title in declared)
    rendered = listing_module.render(items)
    assert rendered.index("Zeta") < rendered.index("Alpha")


def test_a_unit_with_no_page_is_listed_and_not_linked():
    # ⭐ §7's three states: an ungenerated unit is part of the material's shape
    # and a reader must see it. It is listed, marked, and carries no anchor.
    rendered = listing_module.render((an_item(href=None),))
    assert 'data-readable="false"' in rendered
    assert "Your first class" in rendered
    assert "<a " not in rendered


def test_a_unit_with_a_page_is_linked_and_marked_readable():
    rendered = listing_module.render((an_item(),))
    assert 'data-readable="true"' in rendered
    assert '<a href="unit-01-a.unit.html">' in rendered


@pytest.mark.parametrize("href", list(REFUSED.values()), ids=list(REFUSED))
def test_a_refused_href_raises_rather_than_dropping_the_row(href):
    # ⛔ THE decision of this module. `page.navigation._link` drops a refused
    # slot because the bar is chrome; here the links ARE the page, and a silent
    # drop is a module's contents rendered unclickable with nothing raised —
    # `SF-13/1`'s defect with no acceptance clause left to catch it.
    assert safe_href(href) is None, "the fixture must actually be refused"
    with pytest.raises(PageError, match="position 1"):
        listing_module.render((an_item(href=href),))


@pytest.mark.parametrize("href", list(REFUSED.values()), ids=list(REFUSED))
def test_no_refusal_reproduces_the_href_it_refused(href):
    # ⛔ R7. The shapes refused here are exactly the shapes that carry a home
    # directory, and this runs over every unit in a corpus, into a build log.
    with pytest.raises(PageError) as raised:
        listing_module.render((an_item(href=href),))
    assert href not in str(raised.value)
    assert POISON not in str(raised.value)


def test_the_position_a_refusal_names_is_the_position_in_the_list():
    with pytest.raises(PageError, match="position 3"):
        listing_module.render((an_item(), an_item(), an_item(href="/rooted.html")))


def test_a_title_is_escaped_and_its_inline_markers_render():
    rendered = listing_module.render((an_item(title="`a < b` and **c**", href=None),))
    assert "<code>a &lt; b</code>" in rendered
    assert "<strong>c</strong>" in rendered
    assert "a < b" not in rendered


def test_an_href_is_escaped_into_its_attribute():
    rendered = listing_module.render((an_item(href="unit-01.unit.html?a=1&b=2"),))
    assert 'href="unit-01.unit.html?a=1&amp;b=2"' in rendered


def test_numbering_is_wrapped_and_its_trailing_space_goes_with_it():
    # ⚠️ The conditional separator lives with the numbering, or an unnumbered
    # corpus renders a page that differs from its golden by one character.
    numbered = listing_module.render((an_item(numbering="4.4.1", href=None),))
    assert '<span data-kind="numbering">4.4.1</span> Your first class' in numbered
    plain = listing_module.render((an_item(numbering="", href=None),))
    assert "data-kind" not in plain
    assert plain.endswith('<li data-readable="false">Your first class</li></ol></nav>')


def test_the_list_is_labelled_and_ordered():
    rendered = listing_module.render((an_item(),))
    assert rendered.startswith('<nav aria-label="Units"><ol>')
    assert rendered.endswith("</ol></nav>")


def test_not_one_class_name_is_typed_in_this_module():
    # ⛔ Every hook is an element, an `aria-label` or a `data-*` attribute —
    # which is what let `SF-34` be scheduled a milestone after this markup. A
    # class here would need an entry in a published class set two packages away.
    rendered = listing_module.render((an_item(), an_item(href=None)))
    assert re.search(r'\sclass="', rendered) is None
