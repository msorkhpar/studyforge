"""Mirror of `src/studyforge/archive/markdown/listing.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, parse
from studyforge.archive.markdown.listing import read_list


def blocks(text: str) -> list[dict]:
    """Parse `text` and return its blocks."""
    return parse(text)


def test_bullet_list():
    assert blocks("- one\n- two\n") == [{"type": "list", "ordered": False, "items": ["one", "two"]}]


def test_ordered_list():
    assert blocks("1. one\n2. two\n") == [
        {"type": "list", "ordered": True, "items": ["one", "two"]}
    ]


def test_a_paren_marker_starts_an_ordered_list():
    assert blocks("1) one\n2) two\n")[0]["ordered"] is True


def test_a_bare_number_and_paren_mid_sentence_is_still_prose():
    assert blocks("see step 1) of the guide\n")[0]["type"] == "para"


@pytest.mark.parametrize("gap", ["\n", "\n\n", "\n\n\n"])
def test_blank_lines_between_items_do_not_split_the_list(gap):
    # CommonMark's "loose" list: still one list.
    assert blocks(f"- one\n{gap}- two\n") == [
        {"type": "list", "ordered": False, "items": ["one", "two"]}
    ]


def test_a_blank_line_then_prose_ends_the_list():
    assert [block["type"] for block in blocks("- one\n\nprose\n")] == ["list", "para"]


def test_a_change_of_list_kind_ends_the_list_even_across_a_blank_line():
    parsed = blocks("- one\n\n1. two\n")
    assert [block["ordered"] for block in parsed] == [False, True]


def test_a_blank_line_then_a_fence_ends_the_list():
    assert [block["type"] for block in blocks("- one\n\n```py\nx = 1\n```\n")] == ["list", "code"]


def test_a_fence_inside_a_list_item_keeps_the_list_whole():
    # ⛔ How setup steps are written. Without this the list ends at item 1 and
    # the fence, the next item and the closing paragraph all become top-level.
    text = "1. Create a project:\n   ```bash\n   gradle init\n   ```\n2. Then build it.\n"
    parsed = blocks(text)
    assert [block["type"] for block in parsed] == ["list", "code"]
    assert parsed[0]["items"] == ["Create a project:", "Then build it."]
    assert parsed[1]["text"] == "gradle init"


def test_a_fence_indented_under_an_item_after_a_blank_line_still_belongs_to_it():
    text = "1. Step one\n\n    ```bash\n    make\n    ```\n\n2. Step two\n"
    parsed = blocks(text)
    assert parsed[0]["items"] == ["Step one", "Step two"]
    assert parsed[1] == {"type": "code", "lang": "bash", "text": "make"}


def test_a_list_whose_fence_never_closes_still_raises():
    with pytest.raises(MarkdownError):
        blocks("1. Step:\n   ```bash\n   make\n")


def test_a_list_item_continues_onto_the_next_line_without_a_blank():
    # ⛔ CommonMark's lazy continuation, and authors use it: ending the list
    # there makes the sentence a paragraph, one block more than the material.
    parsed = blocks("- **Best Practice:**\nname the thing you are doing.\n")
    assert parsed == [
        {
            "type": "list",
            "ordered": False,
            "items": ["**Best Practice:** name the thing you are doing."],
        }
    ]


def test_a_blank_line_still_ends_an_item_rather_than_continuing_it():
    assert [block["type"] for block in blocks("- one\n\nnot a continuation\n")] == ["list", "para"]


def test_a_continuation_line_that_starts_a_block_ends_the_list_instead():
    assert [block["type"] for block in blocks("- one\n## a heading\n")] == ["list", "heading"]


def test_a_nested_item_folds_into_the_item_above_it():
    # ⭐ The block model is flat, so the nesting is lost either way; folding
    # keeps the words, splitting puts a paragraph where the material has a
    # sub-item and shifts every block after it.
    text = "1. **Centralized control**: one unit.\n\n   - *Core idea*: a single place.\n"
    parsed = blocks(text)
    assert parsed == [
        {
            "type": "list",
            "ordered": True,
            "items": ["**Centralized control**: one unit. *Core idea*: a single place."],
        }
    ]


def test_an_indented_paragraph_under_an_item_folds_into_it_too():
    parsed = blocks("- one\n\n  more about one\n")
    assert parsed[0]["items"] == ["one more about one"]


def test_an_unindented_line_after_an_items_fence_ends_the_list():
    # ⛔ A fenced code block closes an open paragraph, so a line at column zero
    # after an item's fence is a new paragraph.
    text = "1. Step:\n   ```bash\n   make\n   ```\nNote: version 5.9.3\n"
    parsed = blocks(text)
    assert [block["type"] for block in parsed] == ["list", "code", "para"]
    assert parsed[2]["text"] == "Note: version 5.9.3"


def test_the_code_follows_the_whole_list():
    text = "1. one\n   ```py\n   a\n   ```\n2. two\n   ```py\n   b\n   ```\n"
    parsed = blocks(text)
    assert [block["type"] for block in parsed] == ["list", "code", "code"]
    assert parsed[0]["items"] == ["one", "two"]


def test_read_list_returns_several_blocks_and_where_it_stopped():
    lines = ["- one", "- two", "", "after"]
    made, index = read_list(lines, 0)
    assert made == [{"type": "list", "ordered": False, "items": ["one", "two"]}]
    assert index == 2
