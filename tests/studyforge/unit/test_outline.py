"""Mirror of `src/studyforge/unit/outline.py` (R12): the source's outline number is not served.

⛔ **Every expectation is a literal**, written before the run: a test that built
its expected title from the module's own pattern would move with it.
"""

from __future__ import annotations

import pytest

from studyforge.unit.builder import Material, build
from studyforge.unit.outline import (
    headings_without_outline_numbers,
    listed_numbering,
    outline_number,
    without_outline_number,
)

#: `(as the source writes it, as a reader is served it)`.
NUMBERED = [
    ("5.1.1.1 Thread states", "Thread states"),
    ("3.2.1. Batch processing", "Batch processing"),
    ("10.7.2 — ORM frameworks", "ORM frameworks"),
    ("10.7.2 - ORM frameworks", "ORM frameworks"),
    ("2.1 Account Balance Inquiries", "Account Balance Inquiries"),
    ("1.2.1 if/else statements in Java", "if/else statements in Java"),
    ("1. Card Issuance and Activation", "Card Issuance and Activation"),
    ("15. [Troubleshooting](src/15.md)", "[Troubleshooting](src/15.md)"),
    ("4.4: Streams", "Streams"),
    # ⛔ Whatever the next word looks like: lower case, code, punctuation, a quote.
    ("8.1 jPOS Logging Framework", "jPOS Logging Framework"),
    ("2.3 var", "var"),
    ("2.3.1 var", "var"),
    ("4.2 java.util.function", "java.util.function"),
    ("4.2.4 java.util.function interfaces", "java.util.function interfaces"),
    ("7.1 record patterns", "record patterns"),
    ("3.4 `switch` expressions", "`switch` expressions"),
    ("5.2 (optional) Streams", "(optional) Streams"),
    ('6.1 "Hello, world"', '"Hello, world"'),
    ("9.3 @Override", "@Override"),
    ("2.5 millionaire's problem", "millionaire's problem"),
]

#: ⛔ A number that is part of the words, kept to the character.
KEPT = [
    "Java 21 features",
    "ISO 8583 messages",
    "Top 10 pitfalls",
    "10 tips for records",
    "2024 in review",
    "8583 fields",
    "3.2.1",
    "1.5 million requests",
    "3.5 seconds of latency",
    "2.5 times faster",
    "1.5 x the heap",
    "4.5 ms per call",
    "1234.5 Not an outline",
    "Card issuance",
    "",
]


@pytest.mark.parametrize(("written", "served"), NUMBERED)
def test_a_leading_outline_number_is_not_served(written, served):
    assert without_outline_number(written) == served


@pytest.mark.parametrize("written", KEPT)
def test_a_number_that_is_part_of_the_words_is_kept(written):
    assert without_outline_number(written) == written


def test_a_value_that_is_not_a_string_comes_back_as_it_came():
    assert without_outline_number(None) is None


def test_every_heading_at_any_depth_loses_its_number_and_nothing_else_moves():
    blocks = [
        {"type": "heading", "level": 1, "text": "1.1.1 Primitive Data Types"},
        {"type": "para", "text": "1.1.1 is kept in prose."},
        {"type": "quote", "blocks": [{"type": "heading", "level": 3, "text": "2.3 Inside"}]},
    ]
    assert headings_without_outline_numbers(blocks) == [
        {"type": "heading", "level": 1, "text": "Primitive Data Types"},
        {"type": "para", "text": "1.1.1 is kept in prose."},
        {"type": "quote", "blocks": [{"type": "heading", "level": 3, "text": "Inside"}]},
    ]
    # ⭐ A copy: the archive's blocks are never edited.
    assert blocks[0]["text"] == "1.1.1 Primitive Data Types"


def _document(title: str, heading: str) -> dict:
    return {
        "raw_api": 1,
        "source": "demo",
        "address": ["basics"],
        "variant": "java",
        "unit": 1,
        "kind": "lesson",
        "ordinal": 1,
        "ingested": "2026-09-24",
        "title": title,
        "blocks": [{"type": "heading", "level": 1, "text": heading}],
    }


def test_the_served_unit_carries_its_title_and_headings_without_the_number():
    # ⭐ The page and its narration are both made from this document.
    served = build(Material((_document("5.1.1.1 Thread states", "5.1.1.1 Thread states"),)))
    assert served["title"] == "Thread states"
    assert served["sections"][0]["heading"] == "Thread states"
    assert served["sections"][0]["blocks"][0]["text"] == "Thread states"


def test_the_narration_is_made_from_the_heading_without_its_number():
    # ⭐ A clip is named by a digest of its words, so the words are the served ones.
    from studyforge.narrate.speakable import clip_name, speakable_of

    served = build(Material((_document("5.1.1.1 Thread states", "5.1.1.1 Thread states"),)))
    units = speakable_of(served).units
    assert [unit.speak for unit in units] == ["Thread states"]
    numbered = {
        **served,
        "sections": [
            {
                **served["sections"][0],
                "blocks": [{"type": "heading", "level": 1, "text": "5.1.1.1 Thread states"}],
            }
        ],
    }
    assert clip_name(speakable_of(numbered).units[0]) != clip_name(units[0])


@pytest.mark.parametrize(
    ("label", "ordinal", "listed"),
    [
        ("4.2.4", 3, "3"),
        ("6.6.1.1", 5, "5"),
        ("3.", 1, "1"),
        ("7", 7, "7"),
        ("A", 1, "A"),
        ("Appendix", 9, "Appendix"),
    ],
)
def test_a_listing_shows_a_units_place_and_never_an_outline_label(label, ordinal, listed):
    # ⭐ The label keeps the number for order and the file name; the listing does not show it.
    assert listed_numbering(label, ordinal) == listed


@pytest.mark.parametrize(
    ("written", "served"),
    [
        (
            "**8.3.2.1. Extracting patterns** -- into utilities",
            "**Extracting patterns** -- into utilities",
        ),
        ("[7.3.2.1. LocalDate](README_7.3.2.1.md)", "[LocalDate](README_7.3.2.1.md)"),
        ("7.3.2 Overview", "Overview"),
        ("2.1. Setup", "Setup"),
    ],
)
def test_a_list_items_opening_outline_number_is_not_served(written, served):
    blocks = [{"type": "list", "ordered": False, "items": [written, [written, "after"]]}]
    assert headings_without_outline_numbers(blocks) == [
        {"type": "list", "ordered": False, "items": [served, [served, "after"]]}
    ]


@pytest.mark.parametrize(
    "written",
    [
        "1.5 million requests",
        "100.0 and 100.00 are the same amount",
        "2.0 is out",
        "Java 21",
        "1. first",
    ],
)
def test_a_list_item_that_opens_with_a_number_of_its_words_is_kept(written):
    blocks = [{"type": "list", "ordered": True, "items": [written]}]
    assert headings_without_outline_numbers(blocks) == blocks


def test_a_paragraph_that_is_only_an_outline_is_served_as_a_list_of_its_entries():
    written = "7.2.1. Batch processing 7.2.2. Clearing files 7.2.3. Settlement between acquirers"
    assert headings_without_outline_numbers([{"type": "para", "text": written}]) == [
        {
            "type": "list",
            "ordered": False,
            "items": ["Batch processing", "Clearing files", "Settlement between acquirers"],
        }
    ]


@pytest.mark.parametrize(
    "written",
    [
        "7.2.1. Batch processing",
        "Read 7.2.1. Batch processing 7.2.2. Clearing files",
        "7.2.1. Batch processing 7.3.1. Chargebacks",
        "1. Compiler reordering: the JMM allows 2. more",
    ],
)
def test_any_other_paragraph_keeps_every_character(written):
    blocks = [{"type": "para", "text": written}]
    assert headings_without_outline_numbers(blocks) == blocks


@pytest.mark.parametrize(
    ("heading", "number"),
    [
        ("2.2. Bitmaps", "2.2"),
        ("5.1.1.1 Thread states", "5.1.1.1"),
        ("1. Card Issuance", "1"),
        ("10.7.2 — ORM frameworks", "10.7.2"),
        # ⛔ Only a number the served heading lost: one that is part of the words is none.
        ("Java 21 features", None),
        ("1.5 million requests", None),
        ("Bitmaps", None),
        (None, None),
    ],
)
def test_the_number_a_heading_loses_is_what_names_it(heading, number):
    assert outline_number(heading) == number


def test_a_sentence_names_a_heading_by_the_number_it_lost_and_is_served_its_words():
    # ⭐ Read before the number leaves, served after: the page and its narration agree.
    from studyforge.narrate.speakable import speakable_of

    document = _document("2. Structure", "2.2. Bitmaps")
    document["blocks"].append({"type": "para", "text": "Section 2.2 describes it."})
    served = build(Material((document,)))
    assert served["sections"][0]["blocks"] == [
        {"type": "heading", "level": 1, "text": "Bitmaps"},
        {"type": "para", "text": "Section [Bitmaps](#java-b0) describes it."},
    ]
    assert [unit.speak for unit in speakable_of(served).units] == [
        "Bitmaps",
        "Section Bitmaps describes it.",
    ]


def test_a_heading_s_own_number_is_never_served_as_a_mention_of_its_unit():
    # ⛔ The number leaves BEFORE the mentions are served: a unit whose label is its
    # heading's number is headed by its words, never by its title and then its words.
    from pathlib import PurePosixPath

    from studyforge.unit.mentions import Mentions

    labels, origins = Mentions.of(
        (("1.1.1", "a.md", "Primitive data types", PurePosixPath("a.html"), ()),)
    )
    document = _document("1.1.1 Primitive Data Types", "1.1.1 Primitive Data Types")
    served = build(Material((document,)), mentions=Mentions(labels, origins))
    assert served["sections"][0]["blocks"] == [
        {"type": "heading", "level": 1, "text": "Primitive Data Types"}
    ]
