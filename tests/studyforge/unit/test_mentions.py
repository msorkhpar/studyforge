"""Mirror of `src/studyforge/unit/mentions.py` (R12): a mention of another unit is served as it.

⛔ **Every expectation is a literal**, written before the run: a title or an
href built from the module's own index would move with it.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath

import pytest

from studyforge.unit.headings import headings
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


# --- a file, an anchor and a heading the prose links ------------------------

#: A unit's own headings, read before their numbers left, as `unit.builder` reads them.
OWN = headings(
    [
        {
            "key": "prose",
            "blocks": [
                {"type": "heading", "level": 1, "text": "3.2.1 Creating custom exceptions"},
                {"type": "heading", "level": 2, "text": "2.2. Bitmaps"},
                {"type": "heading", "level": 2, "text": "Introduction"},
            ],
        }
    ]
)

#: Another unit's headings in the same container, and its page.
OTHER = headings(
    [{"key": "prose", "blocks": [{"type": "heading", "level": 3, "text": "2.1. The MTI"}]}]
)


def on_disk(tmp_path, page: str = "s/12/u1.html") -> Mentions:
    """The unit, its container's headings and a corpus root holding two files."""
    for where in ("12-custom/src/main/Types.java", "shared/notes.txt"):
        (tmp_path / where).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / where).write_text("x\n", encoding="utf-8")
    numbered = Mentions.numbered(((PurePosixPath("s/12/u4.html"), OTHER),))
    return replace(mentions(page=page), numbers=numbered, root=tmp_path)


def served(value: Mentions, text: str) -> str:
    """One paragraph served by `Mentions.sections`, as the builder serves it."""
    sections = [{"key": "prose", "blocks": [{"type": "para", "text": text}]}]
    return value.sections(sections, OWN)[0]["blocks"][0]["text"]


@pytest.mark.parametrize(
    ("page", "written", "linked"),
    [
        # ⭐ Read from the unit's origin, addressed from wherever the page sits.
        ("s/12/u1.html", "[T](src/main/Types.java)", "[T](../../12-custom/src/main/Types.java)"),
        ("12-custom/u1.html", "[T](src/main/Types.java)", "[T](src/main/Types.java)"),
        (
            "12-custom/study/u1.html",
            "[T](./src/main/Types.java#L3)",
            "[T](../src/main/Types.java#L3)",
        ),
        ("s/12/u1.html", "[n](../shared/notes.txt)", "[n](../../shared/notes.txt)"),
    ],
)
def test_a_link_to_a_file_of_the_corpus_is_addressed_from_the_page(tmp_path, page, written, linked):
    assert served(on_disk(tmp_path, page), written) == linked


@pytest.mark.parametrize(
    "written",
    [
        "[gone](src/main/Gone.java)",
        "[out](../../elsewhere/Types.java)",
        "[rooted](/12-custom/src/main/Types.java)",
        "[a directory](src/main)",
        "[web](https://example.invalid/src/main/Types.java)",
    ],
)
def test_a_link_to_no_file_of_the_corpus_keeps_its_href(tmp_path, written):
    assert served(on_disk(tmp_path), written) == written


def test_with_no_root_no_file_is_linked(tmp_path):
    # ⛔ A site written anywhere but the corpus root keeps the author's href.
    assert served(replace(on_disk(tmp_path), root=None), "[T](src/main/Types.java)") == (
        "[T](src/main/Types.java)"
    )


@pytest.mark.parametrize(
    ("written", "linked"),
    [
        ("[Intro](#introduction)", "[Intro](#prose-b2)"),
        ("[Bitmaps](#22-bitmaps)", "[Bitmaps](#prose-b1)"),
        ("[Bitmaps](#Bitmaps)", "[Bitmaps](#prose-b1)"),
        ("[none](#nowhere)", "[none](#nowhere)"),
    ],
)
def test_an_in_page_anchor_links_the_heading_it_names(tmp_path, written, linked):
    assert served(on_disk(tmp_path), written) == linked


@pytest.mark.parametrize(
    ("written", "named"),
    [
        # ⭐ The unit's own heading: its words, an in-page link.
        ("Section 2.2 describes it.", "Section [Bitmaps](#prose-b1) describes it."),
        ("as in section\n2.2.", "as in section\n[Bitmaps](#prose-b1)."),
        # ⭐ Exactly one heading of the container, on another page.
        ("Section 2.1 calls them", "Section [The MTI](u4.html#prose-b0) calls them"),
        # ⛔ A unit's label is that unit, whatever heading it also numbers.
        ("section 3.2.1 first", "section *Creating custom exceptions* first"),
        # ⛔ No `section` before it, or a number no heading carries: kept.
        ("jPOS 2.2 and 2.1", "jPOS 2.2 and 2.1"),
        ("Subsection 2.2 and section 9.9", "Subsection 2.2 and section 9.9"),
        ("JLS (Section 12.4.2)", "JLS (Section 12.4.2)"),
    ],
)
def test_a_heading_s_number_after_section_is_served_as_its_words(tmp_path, written, named):
    assert served(on_disk(tmp_path), written) == named


def test_the_unit_s_own_references_are_served_with_no_corpus_at_all():
    # ⭐ The default names nothing of the corpus and still knows its own headings.
    assert served(Mentions(), "Section 2.2 and [i](#introduction)") == (
        "Section [Bitmaps](#prose-b1) and [i](#prose-b2)"
    )


def test_a_number_two_headings_of_the_container_share_names_neither():
    numbered = Mentions.numbered(
        ((PurePosixPath("a.html"), OTHER), (PurePosixPath("b.html"), OTHER))
    )
    assert numbered == {}
