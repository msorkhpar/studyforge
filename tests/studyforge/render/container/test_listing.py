"""Mirror of `src/studyforge/render/container/listing.py` (R12).

⭐ The list is the page, so this module carries the assertions that matter most:
declared order is kept, an unlinkable unit is listed rather than dropped, and a
**refused** href raises instead of vanishing — the one place this package
deliberately differs from the between-units bar.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.render.container import Item, PageError
from studyforge.render.container import listing as listing_module
from studyforge.render.markup import safe_href
from studyforge.render.pageassets import SURFACE_HOOKS

#: The container every row below belongs to. ⛔ An `Address`, because the keys
#: the rows carry are minted by `Address.unit_key` and never spelled here — a
#: test that typed `"basics/01-intro/unit-01"` would be the second spelling the
#: one composer exists to prevent (`SF-30`).
WHERE = Address(("basics", "01-getting-started"))

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


def render(items: tuple[Item, ...]) -> str:
    """The module's `render`, with this file's one container supplied.

    ⚠️ Wrapped rather than repeated: the address is an argument now (`SF-30`),
    and nineteen call sites spelling it is nineteen places to forget it.
    """
    return listing_module.render(WHERE, items)


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
    rendered = render(items)
    assert rendered.index("Zeta") < rendered.index("Alpha")


def test_a_unit_with_no_page_is_listed_and_not_linked():
    # ⭐ §7's three states: an ungenerated unit is part of the material's shape
    # and a reader must see it. It is listed, marked, and carries no anchor.
    rendered = render((an_item(href=None),))
    assert 'data-readable="false"' in rendered
    assert "Your first class" in rendered
    assert "<a " not in rendered


def test_a_unit_with_a_page_is_linked_and_marked_readable():
    rendered = render((an_item(),))
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
        render((an_item(href=href),))


@pytest.mark.parametrize("href", list(REFUSED.values()), ids=list(REFUSED))
def test_no_refusal_reproduces_the_href_it_refused(href):
    # ⛔ R7. The shapes refused here are exactly the shapes that carry a home
    # directory, and this runs over every unit in a corpus, into a build log.
    with pytest.raises(PageError) as raised:
        render((an_item(href=href),))
    assert href not in str(raised.value)
    assert POISON not in str(raised.value)


def test_the_position_a_refusal_names_is_the_position_in_the_list():
    with pytest.raises(PageError, match="position 3"):
        render((an_item(), an_item(), an_item(href="/rooted.html")))


def test_a_title_is_escaped_and_its_inline_markers_render():
    rendered = render((an_item(title="`a < b` and **c**", href=None),))
    assert "<code>a &lt; b</code>" in rendered
    assert "<strong>c</strong>" in rendered
    assert "a < b" not in rendered


def test_an_href_is_escaped_into_its_attribute():
    rendered = render((an_item(href="unit-01.unit.html?a=1&b=2"),))
    assert 'href="unit-01.unit.html?a=1&amp;b=2"' in rendered


def test_numbering_is_wrapped_and_its_trailing_space_goes_with_it():
    # ⚠️ The conditional separator lives with the numbering, or an unnumbered
    # corpus renders a page that differs from its golden by one character.
    numbered = render((an_item(numbering="4.4.1", href=None),))
    assert '<span data-kind="numbering">4.4.1</span> Your first class' in numbered
    plain = render((an_item(numbering="", href=None),))
    # ⭐ The only `data-kind` left is the hidden read words every row ends with (`W383`).
    assert 'data-kind="numbering"' not in plain
    said = f'<span data-kind="{SURFACE_HOOKS["read_state"]}" hidden>'
    assert plain.count("data-kind") == plain.count(said) == 1
    assert f'<li id="{WHERE.unit_key(1)}" data-readable="false">Your first class{said}' in plain


def test_the_list_is_labelled_and_ordered():
    rendered = render((an_item(),))
    assert rendered.startswith('<nav aria-label="Units"><ol>')
    assert rendered.endswith("</ol></nav>")


def test_not_one_class_name_is_typed_in_this_module():
    # ⛔ Every hook is an element, an `aria-label` or a `data-*` attribute —
    # which is what let `SF-34` be scheduled a milestone after this markup. A
    # class here would need an entry in a published class set two packages away.
    rendered = render((an_item(), an_item(href=None)))
    assert re.search(r'\sclass="', rendered) is None


def test_every_row_carries_the_unit_key_a_read_mark_is_filed_under():
    # ⛔ `SF-30`'s join, and it is the whole reason the address reaches this
    # module. The mark the unit page writes and the mark this row reads back are
    # one string, or the badge never lights and nothing fails anywhere.
    rendered = render((an_item(), an_item(href=None), an_item()))
    ids = re.findall(r'<li id="([^"]+)"', rendered)
    assert ids == [WHERE.unit_key(n) for n in (1, 2, 3)], ids
    assert len(ids) == 3, "a row without a key is a row no mark can reach"


def test_the_key_is_asked_for_and_never_composed_in_this_module():
    # ⛔ Ruling 123's planted half, at the door that matters: `Address.unit_key`
    # is the one composer, so this module must contain no unit-name arithmetic of
    # its own. ⚠️ A second spelling differing by one character would simply never
    # match anything, with nothing failing anywhere — which is why the absence is
    # asserted over the SOURCE rather than inferred from the output above.
    source = Path(listing_module.__file__).read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith(("#", "*", '"'))
    )
    assert "unit-" not in code, "this module spells a unit name instead of asking for one"
    assert "unit_key" in code, "and it must actually ask"


def test_a_row_key_is_escaped_into_its_attribute():
    # ⚠️ Slugs cannot carry a quote today; the escape is here because the id is
    # an attribute and every attribute on this page goes through the same gate.
    rendered = render((an_item(),))
    assert f'<li id="{WHERE.unit_key(1)}" data-readable="true">' in rendered
