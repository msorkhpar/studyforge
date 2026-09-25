"""Mirror of `src/studyforge/unit/headings.py` (R12): a unit's headings, as its prose names them.

⛔ **Every expectation is a literal**, written before the run.
"""

from __future__ import annotations

from studyforge.unit.headings import Heading, by_number, by_slug, headings, source_slug

SECTIONS = [
    {
        "key": "prose",
        "blocks": [
            {"type": "heading", "level": 2, "text": "2. Message Structure"},
            {"type": "para", "text": "Prose."},
            {"type": "heading", "level": 3, "text": "2.1. Message Type Indicator (MTI)"},
            {"type": "heading", "level": 3, "text": "Key Points:"},
            {"type": "quote", "blocks": [{"type": "heading", "level": 3, "text": "2.9 Nested"}]},
            {"type": "heading", "level": 3, "text": "2.2. Bitmaps"},
            {"type": "heading", "level": 3, "text": "Key Points:"},
            {"type": "heading", "level": 3, "text": "  "},
        ],
    },
    {
        "key": "practice-prose",
        "blocks": [{"type": "heading", "level": 3, "text": "Java 21 [features](x.md)"}],
    },
]


def test_every_heading_of_a_section_s_own_run_is_indexed_with_its_page_id():
    assert headings(SECTIONS) == (
        Heading(
            "2",
            "Message Structure",
            "2-message-structure",
            "message-structure",
            "prose-b0",
            "#prose-b0",
        ),
        Heading(
            "2.1",
            "Message Type Indicator (MTI)",
            "21-message-type-indicator-mti",
            "message-type-indicator-mti",
            "prose-b2",
            "#prose-b2",
        ),
        Heading(None, "Key Points:", "key-points", "key-points", "prose-b3", "#prose-b3"),
        Heading("2.2", "Bitmaps", "22-bitmaps", "bitmaps", "prose-b5", "#prose-b5"),
        Heading(None, "Key Points:", "key-points", "key-points", "prose-b6", "#prose-b6"),
        Heading(
            None,
            "Java 21 [features](x.md)",
            "java-21-features",
            "java-21-features",
            "practice-prose-b0",
            "#practice-prose-b0",
        ),
    )


def test_a_source_anchor_is_its_host_s_and_a_repeat_is_suffixed():
    found = headings(SECTIONS)
    assert by_slug(found) == {
        "2-message-structure": "#prose-b0",
        "21-message-type-indicator-mti": "#prose-b2",
        "key-points": "#prose-b3",
        "22-bitmaps": "#prose-b5",
        "key-points-1": "#prose-b6",
        "java-21-features": "#practice-prose-b0",
        "message-structure": "#prose-b0",
        "message-type-indicator-mti": "#prose-b2",
        "bitmaps": "#prose-b5",
    }


def test_a_number_is_indexed_once_and_a_shared_one_names_neither():
    found = headings(SECTIONS)
    assert {number: heading.anchor for number, heading in by_number(found).items()} == {
        "2": "prose-b0",
        "2.1": "prose-b2",
        "2.2": "prose-b5",
    }
    twice = headings([{"key": "a", "blocks": [SECTIONS[0]["blocks"][5]] * 2}])
    assert by_number(twice) == {}


def test_the_slug_drops_what_a_markdown_host_drops():
    assert source_slug("Interview-specific Insights") == "interview-specific-insights"
    assert source_slug("Fixed-length vs. Variable-length fields") == (
        "fixed-length-vs-variable-length-fields"
    )
    assert source_slug("`var` and __init__") == "var-and-__init__"


def test_anything_that_is_not_sections_indexes_nothing():
    assert headings(None) == ()
    assert headings([None, {"key": 3, "blocks": []}, {"key": "a", "blocks": None}]) == ()
