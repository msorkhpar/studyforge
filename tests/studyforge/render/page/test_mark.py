"""Mirror of `src/studyforge/render/page/mark.py` (R12).

⭐ **The assertion that matters most is not about one page.** A read mark is
written by the unit page under a key and read back by two other pages under the
same key, and the failure mode is **silent**: a badge that never lights, with
every page rendering, every golden matching and nothing raised anywhere. ⛔ So
the join is asserted over the **committed goldens** — three page kinds, two
placement profiles, one question — rather than over a document this file built.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.render import templates
from studyforge.render.page import PageError
from studyforge.render.page import mark as mark_module
from tests.studyforge.render.page.pages import GOLDEN_DIR


def a_document(**overrides) -> dict:
    """A unit page's document, reduced to the two fields a mark is filed under.

    ⚠️ `render` takes the whole document because `page.document` hands it the
    whole document; nothing else in it reaches this module.
    """
    fields = {"address": ["basics", "01-getting-started"], "unit": 1}
    return {**fields, **overrides}


#: A path shaped like the one thing R7 exists for. ⛔ Assembled from fragments,
#: never written whole, because a real home path in a tracked file is a finding
#: against this file by the sweep it is here to exercise.
A_HOME_PATH = "/" + "home/example/material"

#: How a golden page names the unit key it is about, and how a list row does.
#: ⛔ Read off the page rather than taken from a renderer, so a renderer that
#: stopped emitting the hook fails here instead of agreeing with itself.
CONTROL_KEY = re.compile(r'<section data-section="read-mark" data-unit="([^"]+)"')
ROW_KEY = re.compile(r'<li id="([^"]+)"')
INDEX_SUFFIX = ".index.html"
UNIT_SUFFIX = ".unit.html"
CONTAINER_SUFFIX = ".section.html"


def goldens(suffix: str) -> list[Path]:
    """Every committed golden page of one kind, sorted."""
    return sorted(path for path in GOLDEN_DIR.glob("*.html") if path.name.endswith(suffix))


def text_of(path: Path) -> str:
    """One golden page's exact text."""
    return path.read_bytes().decode("utf-8")


# --- the key is asked for, never composed ----------------------------------


def test_the_key_is_the_one_address_mints():
    # ⛔ `Address.unit_key` is the one composer, and its own docstring says why:
    # the page writes a read mark under it and the index reads the mark back.
    document = a_document()
    assert mark_module.key(document) == Address(("basics", "01-getting-started")).unit_key(1)


def test_nothing_in_this_module_composes_a_unit_name():
    # ⛔ The planted check's third row, at the door that matters. ⚠️ Asserted over the
    # SOURCE and not over the output: two spellings that agree today disagree the
    # day one of them is padded differently, and the symptom is a key that simply
    # never matches anything, with nothing failing anywhere.
    code = "\n".join(
        line
        for line in Path(mark_module.__file__).read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith(("#", "*", '"', "⛔", "⚠️", "⭐"))
    )
    assert "unit-" not in code, "this module spells a unit name instead of asking for one"
    assert "unit_key" in code, "and it must actually ask"


@pytest.mark.parametrize(
    "document,why",
    [
        ({"address": [], "unit": 1}, "no address at all"),
        ({"address": ["basics"], "unit": None}, "no ordinal"),
        ({"address": ["basics"], "unit": 0}, "an ordinal below the first"),
        ({"address": ["basics"], "unit": True}, "a flag passed as an ordinal"),
        ({"address": [A_HOME_PATH], "unit": 1}, "a segment that is a path"),
    ],
)
def test_a_document_that_cannot_be_keyed_raises_this_packages_own_error(document, why):
    # ⛔ Re-typed, not re-worded: a caller rendering a site catches one family per
    # page. ⚠️ `True` is in the population because `int` accepts it and `unit-01`
    # would be a whole unit's material filed under a flag.
    with pytest.raises(PageError) as refused:
        mark_module.render(document)
    assert "read mark" in str(refused.value), why


def test_an_address_recorded_as_a_string_is_refused_and_never_taken_apart():
    # ⛔ **A measured defect, not defensiveness.** `tuple("basics")` is six
    # single-character segments, every one a valid slug, so a string address would
    # key `b/a/s/i/c/s/unit-01` — refusing nothing and matching nothing. ⚠️ The
    # reading that found it: `mark.render({"address": "basics", "unit": 1})`
    # returned `data-unit="b/a/s/i/c/s/unit-01"` before this guard existed.
    with pytest.raises(PageError) as refused:
        mark_module.render(a_document(address="basics"))
    assert "list of slugs" in str(refused.value)
    assert "b/a/s" not in str(refused.value)


def test_no_refusal_reproduces_a_path_it_was_handed():
    # ⛔ R7, and this runs over every unit in a corpus into a build log.
    with pytest.raises(PageError) as refused:
        mark_module.render(a_document(address=[A_HOME_PATH]))
    assert A_HOME_PATH not in str(refused.value)


# --- the region itself ------------------------------------------------------


def test_the_region_comes_from_a_template_and_no_markup_is_typed_here():
    # R13, at the one place a whole element with attributes could have arrived as
    # a Python string. ⭐ And the reader-facing words are in the template too, so
    # changing what the page says about the store is editing markup.
    assert mark_module.CONTROL_TEMPLATE in templates.names()
    source = Path(mark_module.__file__).read_text(encoding="utf-8")
    assert "<section" not in source
    assert "<button" not in source


def test_the_region_ships_hidden_so_a_scriptless_reader_sees_no_dead_control():
    # ⛔ `copy-code.js`'s bargain: a control that does nothing is worse than no
    # control. The region is unhidden by `read-mark.js` only with a working store.
    #
    # ⚠️ **The REGION's own opening tag, and the first draft of this assertion was
    # `" hidden>" in region` — which PASSED with the region's `hidden` deleted,
    # because one of the two labels carries `hidden` too.** A plant refuted the
    # prediction written for it; this is the form that holds.
    region = mark_module.render(a_document())
    opening = region.split(">", 1)[0]
    assert opening.startswith("<section "), opening
    assert opening.endswith(" hidden"), f"the region itself is not hidden: {opening}"


def test_the_region_says_what_the_store_is():
    # ⛔ "The site says what the store is": one browser, one machine, not in the
    # repository, gone with site data. A reader who is not told this will assume
    # otherwise and be wrong at the worst moment.
    said = templates.template(mark_module.CONTROL_TEMPLATE).template.lower()
    for owed in ("this browser", "this machine", "repository", "clear"):
        assert owed in said, f"the region never says {owed!r}"


def test_the_control_is_a_button_and_nothing_is_inferred_from_reading():
    # ⛔ An explicit act, never inferred — not from scrolling, not from the
    # narration reaching the end, not from the page having been opened.
    region = mark_module.render(a_document())
    assert region.count("<button") == 1
    assert 'aria-pressed="false"' in region
    assert region.count("data-state=") == 2, "the two labels are the visible state"


def test_the_key_reaches_the_region_as_an_attribute():
    assert f'data-unit="{mark_module.key(a_document())}"' in mark_module.render(a_document())


def test_the_region_is_never_empty_for_a_page_that_can_be_keyed():
    # ⚠️ Unlike every other optional region: a unit page always has an address and
    # an ordinal, and one that declined the control is a page whose reading the
    # reader cannot record.
    assert mark_module.render(a_document()).strip() != ""


# --- the join, over the committed goldens -----------------------------------


def test_the_golden_population_is_inhabited():
    # ⛔ A derived-set assertion asserts inhabitation before it asserts
    # anything about the set, or every check below passes over nothing.
    assert goldens(UNIT_SUFFIX), "no committed unit page"
    assert goldens(CONTAINER_SUFFIX), "no committed container page"
    assert goldens(INDEX_SUFFIX), "no committed root index"


def test_every_golden_unit_page_offers_exactly_one_control():
    for path in goldens(UNIT_SUFFIX):
        found = CONTROL_KEY.findall(text_of(path))
        assert len(found) == 1, f"{path.name} carries {len(found)} read controls"


def test_the_control_sits_outside_the_reading_column():
    # ⭐ Why it matters beyond tidiness: `tests/visual/test_no_script.py` compares
    # `#content`'s own text with scripts on and off, and chrome inside `<main>`
    # would make that comparison about the decoration rather than the material.
    for path in goldens(UNIT_SUFFIX):
        page = text_of(path)
        assert page.index("</main>") < page.index('data-section="read-mark"')


def test_every_key_a_unit_page_writes_under_is_a_key_the_root_index_reads_back():
    # ⛔ **THE assertion of this task.** Two implementations are a mark written
    # under one name and read back under another, with no symptom but a badge that
    # never lights — so the two surfaces are compared rather than trusted.
    indexed = {key for path in goldens(INDEX_SUFFIX) for key in ROW_KEY.findall(text_of(path))}
    written = {key for path in goldens(UNIT_SUFFIX) for key in CONTROL_KEY.findall(text_of(path))}
    assert written, "no golden unit page names a key"
    assert written <= indexed, f"written and never read back: {sorted(written - indexed)}"


def test_every_container_row_is_keyed_the_way_the_root_index_keys_it():
    # ⭐ The second half, and it is the one that was missing: a container row
    # carried no key at all before `SF-30`, so the same mark could light a row on
    # one page and nothing on the other. ⚠️ Both placement profiles are in the
    # population — `depth1` is `tree` and `depth2` is `sibling` — and a key is not
    # a path, so the two must agree anyway.
    indexed = {key for path in goldens(INDEX_SUFFIX) for key in ROW_KEY.findall(text_of(path))}
    listed = {key for path in goldens(CONTAINER_SUFFIX) for key in ROW_KEY.findall(text_of(path))}
    assert listed, "no golden container page keys its rows"
    assert listed <= indexed, f"listed and not in the tree: {sorted(listed - indexed)}"


def test_a_key_is_not_a_path_and_no_page_spells_one_as_a_filename():
    # ⛔ R4: a key names a unit, a path says where a file happens to sit. A key
    # carrying `.html` would be the two collapsed, and a page moved would lose
    # every mark the reader had made.
    keys = {
        key
        for path in goldens(INDEX_SUFFIX) + goldens(CONTAINER_SUFFIX) + goldens(UNIT_SUFFIX)
        for pattern in (ROW_KEY, CONTROL_KEY)
        for key in pattern.findall(text_of(path))
    }
    assert keys
    assert [key for key in sorted(keys) if ".html" in key or key.startswith("/")] == []
