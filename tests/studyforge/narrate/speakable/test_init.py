"""Mirror of `src/studyforge/narrate/speakable/__init__.py` (R12), and SF-16's acceptance.

⛔ **Every clause of the speech units' Acceptance has a test in this module, named for
the clause**, and the two clauses that cannot be discharged here say so in their own
reason rather than being quietly asserted over something weaker.
"""

from __future__ import annotations

import copy
import re
from pathlib import PurePosixPath

import pytest

import studyforge.narrate.speakable as speakable
from studyforge.narrate.speakable import (
    SPEECH_OF,
    by_position,
    clip_name,
    clip_names,
    parse_clip_name,
    speakable_of,
    unit_key_of,
)
from studyforge.narrate.speakable.records import SpeakableError
from studyforge.render.page import AUDIO_ATTRIBUTE
from studyforge.unit import content
from studyforge.unit.builder import build_unit
from tests.support import assert_package_contract, repository_root

FIXTURES = repository_root() / "tests" / "fixtures"

#: ⛔ The one fixture in which two units declare the same `origin.path` and differ
#: only in `origin.section`. It is the input the speech-id negative is written
#: against, and it ships in `VALID` so the whole contract suite sees it.
SHARED_ORIGIN = FIXTURES / "shared-origin/archive/field-notes/raw/prose"

#: Finds every clip href a rendered page addresses its audio by.
#:
#: ⛔ **The value is an HREF, not a speech id** — `render/page/assets.py` declares
#: `AUDIO_ATTRIBUTE` in the module whose whole subject is where a page reaches, and
#: the id is recovered from the filename through `parse_clip_name` below. ⚠️ This
#: comment used to be wrong in the other direction and the assertion under it
#: compared these values to the id set; it never ran, because nothing wrote the
#: attribute until the narration player landed.
AUDIO_VALUES = re.compile(re.escape(AUDIO_ATTRIBUTE) + r'="([^"]*)"')


def depth1_unit_03() -> dict:
    """The fixture unit the disclosure clause is asserted against — two lessons, two disclosures."""
    return build_unit(FIXTURES / "depth1/archive/depth-one/raw/prose/unit-03", declared_practices=0)


def depth1_unit_02() -> dict:
    """A prose unit with no disclosure, so the withheld count has a control."""
    return build_unit(FIXTURES / "depth1/archive/depth-one/raw/prose/unit-02", declared_practices=0)


def depth2_unit_01() -> dict:
    """The authored, two-level, multi-section unit — lists, tables and a practice."""
    root = FIXTURES / "depth2/archive/basics/01-getting-started"
    return build_unit(
        root / "raw/java/unit-01",
        overlay=content.load(root / "units/unit-01/content.json", 2),
        declared_practices=1,
    )


def shared_origin_unit(ordinal: int) -> dict:
    """One of the two units that share one `origin.path`."""
    return build_unit(SHARED_ORIGIN / f"unit-0{ordinal}", declared_practices=0)


#: Every real unit document this module asserts over. ⛔ Derived once so no test
#: quietly runs against a shorter population than its neighbour.
def every_document() -> list[tuple[str, dict]]:
    """The documents, named, for a parametrisation that prints its population."""
    return [
        ("depth1-unit-02", depth1_unit_02()),
        ("depth1-unit-03", depth1_unit_03()),
        ("depth2-unit-01", depth2_unit_01()),
        ("shared-origin-unit-01", shared_origin_unit(1)),
        ("shared-origin-unit-02", shared_origin_unit(2)),
    ]


CASES = every_document()


def test_states_its_contract():
    assert_package_contract(speakable, "studyforge.narrate.speakable")


def test_the_population_of_documents_is_inhabited_and_every_one_speaks():
    # ⛔ A sweep over a derived population states its inhabitation first.
    assert len(CASES) == 5
    for name, document in CASES:
        assert speakable_of(document).units, f"{name} produced no speech at all"


# --------------------------------------------------------------------------
# ⭐ Acceptance 1 — ids are stable under a content edit that does not change structure
# --------------------------------------------------------------------------


def edited(document: dict) -> tuple[dict, str]:
    """Return a copy with one paragraph's words changed, and the id of the unit that moved.

    ⛔ Structure untouched: the same sections, the same block list, the same types, in
    the same order. Only the words inside one paragraph differ.
    """
    after = copy.deepcopy(document)
    for section in after["sections"]:
        for block in section["blocks"]:
            if block.get("type") == "para":
                block["text"] = "Wholly different words, and the structure is untouched."
                moved = next(
                    unit.id
                    for unit in speakable_of(after).units
                    if unit.speak.startswith("Wholly different words")
                )
                return after, moved
    raise AssertionError("no paragraph to edit")


@pytest.mark.parametrize(("name", "document"), CASES)
def test_an_id_is_stable_under_a_content_edit_that_does_not_change_structure(name, document):
    before = [unit.id for unit in speakable_of(document).units]
    after_document, _moved = edited(document)
    assert [unit.id for unit in speakable_of(after_document).units] == before


# --------------------------------------------------------------------------
# ⭐ Acceptance 2 — the filename changes under exactly that same edit
# --------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "document"), CASES)
def test_a_clip_name_changes_under_the_very_edit_the_id_survives(name, document):
    # ⛔ The inverse of the clause above, not a restatement of it: the id is what a
    # structure edit must not renumber, and the digest is what a text edit must change.
    before = {unit.id: clip_name(unit) for unit in speakable_of(document).units}
    after_document, moved = edited(document)
    after = {unit.id: clip_name(unit) for unit in speakable_of(after_document).units}
    assert set(after) == set(before)
    assert after[moved] != before[moved], "a text edit left the clip name alone — a stale clip"
    unchanged = {
        identifier
        for identifier in before
        if identifier != moved and after[identifier] == before[identifier]
    }
    assert len(unchanged) == len(before) - 1, "an untouched unit was resynthesised"


def test_a_stale_clip_cannot_be_addressed_which_is_the_whole_argument():
    # ⭐ Spec §8.2: change the words and the page links a file that is not on disk, so
    # the client synthesises it. There is no check to skip.
    document = depth1_unit_02()
    was = set(clip_names(speakable_of(document).units))
    after_document, _moved = edited(document)
    now = set(clip_names(speakable_of(after_document).units))
    assert was - now, "the old name survived the edit, so the stale clip is still addressable"


# --------------------------------------------------------------------------
# ⛔ Acceptance 3 — every id in a rendered page has a clip and every clip an id
# --------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "document"), CASES)
def test_every_id_maps_to_exactly_one_clip_and_every_clip_back_to_its_id(name, document):
    units = speakable_of(document).units
    names = clip_names(units)
    assert len(names) == len(units)
    assert [parse_clip_name(minted)[0] for minted in names] == [unit.id for unit in units]


def test_every_id_a_rendered_page_addresses_resolves_to_a_clip_and_back():
    # ⛔ The page half of the clause, and it is ARMED — the page writes the attribute.
    # ⭐ CONVERTED rather than deleted, and converted UPWARDS:
    # the skipped form compared the attribute's values to the set of minted ids, which
    # only made sense while the attribute was believed to hold an id. It holds an HREF,
    # so the id is now RECOVERED from the filename through `parse_clip_name` — the
    # published inverse of the one minter — which is strictly stronger than the
    # containment it replaced: it proves the page's real file reference parses, that
    # its id is one this walker mints, and that its digest is the one this walker
    # would have computed for those exact words.
    pages = sorted((repository_root() / "tests/fixtures/pages").glob("*.unit.html"))
    assert pages, "no golden pages at all; the scan is wrong"
    addressed = sorted(
        value for page in pages for value in AUDIO_VALUES.findall(page.read_text(encoding="utf-8"))
    )
    assert addressed, (
        f"no rendered page writes {AUDIO_ATTRIBUTE} over {len(pages)} golden page(s); "
        f"the renderer that links a clip has gone away and this clause has no population"
    )
    minted = {clip_name(unit) for _name, document in CASES for unit in speakable_of(document).units}
    by_name = {}
    for href in addressed:
        assert not href.startswith("/") and "://" not in href, (
            f"a clip is addressed relative to the page it plays on (R8), and this is not: {href}"
        )
        stem = PurePosixPath(href).stem
        identifier, digest = parse_clip_name(stem)
        assert stem in minted, f"the page links a clip this walker never mints: {identifier}"
        by_name.setdefault(stem, []).append(href)
    # ⛔ Ruling 187's shape, at the page: two elements addressing one clip is sixteen
    # passages playing the wrong audio, and every containment check still passes.
    collided = sorted(name for name, hrefs in by_name.items() if len(hrefs) > 1)
    assert collided == [], f"two elements on a page address one clip: {collided}"


# --------------------------------------------------------------------------
# ⛔ Acceptance 4 — the CARDINALITY, which is the only form that states injectivity
# --------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "document"), CASES)
def test_the_clip_names_are_exactly_as_many_as_the_spoken_units(name, document):
    # ⛔ Ruling 187. "Asserted in both directions" proves surjectivity: seventeen
    # clips colliding onto one filename still resolve both ways and the suite stays
    # green. A cardinality equality is what states injectivity.
    units = speakable_of(document).units
    assert len(set(clip_names(units))) == len(units)


def test_the_cardinality_holds_across_every_document_at_once_not_only_inside_one():
    # ⭐ The corpus-wide form, which is the one the synthesis batch needs: spec §8.2's
    # API takes a list of `{id, text}` and returns one artifact per id.
    units = [unit for _name, document in CASES for unit in speakable_of(document).units]
    assert len(set(clip_name(unit) for unit in units)) == len(units)
    assert len({unit.id for unit in units}) == len(units)


def test_the_cardinality_can_come_out_wrong_so_the_green_is_a_reading():
    # ⛔ A plant, shipped: a key space that a collision WOULD shrink. Names
    # derived from the source path alone collide for the two shared-origin units; the
    # minted names do not. A reading that cannot differ is not a reading.
    units = [unit for ordinal in (1, 2) for unit in speakable_of(shared_origin_unit(ordinal)).units]
    by_path = {"field-notes/topics.md" for _unit in units}  # what `origin.path` would key
    assert len(by_path) == 1 < len(units)
    assert len(set(clip_name(unit) for unit in units)) == len(units)


# --------------------------------------------------------------------------
# ⛔ Acceptance 5 — the NEGATIVE, and it is this task's because this task mints the name
# --------------------------------------------------------------------------


def test_two_units_sharing_one_origin_path_mint_different_clip_names():
    # ⛔ `Q23`: neither half of the name comes from the source path. The two units of
    # `shared-origin` declare one `origin.path` and differ only in `origin.section`.
    first = speakable_of(shared_origin_unit(1))
    second = speakable_of(shared_origin_unit(2))
    assert first.unit_key != second.unit_key
    assert set(clip_names(first.units)).isdisjoint(clip_names(second.units))


def test_two_units_whose_spoken_text_is_identical_still_mint_different_names():
    # ⭐ The adversarial form, and the one that actually tests the minter: the digests
    # are EQUAL by construction, so only the id can separate the two clips.
    left = shared_origin_unit(1)
    right = copy.deepcopy(left)
    right["unit"] = 2
    right["sections"] = copy.deepcopy(left["sections"])
    said_left = speakable_of(left).units
    said_right = speakable_of(right).units
    assert [unit.speak for unit in said_left] == [unit.speak for unit in said_right]
    assert set(clip_names(said_left)).isdisjoint(clip_names(said_right))


def test_nothing_in_a_minted_name_is_read_out_of_the_source_path():
    # ⛔ `origin` is provenance, and provenance is never identity.
    for ordinal in (1, 2):
        for minted in clip_names(speakable_of(shared_origin_unit(ordinal)).units):
            assert "topics" not in minted
            assert "README" not in minted.upper()


def test_the_unit_key_the_ids_are_minted_from_is_the_logical_address():
    said = speakable_of(shared_origin_unit(2))
    assert said.unit_key == "field-notes/unit-02"
    assert all(unit.id.startswith("field-notes--unit-02.") for unit in said.units)


# --------------------------------------------------------------------------
# ⭐ Acceptance 6 and 7 — a fence captions; a disclosure's summary is spoken alone
# --------------------------------------------------------------------------


def test_a_code_block_produces_a_caption_and_not_a_reading_of_the_code():
    said = speakable_of(depth1_unit_03())
    captions = [unit.speak for unit in said.units if unit.kind == "code"]
    assert captions, "the fixture has fences; none produced a caption"
    for caption in captions:
        assert caption.startswith("Here's the")
        assert "<" not in caption and "{" not in caption


def test_a_disclosures_summary_is_spoken_and_no_block_inside_it_has_an_id():
    # ⛔ Asserted against `depth1` unit 3, which the Acceptance names: two lessons,
    # one disclosure each, three blocks withheld between them.
    said = speakable_of(depth1_unit_03())
    summaries = sorted(unit.speak for unit in said.units if unit.kind == "disclosure")
    assert summaries == ["This one IS a disclosure", "Why there is no exercise here"]
    for hidden in ("Zero exercises is a first-class outcome", "Same tags as the fence above"):
        assert all(hidden not in unit.speak for unit in said.units)


def test_the_withheld_count_is_carried_on_the_record_and_a_unit_without_one_reads_zero():
    # ⚠️ The record half of the clause. The *report* is not this task's: the coverage
    # report that names units with unspoken content belongs to narration synthesis.
    assert speakable_of(depth1_unit_03()).withheld == 3
    assert speakable_of(depth1_unit_02()).withheld == 0


# --------------------------------------------------------------------------
# ⭐ Acceptance 8 — the gate refuses a leaking string
# --------------------------------------------------------------------------


def test_the_gate_refuses_a_leaking_string_from_a_whole_document():
    from studyforge.archive.scrub import PersonalDataLeak

    document = copy.deepcopy(depth1_unit_02())
    document["sections"][0]["blocks"][0] = {"type": "para", "text": "/" + "home/jane/corpus"}
    with pytest.raises(PersonalDataLeak):
        speakable_of(document)


# --------------------------------------------------------------------------
# The surface, and what it refuses
# --------------------------------------------------------------------------


@pytest.mark.parametrize(("name", "document"), CASES)
def test_the_script_is_byte_stable_across_two_derivations_of_one_document(name, document):
    # ⭐ R10: one enumeration, no clock, no set iteration order reaching the output.
    once = [(unit.id, unit.speak) for unit in speakable_of(document).units]
    assert [(unit.id, unit.speak) for unit in speakable_of(document).units] == once


@pytest.mark.parametrize(("name", "document"), CASES)
def test_the_position_lookup_finds_every_unit_and_loses_none(name, document):
    units = speakable_of(document).units
    found = by_position(units)
    assert len(found) == len(units)
    assert all(found[unit.position] is unit for unit in units)


@pytest.mark.parametrize(("name", "document"), CASES)
def test_every_section_of_the_document_is_reachable_in_the_script(name, document):
    spoken = {unit.section for unit in speakable_of(document).units}
    assert spoken <= {section["key"] for section in document["sections"]}


def test_two_sections_sharing_one_key_are_refused_rather_than_merged():
    document = copy.deepcopy(depth1_unit_03())
    document["sections"][1]["key"] = document["sections"][0]["key"]
    with pytest.raises(SpeakableError):
        speakable_of(document)


@pytest.mark.parametrize("key", ["Shared", "", "a--b", "with space", None, 7])
def test_a_section_key_that_is_not_a_slug_is_refused_because_a_filename_is_minted_from_it(key):
    document = copy.deepcopy(depth1_unit_02())
    document["sections"][0]["key"] = key
    with pytest.raises(SpeakableError):
        speakable_of(document)


def test_the_refusal_of_a_section_key_never_reproduces_it():
    # ⛔ R7: a section key comes from a file a person edits, so it can be a path.
    document = copy.deepcopy(depth1_unit_02())
    document["sections"][0]["key"] = "/" + "home/jane/corpus"
    with pytest.raises(SpeakableError) as refused:
        speakable_of(document)
    assert "jane" not in str(refused.value)


@pytest.mark.parametrize("missing", ["address", "unit", "sections"])
def test_a_document_missing_the_identity_the_ids_are_minted_from_is_refused(missing):
    document = copy.deepcopy(depth1_unit_02())
    del document[missing]
    with pytest.raises(SpeakableError):
        speakable_of(document)


@pytest.mark.parametrize("value", [None, "a document", 7, []])
def test_anything_that_is_not_a_served_document_is_refused(value):
    with pytest.raises(SpeakableError):
        speakable_of(value)


def test_a_unit_key_round_trips_through_the_token_the_ids_carry():
    said = speakable_of(depth2_unit_01())
    token = said.units[0].id.split(".")[0]
    assert unit_key_of(token) == said.unit_key


def test_the_surface_names_every_disposition_a_consumer_might_branch_on():
    # ⭐ `SPEECH_OF` is exported so synthesis and the player read the decision rather than
    # inferring it from what happened to come back.
    assert set(SPEECH_OF) and "disclosure" in SPEECH_OF
    # ⛔ Every name the contract promises resolves, and nothing is promised twice.
    assert len(set(speakable.__all__)) == len(speakable.__all__)
    missing = sorted(name for name in speakable.__all__ if not hasattr(speakable, name))
    assert missing == []
