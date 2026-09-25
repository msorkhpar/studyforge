"""Mirror of `src/studyforge/unit/mentions.py` (R12): a mention of another unit is served as it.

⛔ **Every expectation is a literal**, written before the run: a title or an
href built from the module's own index would move with it.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.unit.mentions import Mentions

#: `(label, origin, title, page)`: three units of one container, and one of another.
UNITS = (
    ("3.2.1", "12-custom/README_3.2.1.md", "3.2.1. Creating custom exceptions", "s/12/u1.html"),
    ("3.2.4", "12-custom/README_3.2.4.md", "Checked vs. unchecked", "s/12/u4.html"),
    ("3.1.3", "11-try/README_3.1.3.md", "The finally block", "s/11/u3.html"),
    ("4.2", "13-lambda/README_4.2.md", "Lambdas", "s/13/u2.html"),
)


def mentions(origin: str = "12-custom/README_3.2.1.md", page: str = "s/12/u1.html") -> Mentions:
    labels, origins = Mentions.of(
        tuple((label, at, title, PurePosixPath(to)) for label, at, title, to in UNITS)
    )
    return Mentions(labels, origins, origin, PurePosixPath(page))


@pytest.mark.parametrize(
    ("written", "served"),
    [
        # ⭐ A bare label is the unit's title, in emphasis; the title loses its own number.
        ("see 3.2.4 first.", "see *Checked vs. unchecked* first."),
        ("(see 3.2.1 and 3.1.3)", "(see *Creating custom exceptions* and *The finally block*)"),
        ("covered in section 3.1.3.", "covered in section *The finally block*."),
        # ⭐ A link to a unit's source file links its page, and its number label is the title.
        ("See [3.2.4](README_3.2.4.md).", "See [Checked vs. unchecked](u4.html)."),
        ("[3.1.3](../11-try/README_3.1.3.md)", "[The finally block](../11/u3.html)"),
        ("[3.2.4. Checked](README_3.2.4.md)", "[Checked](u4.html)"),
        ("[the rules](./README_3.2.4.md#choose)", "[the rules](u4.html)"),
        # ⭐ A two-part label is a title inside a link's label only.
        ("[4.2](../13-lambda/README_4.2.md)", "[Lambdas](../13/u2.html)"),
    ],
)
def test_a_mention_of_a_unit_is_served_as_that_unit(written, served):
    assert mentions().text(written) == served


@pytest.mark.parametrize(
    "written",
    [
        "JLS §17.4.5 and JLS 9.6.4.2 name no unit.",
        "Since Java 1.4, and JDBC 4.2+, and HTTP/1.1.",
        "a two-part label in a sentence, 4.2, is kept",
        "`see 3.2.4` in code is code",
        "version 3.2.40, 13.2.4, 3.2.4x and v3.2.4 name none",
        "[a page](https://example.invalid/README_3.2.4.md)",
        "[missing](README_9.9.9.md) and [rooted](/README_3.2.4.md)",
        "1.5 million requests",
    ],
)
def test_a_number_or_link_that_names_no_unit_is_kept(written):
    assert mentions().text(written) == written


def test_a_label_two_units_share_names_neither():
    labels, _ = Mentions.of(
        (
            ("1.1.1", "a.md", "One", PurePosixPath("a.html")),
            ("1.1.1", "b.md", "Other", PurePosixPath("b.html")),
        )
    )
    assert labels == {}


def test_every_prose_field_at_any_depth_is_served_and_code_is_not():
    blocks = [
        {"type": "heading", "level": 2, "text": "After 3.2.4"},
        {"type": "para", "text": "see 3.2.4"},
        {"type": "code", "lang": "java", "text": "// see 3.2.4"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "see 3.2.4",
                ["see 3.1.3", {"type": "code", "lang": "java", "text": "3.2.4"}],
            ],
        },
        {"type": "table", "headers": ["3.2.4"], "rows": [["see 3.1.3"]]},
        {"type": "quote", "blocks": [{"type": "para", "text": "see 3.2.4"}]},
        {"type": "disclosure", "summary": "3.2.4", "open": False, "blocks": []},
    ]
    served = mentions().served(blocks)
    assert served == [
        {"type": "heading", "level": 2, "text": "After *Checked vs. unchecked*"},
        {"type": "para", "text": "see *Checked vs. unchecked*"},
        {"type": "code", "lang": "java", "text": "// see 3.2.4"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "see *Checked vs. unchecked*",
                ["see *The finally block*", {"type": "code", "lang": "java", "text": "3.2.4"}],
            ],
        },
        {
            "type": "table",
            "headers": ["*Checked vs. unchecked*"],
            "rows": [["see *The finally block*"]],
        },
        {"type": "quote", "blocks": [{"type": "para", "text": "see *Checked vs. unchecked*"}]},
        {"type": "disclosure", "summary": "*Checked vs. unchecked*", "open": False, "blocks": []},
    ]
    # ⭐ A copy: the archive's blocks are never edited.
    assert blocks[1]["text"] == "see 3.2.4"


def test_mentions_that_name_nothing_serve_the_blocks_as_they_came():
    blocks = [{"type": "para", "text": "see 3.2.4"}]
    assert Mentions().served(blocks) is blocks
