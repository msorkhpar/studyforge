"""Mirror of `src/studyforge/archive/markdown/scan.py` (R12).

⛔ The ORDER of `block_kind`'s tests is the contract, and most of this module
asserts that order rather than the individual patterns.
"""

from __future__ import annotations

import pytest

from studyforge.archive.markdown.scan import (
    block_kind,
    cells,
    dedent,
    fence_parts,
    image_span,
    indent_of,
    is_separator_row,
)


def kind(*lines: str) -> str | None:
    """The construct `block_kind` sees opening at the first of `lines`."""
    return block_kind(list(lines), 0)


# --- the order, which is the contract ---------------------------------------


def test_a_fence_is_tested_first_so_nothing_inside_one_is_classified():
    # ⛔ THE constraint. A reader that scanned for `<` would read a quoted
    # `<details>` as a disclosure and a quoted `<div>` as markup. It passes
    # every other case without this and fails here, silently.
    assert kind("```html", "<details>", "</details>", "```") == "code"
    assert kind("```xml", "<project>", "</project>", "```") == "code"


def test_a_thematic_break_is_tested_before_a_list():
    # `- - -` is both, and CommonMark gives the break priority.
    assert kind("- - -") == "rule"
    assert kind("- an item") == "list"


def test_the_named_tags_reach_their_own_readers_before_the_general_html_rule():
    assert kind('<img src="a.png">') == "image"
    assert kind('<iframe src="v.mp4"></iframe>') == "video"
    assert kind("<video>") == "media-embed"
    assert kind("<details>") == "disclosure"
    assert kind("<details open>") == "disclosure"
    assert kind("<div class='callout'>") == "html"
    assert kind("<summary>orphan</summary>") == "html"


def test_prose_is_last_and_unclassifiable_lines_return_none():
    assert kind("just some prose") is None
    assert kind("a < b and c > d") is None
    assert kind("<") is None


@pytest.mark.parametrize(
    "line,expected",
    [
        ("# h", "heading"),
        ("###### h", "heading"),
        ("####### not a heading", None),
        ("```", "code"),
        ("   ```py", "code"),
        ("    ```py", None),
        ("> quoted", "quote"),
        ("1. item", "list"),
        ("1) item", "list"),
        ("![a](b)", "image"),
        ("***", "rule"),
    ],
)
def test_the_classification_of_one_line(line, expected):
    assert kind(line) == expected


def test_a_table_needs_the_separator_on_the_next_line():
    assert block_kind(["a | b", "--- | ---"], 0) == "table"
    assert block_kind(["a | b", "not a separator"], 0) is None
    assert block_kind(["a | b"], 0) is None


# --- the line arithmetic ----------------------------------------------------


def test_indent_of():
    assert indent_of("no indent") == 0
    assert indent_of("    four") == 4
    assert indent_of("\ttab is not a space") == 0


def test_dedent_never_removes_content():
    assert dedent("    x = 1", 4) == "x = 1"
    assert dedent("  x = 1", 4) == "x = 1"  # fewer spaces than asked for
    assert dedent("x = 1", 4) == "x = 1"


def test_fence_parts():
    assert fence_parts("   ```python") == ("```", "python")
    assert fence_parts("````") == ("````", "")


def test_cells_strips_the_outer_pipes_and_unescapes():
    assert cells("| a | b |") == ["a", "b"]
    assert cells("a | b") == ["a", "b"]
    assert cells("| x \\| y |") == ["x | y"]


def test_is_separator_row():
    assert is_separator_row("| --- | --- |")
    assert is_separator_row("--- | ---")
    assert is_separator_row("| :--- | ---: |")
    assert not is_separator_row("---")  # no pipe: a thematic break, not a table
    assert not is_separator_row("| a | b |")


def test_image_span_is_bounded_and_blank_line_terminated():
    assert image_span(["![alt](src)"], 0) is None  # already complete on one line
    assert image_span(["![a", "wraps](src)", "after"], 0) == ("![a\nwraps](src)", 2)
    assert image_span(["![never", "", "closed](src)"], 0) is None
    assert image_span(["![a"] + ["more"] * 20 + ["](src)"], 0) is None
