"""Mirror of `src/studyforge/unit/content.py` (R12)."""

from __future__ import annotations

import json

import pytest

from studyforge.address import AddressError
from studyforge.unit import (
    CONTENT_API,
    CONTENT_FILENAME,
    DERIVED_FIELDS,
    OVERLAY_KEYS,
    ContentError,
    Overlay,
    from_document,
    load,
    parse,
)
from tests.support import repository_root

#: The fixture overlay's shape, minimally. Each test changes one thing.
BASE = {
    "content_api": 1,
    "address": ["basics", "01-getting-started"],
    "unit": 1,
    "title": "Your first class",
    "sections": [
        {
            "kind": "shared",
            "heading": "Before you start",
            "blocks": [{"type": "para", "text": "a"}],
        },
        {"kind": "lang", "lang": "java", "heading": "Your first class", "blocks": []},
    ],
}

FIXTURE = (
    repository_root()
    / "tests/fixtures/depth2/archive/basics/01-getting-started/units/unit-01/content.json"
)


def overlay(**overrides) -> Overlay:
    return from_document({**BASE, **overrides}, 2)


def refusal(**overrides) -> str:
    with pytest.raises(ContentError) as raised:
        overlay(**overrides)
    return str(raised.value)


# --- R21: located, versioned, one producer ---------------------------------


def test_the_overlay_is_versioned_and_the_key_is_content_api():
    # ⭐ Minted by SF-09 because R9's enumeration was written from the
    # generating side and this is the one document the framework only reads.
    # ⛔ R21: silence was not an option, so this is a decision.
    assert "content_api" in OVERLAY_KEYS
    assert overlay().content_api == CONTENT_API


@pytest.mark.parametrize("declared", [0, 2, 99, "1", 1.0, None, True])
def test_an_unknown_content_api_is_refused_and_never_migrated(declared):
    message = refusal(content_api=declared)
    assert "content_api" in message
    assert "never migrated in place" in message


def test_the_version_is_checked_through_the_shared_guard_and_not_a_local_copy():
    # ⚠️ SF-33 ships a tree test that fails any module rolling its own
    # membership test; this asserts the message that guard produces.
    assert "this build speaks content_api [1]" in refusal(content_api=99)


def test_the_file_it_lives_in_has_one_spelling():
    assert CONTENT_FILENAME == "content.json"


# --- the address is recorded, never derived --------------------------------


def test_the_address_is_a_list_of_slugs():
    assert overlay().address.key == "basics/01-getting-started"


@pytest.mark.parametrize("address", [["Basics", "01-getting-started"], ["Getting Started"]])
def test_an_address_spelled_as_titles_is_refused_rather_than_slugified(address):
    # ⛔ §6: an address is recorded, never derived. The extraction source let
    # an overlay spell its address as titles and slugified them to compare —
    # measured on that catalog, 157 of 1,290 units are served at a slug their
    # title does not produce, so that comparison accepts an overlay filed
    # under the wrong unit one time in eight.
    with pytest.raises((ContentError, AddressError)):
        overlay(address=address)


def test_an_address_of_the_wrong_arity_is_refused():
    assert "1 segment(s) deep" in refusal(address=["basics"])


@pytest.mark.parametrize("address", ["basics/01-getting-started", None, {}, 7])
def test_an_address_that_is_not_a_list_is_refused(address):
    assert "address" in refusal(address=address)


@pytest.mark.parametrize("unit", [0, -1, 1.0, True, None, "1"])
def test_a_unit_ordinal_that_is_not_one_is_refused(unit):
    with pytest.raises((ContentError, AddressError)):
        overlay(unit=unit)


@pytest.mark.parametrize("title", ["", "   ", None, 7])
def test_an_overlay_with_no_title_is_refused(title):
    assert "'title'" in refusal(title=title)


def test_the_title_is_a_title_and_not_a_slug():
    assert overlay(title="ISO-8583: Getting Started").title.startswith("ISO")


# --- keys and sections ------------------------------------------------------


def test_the_sections_keep_the_authors_order():
    # ⛔ Order is never re-derived: two consumers ordering differently would
    # mint different speech ids for one unit and desynchronise the page from
    # its audio.
    assert overlay().keys == ("shared", "java")


def test_two_sections_may_not_share_a_key():
    # ⛔ Two sections on one key mint the same audio filenames, and one unit's
    # narration then overwrites another's.
    sections = [
        {"kind": "lang", "lang": "java", "heading": "A", "blocks": [{"type": "para", "text": "a"}]},
        {"kind": "lang", "lang": "java", "heading": "B", "blocks": []},
    ]
    assert "both key on 'java'" in refusal(sections=sections)


def test_an_explicit_key_can_rescue_two_sections_of_one_kind():
    # ⭐ Which is what the escape hatch is for.
    sections = [
        {"kind": "lang", "lang": "java", "heading": "A", "blocks": [{"type": "para", "text": "a"}]},
        {"kind": "lang", "lang": "java", "key": "java-2", "heading": "B", "blocks": []},
    ]
    assert overlay(sections=sections).keys == ("java", "java-2")


def test_section_keys_are_unique_within_a_multi_variant_unit():
    # SF-09's acceptance, at the shape a multi-variant corpus produces.
    sections = [
        {"kind": "shared", "heading": "S", "blocks": [{"type": "para", "text": "a"}]},
        {"kind": "lang", "lang": "java", "heading": "J", "blocks": []},
        {"kind": "lang", "lang": "kotlin", "heading": "K", "blocks": []},
        {"kind": "practice", "lang": "java", "heading": "PJ", "blocks": []},
        {"kind": "practice", "lang": "kotlin", "heading": "PK", "blocks": []},
    ]
    keys = overlay(sections=sections).keys
    assert keys == ("shared", "java", "kotlin", "practice-java", "practice-kotlin")
    assert len(set(keys)) == len(keys)


@pytest.mark.parametrize("field", DERIVED_FIELDS)
def test_a_section_may_not_write_what_the_builder_derives(field):
    # ⛔ An author writing one is asserting something they are not the author
    # of, and it would be silently overwritten or, worse, silently believed.
    sections = [{**BASE["sections"][0], field: "anything"}]
    assert field in refusal(sections=sections)
    assert "not the author's to write" in refusal(sections=sections)


def test_an_unknown_key_in_a_section_is_refused():
    sections = [{**BASE["sections"][0], "language": "java"}]
    assert "unknown key" in refusal(sections=sections)


@pytest.mark.parametrize("sections", [[], None, {}, "sections"])
def test_an_overlay_with_no_sections_is_refused(sections):
    assert "'sections'" in refusal(sections=sections)


def test_an_overlay_whose_sections_hold_no_blocks_at_all_is_refused():
    # ⛔ Refusing to write an empty page: a unit with no blocks writes a
    # plausible page that says nothing.
    sections = [{"kind": "shared", "heading": "S", "blocks": []}]
    assert "refusing to write an empty page" in refusal(sections=sections)


def test_a_shared_section_may_not_name_a_variant():
    sections = [{**BASE["sections"][0], "lang": "java"}]
    assert "is 'shared' and also names a variant" in refusal(sections=sections)


@pytest.mark.parametrize("heading", ["", "  ", None, 7])
def test_a_section_with_no_heading_is_refused(heading):
    sections = [{**BASE["sections"][0], "heading": heading}]
    assert "'heading'" in refusal(sections=sections)


def test_a_block_type_the_vocabulary_does_not_name_is_refused():
    # ⛔ The type list is imported from SF-06, never restated: a block
    # vocabulary with two definitions is two answers to what a page may hold.
    sections = [{**BASE["sections"][0], "blocks": [{"type": "callout", "text": "x"}]}]
    assert "the block vocabulary does not name" in refusal(sections=sections)


def test_the_block_vocabulary_is_sf06s_and_not_a_copy():
    from studyforge.archive.blocks import BLOCK_TYPES

    sections = [{"kind": "shared", "heading": "S", "blocks": [{"type": t} for t in BLOCK_TYPES]}]
    assert overlay(sections=sections).block_count == len(BLOCK_TYPES)


# --- the document as text, and as a file ------------------------------------


def test_parse_reads_the_text_of_an_overlay():
    assert parse(json.dumps(BASE), 2).title == "Your first class"


@pytest.mark.parametrize("text", ["", "{", "[]", "null", "7"])
def test_text_that_is_not_an_overlay_object_is_refused(text):
    with pytest.raises(ContentError, match="not valid JSON|must be a JSON object"):
        parse(text, 2)


def test_the_json_parsers_own_message_is_not_formatted_into_the_refusal():
    # ⛔ R7: it quotes the offending line, and this is a file a person edits —
    # that line could be anything.
    with pytest.raises(ContentError) as raised:
        parse('{"title": ' + '"/' + 'home/somebody/secret", ', 2)
    assert "somebody" not in str(raised.value)
    assert "is not valid JSON" in str(raised.value)


def test_load_reads_one_overlay_from_disk(tmp_path):
    path = tmp_path / CONTENT_FILENAME
    path.write_text(json.dumps(BASE), encoding="utf-8")
    assert load(path, 2).unit == 1


def test_a_missing_overlay_is_refused_with_its_name_and_no_absolute_path(tmp_path):
    with pytest.raises(ContentError) as raised:
        load(tmp_path / CONTENT_FILENAME, 2)
    assert CONTENT_FILENAME in str(raised.value)
    assert str(tmp_path) not in str(raised.value)


def test_the_shared_fixture_parses_under_this_module():
    # ⚠️ The fixture MOVED for this: it carried no `content_api`, because
    # FND-04 followed R9's enumeration literally and shipped the overlay
    # unversioned, flagging it. Fixtures serve the contract, never the reverse.
    built = load(FIXTURE, 2)
    assert built.keys == ("shared", "java", "practice-java")
    assert built.content_api == CONTENT_API


# --- no refusal emits what it refuses (R7, rubric §1f) ---------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"address": "/" + "home/somebody/corpus"},
        {"title": 4},
        {"sections": [{"kind": "/" + "home/somebody", "heading": "H", "blocks": []}]},
        {
            "sections": [
                {"kind": "shared", "heading": "H", "blocks": [{"type": "/" + "home/somebody"}]}
            ]
        },
        {
            "sections": [
                {
                    "kind": "lang",
                    "lang": "java",
                    "key": "/" + "home/somebody/k",
                    "heading": "H",
                    "blocks": [],
                }
            ]
        },
    ],
)
def test_no_refusal_reproduces_a_value_from_the_authored_file(overrides):
    # ⛔ Rubric §1f, the emission clause: every R7 check before it asked whether
    # an identifier reached a FILE, and none asked whether the code would write
    # one into a LOG. This module reads the one file a person edits by hand, so
    # any string in it can be an absolute path — and each of these is a branch
    # that fires on a value the author supplied.
    #
    # ⚠️ The gate runs first and refuses two of these for carrying a home path,
    # which is the right answer; what this asserts is that the message never
    # carries the value, whichever branch produced it.
    with pytest.raises(ContentError) as raised:
        overlay(**overrides)
    assert "somebody" not in str(raised.value)


def test_a_refusal_still_says_enough_to_act_on():
    # ⚠️ The other half, or "describe rather than echo" becomes "say nothing".
    # An integer IS quoted: it is the one shape that cannot carry an identifier.
    message = refusal(sections=[{"kind": 7, "heading": "H", "blocks": []}])
    assert "section 0" in message and "7" in message and "shared" in message


# --- the personal-data gate is invoked, and only it can see the leak --------


def test_the_personal_data_gate_is_invoked_over_the_whole_document():
    # ⛔ SF-08's call-site clause: assert the gate IS invoked, not that the
    # data happens to be clean. ⭐ The leak is placed in a section `heading` —
    # a field this module validates only for non-emptiness, so no per-field
    # check here can see it. Only a whole-document sweep can, and if the sweep
    # were removed this test would go green with the leak still on the page.
    leak = "/" + "home/somebody/notes"
    sections = [{**BASE["sections"][0], "heading": f"See {leak} for context"}]
    message = refusal(sections=sections)
    assert "personal data" in message
    # ⛔ The SHAPE is named — "a home path" — and the value never is.
    assert "home path" in message
    assert "somebody" not in message


def test_the_gate_sees_a_leak_inside_a_block_that_nothing_else_reads():
    # The same argument one level deeper: block TEXT is never inspected here,
    # only a block's `type`. A leak in it is invisible to every other check.
    # ⚠️ Not `contact@example.com`: that is the documented PLACEHOLDER the
    # gate deliberately allows, so using it would have made this test pass
    # with no gate at all.
    leak = "j.doe" + "@corp.invalid"
    sections = [
        {"kind": "shared", "heading": "S", "blocks": [{"type": "para", "text": f"mail {leak}"}]}
    ]
    message = refusal(sections=sections)
    assert "personal data" in message
    assert "j.doe" not in message


def test_the_refusal_names_the_shape_and_never_the_value():
    leak = "/" + "home/somebody/notes"
    message = refusal(title=f"Notes at {leak}")
    assert "home path" in message
    assert "somebody" not in message
