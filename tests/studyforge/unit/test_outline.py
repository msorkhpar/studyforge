"""Mirror of `src/studyforge/unit/outline.py` (R12): the source's outline number is not served.

⛔ **Every expectation is a literal**, written before the run: a test that built
its expected title from the module's own pattern would move with it.
"""

from __future__ import annotations

import pytest

from studyforge.unit.builder import Material, build
from studyforge.unit.outline import headings_without_outline_numbers, without_outline_number

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
