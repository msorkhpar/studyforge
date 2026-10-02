"""Mirror of `render/page/blocks/example.py` (R12): one example, a tab per language."""

from __future__ import annotations

import re

from studyforge.corpus.manifest.reading import Language, Mode, Reading
from studyforge.render import modes
from studyforge.render.page import blocks
from studyforge.render.page.assets import Placement

LANGUAGES = (Language("aa", "Aa <lang>", ("aa",)), Language("bb", "Bb", ("bb",)))
MODES = (
    Mode("only-aa", "Aa", "Aa", "aa", ("aa",), ("aa",)),
    Mode("both-bb", "Bb first", "Bb first", "bb", ("bb", "aa"), ("bb", "aa")),
)
OFFER = modes.offer(Reading(languages=LANGUAGES, modes=MODES, default_mode="both-bb"))

EXAMPLE = {
    "type": "example",
    "id": "ex",
    "tabs": [{"lang": "aa", "span": 2}, {"lang": "bb", "span": 1}],
    "blocks": [
        {"type": "code", "lang": "aa", "text": "a != b"},
        {"type": "code", "lang": "text", "text": "printed <out>"},
        {"type": "code", "lang": "bb", "text": "b"},
    ],
}


class Where:
    """The one thing the renderer reads of a placement: the offer."""

    def __init__(self, offer):
        self.offer = offer


def draw(block=EXAMPLE, offer=OFFER, section="prose", position=3):
    return blocks.render_one(block, position, placement=Where(offer), section=section)


def test_the_example_type_has_a_renderer_and_the_dispatcher_does_not_draw_its_children_twice():
    assert "example" in blocks.RENDERERS
    assert Placement.__dataclass_fields__["offer"]


def test_the_panels_follow_the_default_modes_order_under_a_visible_label():
    page = draw()
    assert page.index('data-lang="bb"') < page.index('data-lang="aa"')
    assert page.count("<p data-example-label>") == 2
    assert "<p data-example-label>Aa &lt;lang&gt;</p>" in page
    assert 'data-langs="bb aa"' in page


def test_each_fence_lands_in_the_panel_of_its_own_language_and_is_escaped():
    page = draw()
    aa = re.search(r'<div role="tabpanel"[^>]*data-lang="aa">(.*?)</div>', page, re.S)
    assert aa is not None
    assert "a != b" in aa.group(1) and "printed &lt;out&gt;" in aa.group(1)
    assert ">b</code>" not in aa.group(1)


def test_the_tabs_are_wai_aria_tabs_with_roving_tabindex_and_linked_ids():
    page = draw()
    assert page.count('role="tablist"') == 1 and page.count('role="tab"') == 2
    assert page.count('role="tabpanel"') == 2
    assert page.count('aria-selected="false"') == 2 and page.count('tabindex="-1"') == 2
    assert page.count('tabindex="0"') == 2, "each panel is focusable"
    pairs = re.findall(r'id="([^"]+)" aria-selected="false" aria-controls="([^"]+)"', page)
    assert len(pairs) == 2
    for tab, panel in pairs:
        assert f'id="{panel}" aria-labelledby="{tab}"' in page
    assert "<div role=\"tablist\" aria-label=\"Language\" data-example-tabs hidden>" in page


def test_ids_are_minted_from_the_section_and_the_address_so_two_examples_never_share_one():
    first, second = draw(position=1), draw(position=2)
    ids = re.findall(r' id="([^"]+)"', first + second)
    assert len(ids) == len(set(ids)) == 8


def test_a_compiler_message_is_flagged_in_words_and_by_attribute():
    page = draw({**EXAMPLE, "output": "compiler"})
    assert 'data-output="compiler"' in page
    assert "<p data-example-flag>Does not compile, on purpose</p>" in page
    warned = draw({**EXAMPLE, "output": "warning"})
    assert "Compiles with a warning, on purpose" in warned and 'data-output="warning"' in warned
    assert "data-output" not in draw() and "data-example-flag" not in draw()


def test_a_corpus_that_declares_no_modes_gets_panels_under_labels_and_no_tab_bar():
    page = draw(offer=None)
    assert "role=\"tablist\"" not in page and "role=\"tab\"" not in page
    assert page.index('data-lang="aa"') < page.index('data-lang="bb"')
    assert "<p data-example-label>aa</p>" in page, "the id is the label when none is declared"


def test_nothing_in_an_example_is_narrated():
    assert "data-speak" not in draw() and "audio" not in draw()
