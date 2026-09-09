"""Mirror of `src/studyforge/archive/markdown/table.py` (R12)."""

from __future__ import annotations

from studyforge.archive.markdown import parse
from studyforge.archive.markdown.table import read_table


def blocks(text: str) -> list[dict]:
    """Parse `text` and return its blocks."""
    return parse(text)


def test_table():
    assert blocks("| a | b |\n| --- | --- |\n| 1 | 2 |\n") == [
        {"type": "table", "headers": ["a", "b"], "rows": [["1", "2"]]}
    ]


def test_a_table_without_outer_pipes_is_still_a_table():
    # ⛔ GFM makes the outer pipes optional and authors omit both. Requiring
    # the leading pipe turns every borderless comparison table into a
    # paragraph — silently, because prose is the catch-all.
    assert blocks("**Bad** | **Good**\n--- | ---\nx | y\n") == [
        {"type": "table", "headers": ["**Bad**", "**Good**"], "rows": [["x", "y"]]}
    ]


def test_a_borderless_table_ends_the_paragraph_above_it():
    parsed = blocks("prose about it\nBad | Good\n--- | ---\nx | y\n")
    assert [block["type"] for block in parsed] == ["para", "table"]


def test_a_setext_underline_is_not_a_borderless_table_separator():
    # ⛔ Requiring an unescaped pipe in the SEPARATOR row is what stops any
    # paragraph line holding a `|` followed by `---` from opening a table.
    parsed = blocks("a | b in prose\n---\n")
    assert [block["type"] for block in parsed] == ["para", "rule"]


def test_a_table_cell_may_contain_an_escaped_pipe():
    # Splitting on every `|` turns one such cell into two, which is the silent
    # loss this reader exists to refuse.
    parsed = blocks("| a | b |\n| --- | --- |\n| x \\| y | z |\n")
    assert parsed[0]["rows"] == [["x | y", "z"]]


def test_an_all_blank_header_row_is_a_table_with_no_headers():
    # ⭐ GFM has no other way to write a headerless table, and keeping the
    # blanks makes a narrator read every cell as "«nothing»: value".
    parsed = blocks("|  |  |\n| --- | --- |\n| 1 | 2 |\n")
    assert parsed[0]["headers"] == []
    assert parsed[0]["rows"] == [["1", "2"]]


def test_pipe_rows_with_no_separator_are_prose_and_are_never_dropped():
    parsed = blocks("a | b\nc | d\n")
    assert parsed == [{"type": "para", "text": "a | b c | d"}]


def test_a_line_with_no_pipe_ends_the_table():
    parsed = blocks("| a |\n| --- |\n| 1 |\nprose\n")
    assert [block["type"] for block in parsed] == ["table", "para"]


def test_read_table_reports_where_it_stopped():
    lines = ["| a |", "| --- |", "| 1 |", "prose"]
    block, index = read_table(lines, 0)
    assert block == {"type": "table", "headers": ["a"], "rows": [["1"]]}
    assert index == 3
