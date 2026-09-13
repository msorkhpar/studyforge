"""Mirror of `src/studyforge/archive/markdown/listing.py` (R12)."""

from __future__ import annotations

import re
from collections import Counter

import pytest

from studyforge.archive.document import content_sha256
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


#: ⛔ `W258`'s two-level fixture: a nested list four spaces under each item, one
#: unordered and one ordered, with a blank line between the parents.
TWO_LEVEL = (
    "- Version (1st digit):\n"
    "    - 0: first\n"
    "    - 1: second\n"
    "\n"
    "- Message Class:\n"
    "    1. Reserved\n"
    "    2. Authorization\n"
)

MARKER_WORD = re.compile(r"^(?:[-*]|\d+[.)])$")


def strings_of(value) -> list[str]:
    """Every string a block list carries, keys and flags aside."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for key, item in value.items() if key != "type" for s in strings_of(item)]
    if isinstance(value, list):
        return [s for item in value for s in strings_of(item)]
    return []


def words_of_source(text: str) -> Counter:
    """The source's words with every list marker taken out — what must survive."""
    return Counter(word for word in text.split() if not MARKER_WORD.match(word))


def test_a_nested_list_is_read_as_a_nested_list():
    # ⛔ W258 clause 1. An item holding a nested list is its parts in reading
    # order — its text, then the whole nested `list` block.
    assert blocks(TWO_LEVEL) == [
        {
            "type": "list",
            "ordered": False,
            "items": [
                [
                    "Version (1st digit):",
                    {"type": "list", "ordered": False, "items": ["0: first", "1: second"]},
                ],
                [
                    "Message Class:",
                    {"type": "list", "ordered": True, "items": ["Reserved", "Authorization"]},
                ],
            ],
        }
    ]


def test_no_nested_line_is_flattened_into_its_parents_text():
    # ⛔ The defect as received: `- 0: first` kept as literal text in its parent.
    for text in strings_of(blocks(TWO_LEVEL)):
        assert not re.search(r"(?:^|\s)(?:[-*]|\d+[.)]) ", text), text


def test_the_words_survive_the_nesting():
    # ⛔ The digest property: structure is added, and not one word is lost.
    parsed = blocks(TWO_LEVEL)
    assert Counter(" ".join(strings_of(parsed)).split()) == words_of_source(TWO_LEVEL)


@pytest.mark.parametrize(
    "text",
    [
        "- parent\n  - child\n",
        "- parent\n    - child\n",
        "- parent\n\n    - child\n",
        "1. parent\n   - child\n",
        "- parent\n        - child\n",
    ],
    ids=["indent-2", "indent-4", "after-a-blank", "under-an-ordered-item", "indent-8"],
)
def test_a_nested_list_is_read_at_any_indent_under_its_item(text):
    parsed = blocks(text)
    assert len(parsed) == 1
    assert parsed[0]["items"] == [
        ["parent", {"type": "list", "ordered": False, "items": ["child"]}]
    ]


def test_three_levels_are_the_same_rule_applied_again():
    parsed = blocks("- a\n  - b\n    - c\n  - d\n- e\n")
    inner = {"type": "list", "ordered": False, "items": ["c"]}
    middle = {"type": "list", "ordered": False, "items": [["b", inner], "d"]}
    assert parsed[0]["items"] == [["a", middle], "e"]


def test_text_after_a_nested_list_is_a_part_after_it_and_a_second_list_follows():
    # ⛔ Measured in a pinned corpus: a paragraph continues the item AFTER its
    # nested list, and a second nested list follows. Folded into the item's
    # text, the paragraph would move ahead of the list it was written after.
    text = "4. Autoboxing:\n\n    - costs memory\n\n   **When to use:**\n    - primitives\n"
    parsed = blocks(text)
    assert parsed[0]["items"] == [
        [
            "Autoboxing:",
            {"type": "list", "ordered": False, "items": ["costs memory"]},
            "**When to use:**",
            {"type": "list", "ordered": False, "items": ["primitives"]},
        ]
    ]
    assert Counter(" ".join(strings_of(parsed)).split()) == words_of_source(text)


def test_an_item_with_no_text_of_its_own_keeps_no_empty_part():
    assert blocks("- \n  - child\n")[0]["items"] == [
        [{"type": "list", "ordered": False, "items": ["child"]}]
    ]


def test_a_continuation_paragraph_under_a_nested_item_continues_that_item():
    parsed = blocks("- parent\n    - child\n\n      more about child\n")
    assert parsed[0]["items"] == [
        ["parent", {"type": "list", "ordered": False, "items": ["child more about child"]}]
    ]


def test_a_fence_under_a_nested_item_still_follows_the_whole_list():
    text = "1. Step\n   - sub\n\n     ```bash\n     make\n     ```\n2. Next\n"
    parsed = blocks(text)
    assert [block["type"] for block in parsed] == ["list", "code"]
    assert parsed[0]["items"] == [
        ["Step", {"type": "list", "ordered": False, "items": ["sub"]}],
        "Next",
    ]
    assert parsed[1]["text"] == "make"


def test_an_indented_marker_outside_any_list_is_still_not_a_list():
    # ⚠️ Four spaces at the top level is an indented code block, not a list, and
    # W258 widens the marker only inside a list.
    assert blocks("prose\n\n    - not an item\n")[1]["type"] != "list"


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


# --------------------------------------------------------------------------
# ⛔ W264: an ordered list keeps the number it starts at
# --------------------------------------------------------------------------

#: A document with lists that all start at one, nested included.
UNNUMBERED = (
    "Steps:\n\n1. one\n2. two\n\n```\ncode\n```\n\n- a\n  1. nested one\n  2. nested two\n- b\n"
)

#: ⛔ Its `content_sha256`, measured at `8f59ed9` before `W264` existed. A pin and
#: not a recomputation, so a reader that starts writing `start: 1` goes RED here.
UNNUMBERED_SHA256 = "baa69df8565b52a2968439bba753bad0e838a80ffd52ba48f10990fb9fffbc5a"


def test_a_list_that_starts_at_one_reads_byte_identical_to_before():
    assert content_sha256(parse(UNNUMBERED)) == UNNUMBERED_SHA256


@pytest.mark.parametrize("marker", [".", ")"])
def test_an_ordered_list_that_starts_past_one_keeps_its_number(marker):
    assert blocks(f"3{marker} three\n4{marker} four\n") == [
        {"type": "list", "ordered": True, "items": ["three", "four"], "start": 3}
    ]


def test_a_step_list_continued_after_a_code_block_keeps_its_number():
    made = blocks("1. one\n\n```\nx\n```\n\n2. two\n3. three\n")
    assert [block.get("start") for block in made] == [None, None, 2]
    assert made[2]["items"] == ["two", "three"]


def test_a_nested_ordered_list_keeps_its_number():
    nested = blocks("- a\n  5. five\n  6. six\n")[0]["items"][0][1]
    assert nested == {"type": "list", "ordered": True, "items": ["five", "six"], "start": 5}


def test_zero_is_a_number_an_author_can_start_at():
    assert blocks("0. zero\n")[0]["start"] == 0


def test_an_unordered_list_never_carries_a_start():
    assert "start" not in blocks("- a\n- b\n")[0]
