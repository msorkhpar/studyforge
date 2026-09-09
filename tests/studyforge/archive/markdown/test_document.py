"""Mirror of `src/studyforge/archive/markdown/document.py` (R12)."""

from __future__ import annotations

from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES
from studyforge.archive.markdown import parse


def test_blank_input_is_no_blocks():
    assert parse("") == []
    assert parse("\n\n   \n") == []


def test_crlf_input_parses_the_same_as_lf():
    # ⛔ Every pattern anchors on `$`; a stray trailing `\r` would make every
    # one of them silently miss.
    body = "# h\n\ntext\n\n- one\n"
    assert parse(body.replace("\n", "\r\n")) == parse(body)
    assert parse(body.replace("\n", "\r")) == parse(body)


def test_a_multi_block_document_keeps_every_block_in_order():
    text = (
        "# Title\n\nProse.\n\n---\n\n- one\n- two\n\n"
        "| a | b |\n| --- | --- |\n| 1 | 2 |\n\n"
        "```py\nx = 1\n```\n\n> quoted\n\n"
        "<details>\n<summary>s</summary>\n\nhidden\n\n</details>\n\n"
        "<div>\n<p>raw</p>\n</div>\n\n![alt](p.png)\n"
    )
    assert [block["type"] for block in parse(text)] == [
        "heading",
        "para",
        "rule",
        "list",
        "table",
        "code",
        "quote",
        "disclosure",
        "html",
        "image",
    ]


def test_every_type_the_reader_emits_is_in_the_vocabulary():
    # ⛔ `counts` in an archive document carries one key per type, so a type
    # this reader can emit and the vocabulary does not name is a document that
    # cannot be counted.
    text = (
        "# h\n\np\n\n---\n\n- i\n\n| a |\n| --- |\n| 1 |\n\n```\nc\n```\n\n"
        "> q\n\n<details>\n<summary>s</summary>\n\nb\n\n</details>\n\n"
        '<div>\nx\n</div>\n\n![a](b)\n\n<iframe src="v"></iframe>\n'
    )
    emitted = {block["type"] for block in parse(text)}
    assert emitted <= set(BLOCK_TYPES)
    assert emitted == set(BLOCK_TYPES), sorted(set(BLOCK_TYPES) - emitted)


def test_the_container_types_are_the_ones_that_hold_blocks():
    # ⭐ Named so that every walker recurses on them, and the *next* container
    # is not forgotten the way `disclosure` was.
    text = "> q\n\n<details>\n<summary>s</summary>\n\nb\n\n</details>\n"
    for block in parse(text):
        assert ("blocks" in block) == (block["type"] in CONTAINER_TYPES)


def test_the_vocabulary_is_eleven_types():
    assert len(BLOCK_TYPES) == 11
    assert len(set(BLOCK_TYPES)) == 11
    assert set(CONTAINER_TYPES) <= set(BLOCK_TYPES)


def test_the_language_default_reaches_a_fence_inside_a_container():
    quoted = parse("> ```\n> x = 1\n> ```\n", lang_default="java")
    assert quoted[0]["blocks"][0]["lang"] == "java"
    hidden = parse(
        "<details>\n<summary>s</summary>\n\n```\nx = 1\n```\n\n</details>\n", lang_default="java"
    )
    assert hidden[0]["blocks"][0]["lang"] == "java"
