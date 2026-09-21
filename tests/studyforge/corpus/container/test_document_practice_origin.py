"""`container_api: 3` — a unit whose practice came from a file of its own (`W428`).

⛔ **A sibling of `test_document.py` rather than an addition to it**, for the
reason `test_document_origin.py` states: that module is against R11's test
ceiling and a row that needed one more line there would have to break it.

⭐ **Every version here is a literal.** A set spelled out of the constant it
accompanies cannot fail when the constant moves.
"""

import json

import pytest

from studyforge.corpus.container import (
    CONTAINER_API,
    KNOWN_CONTAINER_API,
    PRACTICE_ORIGIN_API,
    UNIT_KEYS,
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
    "exercises": True,
    "placement": "tree",
    "content": {"include": ["**/*.md"]},
}

UNIT = {
    "n": 1,
    "title": "Message Type Indicators",
    "practices": 1,
    "origin": "src/4.md",
    "practice_origin": "src/p1.md",
}


def manifest():
    return manifest_from_document(MANIFEST, "corpus.json")


def document(*, container_api=3, units=None):
    return {
        "container_api": container_api,
        "address": ["demo"],
        "titles": ["Demo"],
        "variant": "prose",
        "ingested": "2026-01-05",
        "units": [dict(UNIT)] if units is None else units,
    }


def built(**overrides):
    return from_document(document(**overrides), "container.json", manifest())


def refusal(**overrides):
    with pytest.raises(ContainerError) as raised:
        built(**overrides)
    return str(raised.value)


# --------------------------------------------------------------------------
# ⛔ the version this row mints
# --------------------------------------------------------------------------


def test_this_build_writes_version_three():
    assert CONTAINER_API == 3


def test_a_practice_origin_is_a_version_three_shape():
    assert PRACTICE_ORIGIN_API == 3


def test_the_set_this_build_reads_is_spelled_out():
    assert KNOWN_CONTAINER_API == frozenset({1, 2, 3})


def test_a_version_two_map_that_declares_one_is_refused_by_version():
    # ⛔ **R9's other direction, and the reason a version was minted at all.**
    # A build that cannot see `practice_origin` would sum both files' headings
    # against one of them and report a short read on a corpus that is
    # complete — so it must be unable to read the map, not merely unaware.
    message = refusal(container_api=2)
    assert "container_api 2" in message
    assert "container_api 3" in message
    assert "refused rather than read" in message


def test_a_version_two_map_with_no_practice_origin_still_parses():
    made = built(container_api=2, units=[{"n": 1, "title": "One", "practices": 0}])
    assert made.container_api == 2
    assert made.units[0].practice_origin is None


def test_the_declared_version_is_kept_rather_than_promoted():
    text = json.dumps(document(container_api=1, units=[{"n": 1, "title": "One", "practices": 0}]))
    assert '"container_api": 1' in render(parse(text, "container.json", manifest()))


# --------------------------------------------------------------------------
# ⛔ the shape, and what it refuses
# --------------------------------------------------------------------------


def test_the_key_is_read_into_the_unit():
    unit = built().units[0]
    assert unit.origin == "src/4.md"
    assert unit.practice_origin == "src/p1.md"
    assert unit.practice_origin_section is None


def test_it_is_a_unit_key_and_its_section_is_not():
    # ⛔ Exactly as `origin`'s is: the object is the *value* of one key, so the
    # region half never appears on disk as a key of its own.
    assert "practice_origin" in UNIT_KEYS
    assert "practice_origin_section" not in UNIT_KEYS


def test_it_carries_the_region_shape_too():
    region = {"path": "src/p1.md", "section": "Problem statement"}
    unit = built(units=[{**UNIT, "practice_origin": region}]).units[0]
    assert unit.practice_origin == "src/p1.md"
    assert unit.practice_origin_section == "Problem statement"


def test_a_unit_entry_keeps_its_key_order():
    # ⛔ **Moved here from `test_document.py` by `W428`**, because the only
    # shape that can assert the order is one with every optional key set — an
    # absent key is omitted rather than written null — and `practice_origin`
    # made that shape a `container_api` 3 one. ⚠️ The module it left is against
    # R11's test ceiling, which is why this is a move and not a copy.
    entry = to_document(
        built(
            units=[
                {
                    **UNIT,
                    "url_slug": "one",
                    "label": "4.4.1",
                    "note": "why",
                }
            ]
        )
    )["units"][0]
    assert tuple(entry) == UNIT_KEYS


def test_a_region_round_trips_in_place():
    region = {"path": "src/p1.md", "section": "Problem statement"}
    entry = to_document(built(units=[{**UNIT, "practice_origin": region}]))["units"][0]
    assert entry["practice_origin"] == region
    assert tuple(entry) == tuple(k for k in UNIT_KEYS if k in entry)


def test_both_origins_may_be_regions_at_once():
    unit = built(
        units=[
            {
                **UNIT,
                "origin": {"path": "src/4.md", "section": "MTIs"},
                "practice_origin": {"path": "src/p1.md", "section": "Problem statement"},
            }
        ]
    ).units[0]
    assert (unit.origin, unit.origin_section) == ("src/4.md", "MTIs")
    assert (unit.practice_origin, unit.practice_origin_section) == (
        "src/p1.md",
        "Problem statement",
    )


def test_a_practice_origin_with_no_origin_is_refused():
    # ⚠️ The key *means* "not the file the prose came from". With no prose
    # file there is no other file, and the one path belongs in `origin`, where
    # everything that places a page can see it.
    message = refusal(units=[{"n": 1, "title": "One", "practices": 1, "practice_origin": "p.md"}])
    assert "practice_origin and no origin" in message


def test_an_absolute_practice_origin_is_refused_without_echoing_it():
    # ⚠️ Not a home-shaped one: that is caught a step earlier by R7's gate,
    # which `test_document.py` already holds. This is the path rule itself.
    absolute = "/srv/material/p1.md"
    message = refusal(units=[{**UNIT, "practice_origin": absolute}])
    assert "practice_origin" in message
    assert absolute not in message


def test_a_fragment_practice_origin_is_refused():
    assert "fragment" in refusal(units=[{**UNIT, "practice_origin": "src/p1.md#problem"}])


def test_the_default_is_absent_rather_than_empty():
    assert Unit(n=1, title="One", practices=0).practice_origin is None
    assert (
        "practice_origin"
        not in to_document(
            built(container_api=1, units=[{"n": 1, "title": "One", "practices": 0}])
        )["units"][0]
    )


def test_it_places_nothing():
    # ⛔ `origin` is what placement reads. A practice that moved the page it
    # joined would move a page a reader is already reading.
    import inspect

    from studyforge.contents import tree
    from studyforge.corpus import placement
    from studyforge.generate import declarations

    for module in (placement.profile, declarations, tree):
        assert "practice_origin" not in inspect.getsource(module)
