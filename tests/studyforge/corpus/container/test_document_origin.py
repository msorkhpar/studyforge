"""`container_api: 2` — an `origin` that names a region (SF-36, Ruling 92).

⛔ **A sibling of `test_document.py` rather than an addition to it.** That
module is 598 lines against R11's 600 test ceiling and `W40` splits it; a row
that needed one more line there would either break the ceiling or wait for a
queued task. ⚠️ The two assertions it already carried about the version set
were **corrected in place**, at the same line count, because they built their
expectations out of `CONTAINER_API` itself.

⭐ **Every version here is a literal.** `KNOWN_CONTAINER_API == {CONTAINER_API}`
was true before this task and after it; a set spelled out of the constant it
accompanies cannot fail when the constant moves.
"""

import json

import pytest

from studyforge.corpus.container import (
    CONTAINER_API,
    KNOWN_CONTAINER_API,
    ORIGIN_KEYS,
    REGION_ORIGIN_API,
    Container,
    ContainerError,
    Unit,
    from_document,
    parse,
    render,
    to_document,
)
from studyforge.corpus.manifest import from_document as manifest_from_document

MANIFEST = {
    "corpus_api": 1,
    "source": "demo",
    "title": "Demo",
    "levels": ["section"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["**/*.md"]},
}

REGION = {"path": "TestCases.md", "section": "3. Card issuance"}


def manifest():
    return manifest_from_document(MANIFEST, "corpus.json")


def document(*, container_api=2, units=None):
    return {
        "container_api": container_api,
        "address": ["depth-one"],
        "titles": ["Depth One"],
        "variant": "prose",
        "ingested": "2026-01-05",
        "units": units
        if units is not None
        else [{"n": 1, "title": "One", "practices": 0, "origin": dict(REGION)}],
    }


def built(**overrides):
    return from_document(document(**overrides), "container.json", manifest())


def refusal(**overrides):
    with pytest.raises(ContainerError) as raised:
        built(**overrides)
    return str(raised.value)


# --------------------------------------------------------------------------
# ⛔ the version this task mints — `container_api`, and not `corpus_api`
# --------------------------------------------------------------------------


def test_a_region_is_read_by_the_version_this_build_writes():
    # ⚠️ **Corrected in place when `W428` minted 3**, exactly as this module's
    # own docstring records the previous correction: the assertion is that a
    # region is still read, and the version it is read at is a literal.
    assert CONTAINER_API == 3
    assert 2 in KNOWN_CONTAINER_API


def test_this_build_reads_one_two_and_three_and_nothing_else():
    assert KNOWN_CONTAINER_API == frozenset({1, 2, 3})


def test_a_region_is_a_version_two_shape():
    assert REGION_ORIGIN_API == 2


def test_the_version_above_this_build_s_is_refused_and_not_migrated():
    # ⛔ R9. The refusal for the version above this one must be as sharp as
    # the acceptance of this one, or the set is decorative.
    message = refusal(container_api=4)
    assert "container_api 4" in message
    assert "never migrated in place" in message


def test_a_version_one_map_with_no_region_still_parses():
    made = built(container_api=1, units=[{"n": 1, "title": "One", "practices": 0}])
    assert made.container_api == 1
    assert made.units[0].origin is None


def test_a_version_one_map_that_declares_a_region_is_refused_by_version():
    # ⛔ **R9's other direction.** A map using the new shape must be unreadable
    # to a build that speaks only the old version — so it may not call itself
    # the old version, or it slips past that build's check entirely.
    message = refusal(container_api=1)
    assert "container_api 1" in message
    assert "container_api 2" in message


def test_the_declared_version_is_kept_rather_than_promoted():
    # ⚠️ The round trip is the guarantee: a v1 map read and written back is a
    # v1 map. Promoting it would rewrite the one field saying which reader the
    # document was written for.
    text = json.dumps(document(container_api=1, units=[{"n": 1, "title": "One", "practices": 0}]))
    assert '"container_api": 1' in render(parse(text, "container.json", manifest()))


def test_the_render_path_cannot_mint_an_unreadable_map_either():
    # ⭐ Constructed in code rather than decoded, which is the path
    # `from_document`'s own check would never see.
    with pytest.raises(ContainerError):
        Container(
            address=built().address,
            titles=("Depth One",),
            variant="prose",
            ingested="2026-01-05",
            units=(Unit(1, "One", 0, "TestCases.md", "3. Card issuance"),),
            container_api=1,
        )


# --------------------------------------------------------------------------
# ⛔ the shape — a string, an object, and one key either way
# --------------------------------------------------------------------------


def test_a_string_origin_is_a_whole_file_and_carries_no_section():
    made = built(units=[{"n": 1, "title": "One", "practices": 0, "origin": "TestCases.md"}])
    assert (made.units[0].origin, made.units[0].origin_section) == ("TestCases.md", None)


def test_an_object_origin_is_a_path_and_a_section():
    unit = built().units[0]
    assert (unit.origin, unit.origin_section) == ("TestCases.md", "3. Card issuance")


def test_the_object_keys_are_path_and_section():
    assert ORIGIN_KEYS == ("path", "section")


def test_a_region_renders_back_as_the_object_it_was_read_from():
    assert to_document(built())["units"][0]["origin"] == {
        "path": "TestCases.md",
        "section": "3. Card issuance",
    }


def test_a_whole_file_renders_back_as_a_plain_string():
    made = built(units=[{"n": 1, "title": "One", "practices": 0, "origin": "TestCases.md"}])
    assert to_document(made)["units"][0]["origin"] == "TestCases.md"


def test_a_region_keeps_origins_place_in_the_key_order():
    entry = to_document(
        built(
            units=[
                {
                    "n": 1,
                    "title": "One",
                    "practices": 0,
                    "origin": dict(REGION),
                    "url_slug": "card-issuance",
                }
            ]
        )
    )["units"][0]
    assert list(entry) == ["n", "title", "practices", "origin", "url_slug"]


def test_a_region_round_trips_byte_for_byte():
    text = json.dumps(document(), indent=2, ensure_ascii=False) + "\n"
    assert render(parse(text, "container.json", manifest())) == text


def test_section_is_not_a_unit_key():
    # ⛔ The object is the *value* of `origin`. A `section` beside it is an
    # unknown key and is refused as one.
    message = refusal(
        units=[{"n": 1, "title": "One", "practices": 0, "origin": "T.md", "section": "3. Card"}]
    )
    assert "unknown key" in message


def test_seventeen_units_may_share_one_path_with_seventeen_sections():
    # ⭐ `F21` in miniature, and the reason the version exists.
    made = built(
        units=[
            {
                "n": n,
                "title": f"Unit {n}",
                "practices": 0,
                "origin": {"path": "T.md", "section": f"{n}. X"},
            }
            for n in range(1, 18)
        ]
    )
    assert len({unit.origin for unit in made.units}) == 1
    assert len({unit.origin_section for unit in made.units}) == 17
