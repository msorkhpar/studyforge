"""Mirror of `src/studyforge/corpus/placement/identity.py` (R12).

⭐ Both halves and the round-trip are tested **here, a milestone before SF-04
reads any of it** — which is the whole reason the block is defined in SF-03.
"""

from __future__ import annotations

import json

import pytest

from studyforge.address import Address, AddressError
from studyforge.corpus.placement import (
    IDENTITY_API,
    IDENTITY_ELEMENT_ID,
    IDENTITY_KEYS,
    Identity,
    PlacementError,
    identity,
)

ADDRESS = Address.of("basics", "16-streams-api")
UNIT = Identity(corpus="example-corpus", address=ADDRESS, variant="java", unit=7)
CONTAINER = Identity(corpus="example-corpus", address=ADDRESS, variant="java", kind="container")


def page(block, before="<!doctype html><html><head>", after="</head><body>x</body></html>"):
    return before + block + after


# --- what a page says about itself -----------------------------------------


def test_the_block_carries_everything_a_scan_needs_to_place_a_page():
    document = UNIT.document
    assert document["corpus"] == "example-corpus"
    assert document["address"] == ["basics", "16-streams-api"]
    assert document["unit"] == 7
    assert document["variant"] == "java"
    assert document["kind"] == "unit"
    assert document["identity_api"] == IDENTITY_API


def test_the_keys_are_written_in_a_fixed_order():
    # ⛔ R10: an unchanged page must re-render to identical bytes, so the order
    # is stated rather than sorted.
    assert list(UNIT.document) == list(IDENTITY_KEYS)
    assert list(CONTAINER.document) == [key for key in IDENTITY_KEYS if key != "unit"]


def test_a_container_page_addresses_no_unit():
    assert "unit" not in CONTAINER.document
    with pytest.raises(PlacementError, match="addresses no unit"):
        Identity(corpus="c", address=ADDRESS, variant="java", kind="container", unit=1)


def test_a_unit_page_must_address_one():
    with pytest.raises(AddressError, match="identity 'unit'"):
        Identity(corpus="c", address=ADDRESS, variant="java")


# --- rendered, and read back ------------------------------------------------


def test_the_block_renders_on_one_line():
    # ⛔ A scan that had to tolerate reflowed JSON would be a scan tolerating
    # anything — and pages are compared byte for byte (R10).
    assert "\n" not in identity.render(UNIT)


def test_the_marker_is_fixed_here_rather_than_chosen_by_a_renderer():
    rendered = identity.render(UNIT)
    assert f'id="{IDENTITY_ELEMENT_ID}"' in rendered
    assert 'type="application/json"' in rendered


@pytest.mark.parametrize("block", [UNIT, CONTAINER])
def test_what_is_written_is_what_is_read_back(block):
    assert identity.parse(page(identity.render(block)), ADDRESS.depth) == block


def test_a_page_is_identified_wherever_it_ends_up():
    # ⛔ R4, stated as the property the whole package exists for: identity is
    # embedded, so a move changes nothing about what the page IS. ⚠️ Its
    # stylesheet and its audio legitimately break, because they resolve
    # relative to the page (R8) — that is not a defect and no test here
    # requires a moved page to render.
    html = page(identity.render(UNIT))
    assert identity.parse(html, 2) == UNIT
    moved = page(identity.render(UNIT), before="<html>", after="</html>")
    assert identity.parse(moved, 2) == UNIT


def test_the_block_is_found_whatever_order_the_attributes_are_in():
    # ⚠️ It reads files this build may not have written.
    html = page(
        f'<script id="{IDENTITY_ELEMENT_ID}" type="application/json">'
        f"{json.dumps(UNIT.document)}</script>"
    )
    assert identity.parse(html, 2) == UNIT


# --- what it refuses --------------------------------------------------------


def test_an_artifact_with_no_identity_block_is_reported_by_name():
    # ⛔ R6, and it is SF-04's acceptance too: never skipped silently.
    with pytest.raises(PlacementError, match="carries no identity block"):
        identity.parse("<html><body>a page nobody stamped</body></html>", 2, "16-x/page.unit.html")


def test_the_report_names_the_file_it_was_reading():
    with pytest.raises(PlacementError) as raised:
        identity.parse("<html></html>", 2, "16-streams-api/x.unit.html")
    assert "16-streams-api/x.unit.html" in str(raised.value)


def test_an_unknown_identity_api_is_refused_and_never_migrated():
    # ⛔ R9, through the one shared gate.
    document = dict(UNIT.document, identity_api=99)
    with pytest.raises(PlacementError, match="never migrated in place"):
        identity.from_document(document, 2)


@pytest.mark.parametrize("declared", [True, 1.0, "1", None])
def test_a_version_that_merely_resembles_one_is_refused(declared):
    document = dict(UNIT.document, identity_api=declared)
    with pytest.raises(PlacementError, match="identity_api"):
        identity.from_document(document, 2)


def test_a_block_that_is_not_json_is_refused_without_quoting_it():
    # ⛔ R7: a refusal that quotes an unreadable block has only relocated
    # whatever it held into a log.
    # ⚠️ Split for the R7 sweep, as in `test_errors.py`.
    leak = "/" + "home/example/leak"
    html = page(
        f'<script type="application/json" id="{IDENTITY_ELEMENT_ID}">{{"corpus": "{leak}"</script>'
    )
    with pytest.raises(PlacementError) as raised:
        identity.parse(html, 2)
    assert "/home/" not in str(raised.value)
    assert "not valid JSON" in str(raised.value)


def test_an_address_of_the_wrong_arity_is_refused_by_sf01():
    # ⚠️ The boundary, again: SF-01 owns the comparison and this module does
    # not restate it.
    with pytest.raises(AddressError, match="the corpus declares"):
        identity.parse(page(identity.render(UNIT)), 1)


def test_an_unknown_key_in_the_block_is_refused():
    with pytest.raises(PlacementError, match="unknown key"):
        identity.from_document(dict(UNIT.document, chapter=2), 2)


@pytest.mark.parametrize("field", ["corpus", "variant"])
def test_a_missing_required_field_is_refused(field):
    document = {key: value for key, value in UNIT.document.items() if key != field}
    with pytest.raises(PlacementError, match=field):
        identity.from_document(document, 2)


@pytest.mark.parametrize("value", ["Example", "example corpus", ""])
def test_the_corpus_and_variant_are_slugs_because_they_are_identities(value):
    with pytest.raises(AddressError):
        Identity(corpus=value, address=ADDRESS, variant="java", unit=1)


def test_an_unknown_kind_is_refused():
    with pytest.raises(PlacementError, match="kind"):
        Identity(corpus="c", address=ADDRESS, variant="java", kind="lesson", unit=1)
