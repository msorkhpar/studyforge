"""Mirror of `src/studyforge/archive/markdown/leaf.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import MarkdownError, parse
from studyforge.archive.markdown.leaf import read_html, read_rule


def blocks(text: str, **kwargs) -> list[dict]:
    """Parse `text` and return its blocks."""
    return parse(text, **kwargs)


# --- heading and paragraph --------------------------------------------------


def test_heading():
    assert blocks("### Three\n") == [{"type": "heading", "level": 3, "text": "Three"}]


def test_paragraph_keeps_bold_and_inline_code():
    # ⛔ Emphasis, inline code and links are left untouched inside `text`.
    # Stripping them here is exactly the loss this reader exists to prevent.
    text = "A **bold** word and `code` and [a link](http://example.invalid)."
    assert blocks(text + "\n") == [{"type": "para", "text": text}]


def test_a_paragraph_joins_its_lines_with_single_spaces():
    assert blocks("one\ntwo\nthree\n") == [{"type": "para", "text": "one two three"}]


@pytest.mark.parametrize(
    "following",
    ["```py\nx = 1\n```", "## a heading", "- an item", "| a | b |\n| --- | --- |", "![alt](src)"],
)
def test_a_paragraph_stops_before_a_construct_with_no_blank_line(following):
    # ⛔ A paragraph must never absorb a line the dispatcher would have
    # handled — which is how a fence with no blank line before it ends up as
    # prose with literal backticks in it.
    parsed = blocks("prose\n" + following + "\n")
    assert parsed[0] == {"type": "para", "text": "prose"}
    assert len(parsed) >= 2


def test_a_line_matching_nothing_still_falls_into_the_paragraph():
    # ⭐ The catch-all is deliberate: only a *classifiable* line must not be
    # swallowed.
    assert blocks("2 + 2 = 4 and a < b\n") == [{"type": "para", "text": "2 + 2 = 4 and a < b"}]


# --- code -------------------------------------------------------------------


def test_fenced_code_keeps_its_language_and_indentation():
    assert blocks("```python\ndef f():\n    return 1\n```\n") == [
        {"type": "code", "lang": "python", "text": "def f():\n    return 1"}
    ]


def test_a_text_fence_is_not_relabelled():
    assert blocks("```text\nplain\n```\n", lang_default="java")[0]["lang"] == "text"


def test_a_bare_fence_falls_back_to_the_declared_language():
    assert blocks("```\nplain\n```\n", lang_default="java")[0]["lang"] == "java"


def test_a_fence_indented_up_to_three_spaces_is_still_a_fence():
    # ⛔ CommonMark's rule. Anchored at column 0, a one-space opener is
    # invisible — which makes the CLOSING fence an opener and refuses the
    # document naming the wrong line.
    assert blocks("   ```py\n   x = 1\n   ```\n") == [
        {"type": "code", "lang": "py", "text": "x = 1"}
    ]


def test_the_openers_indent_is_stripped_from_the_code():
    assert blocks("  ```py\n  x = 1\n    y = 2\n  ```\n")[0]["text"] == "x = 1\n  y = 2"


def test_an_indented_closing_fence_does_not_close_early():
    # ⛔ A closing fence may carry at most three spaces MORE than the opener.
    # Asking only "is this line all backticks" lets an indented ``` inside the
    # code end the block early, and everything after re-parses as alternating
    # prose and code.
    parsed = blocks("```text\nquoted transcript\n    ```json\n    {}\n    ```\nstill text\n```\n")
    assert len(parsed) == 1
    assert "still text" in parsed[0]["text"]


def test_a_fence_that_never_closes_raises():
    with pytest.raises(MarkdownError) as raised:
        blocks("```py\nx = 1\n")
    assert "never closed" in str(raised.value)
    assert "line 1" in str(raised.value)


# --- image ------------------------------------------------------------------


def test_markdown_image_becomes_an_image_block():
    assert blocks("![the alt](pic.png)\n") == [
        {"type": "image", "src": "pic.png", "alt": "the alt", "width": None}
    ]


def test_html_img_tag_becomes_an_image_block():
    assert blocks('<img src="pic.png" alt="the alt" width="120">\n') == [
        {"type": "image", "src": "pic.png", "alt": "the alt", "width": 120}
    ]


def test_single_quoted_img_attributes_parse():
    assert blocks("<img src='pic.png' alt='a'>\n")[0]["src"] == "pic.png"


def test_a_percentage_width_is_dropped_rather_than_crashing_the_document():
    # ⭐ The contract is `int | None`, and authors write `width="90%"`.
    # `int("90%")` raises a bare ValueError and costs the whole document.
    assert blocks('<img src="p.png" width="90%">\n')[0]["width"] is None


def test_an_img_tag_with_no_src_raises():
    # ⛔ A figure that silently renders as a broken icon is exactly the kind of
    # loss this reader exists to refuse.
    with pytest.raises(MarkdownError) as raised:
        blocks('<img alt="no source">\n')
    assert "no src" in str(raised.value)


def test_an_images_alt_text_may_wrap():
    parsed = blocks("![a long alt\nthat wraps](pic.png)\n")
    assert parsed == [
        {"type": "image", "src": "pic.png", "alt": "a long alt that wraps", "width": None}
    ]


def test_an_unclosed_image_span_stays_prose():
    # Bounded and blank-line terminated: an `![` that never closes must not
    # absorb the rest of the document.
    assert blocks("![never closed\n\nafter\n")[0]["type"] == "para"


# --- video ------------------------------------------------------------------


def test_an_iframe_with_a_src_becomes_a_video_block():
    line = '<iframe src="https://example.invalid/v?a=1&amp;b=2" title="Watch it"></iframe>'
    # ⛔ UNESCAPED: left alone the query string is escaped again into the href
    # and the reader clicks through to the wrong URL.
    assert blocks(line + "\n") == [
        {"type": "video", "src": "https://example.invalid/v?a=1&b=2", "title": "Watch it"}
    ]


def test_the_closing_wrapper_of_an_embed_carries_no_block():
    # ⚠️ Not a silent drop: the `src` is the content and it has been kept by
    # the opening tag's own block.
    parsed = blocks('<video>\n<source src="clip.mp4">\n</video>\n')
    assert [block["type"] for block in parsed] == ["video"]
    assert parsed[0]["src"] == "clip.mp4"


# --- rule -------------------------------------------------------------------


@pytest.mark.parametrize("break_line", ["---", "***", "___", "- - -", "  ***  "])
def test_a_thematic_break_is_a_block(break_line):
    # ⚠️ The extraction source emits NOTHING here, to agree with its DOM
    # reader. studyforge has none to agree with, and a break is a real division
    # the author wrote — 10 of one surveyed corpus's 166 lessons use one.
    assert blocks(f"a\n\n{break_line}\n\nb\n")[1] == {"type": "rule"}
    assert read_rule() == {"type": "rule"}


def test_a_break_wins_over_a_list_item_that_looks_like_one():
    # `- - -` is both; CommonMark gives the break priority.
    assert blocks("- - -\n") == [{"type": "rule"}]


def test_a_setext_underline_is_not_a_break_when_it_carries_pipes():
    parsed = blocks("| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    assert [block["type"] for block in parsed] == ["table"]


# --- html -------------------------------------------------------------------


def test_raw_block_level_html_is_kept_verbatim():
    # ⭐ A lesson teaching HTML must keep its HTML: stored verbatim, rendered
    # as-is, never parsed.
    text = '<div class="callout">\n<p>Kept exactly.</p>\n</div>\n'
    assert blocks(text) == [{"type": "html", "text": text.rstrip("\n")}]


def test_an_html_run_ends_at_a_blank_line():
    parsed = blocks("<div>\n<p>x</p>\n</div>\n\nprose after\n")
    assert [block["type"] for block in parsed] == ["html", "para"]
    assert parsed[1]["text"] == "prose after"


def test_a_lone_angle_bracket_line_is_still_prose():
    # ⛔ Narrow on purpose: a pattern loose enough to catch a bare `<` turns
    # arithmetic into markup.
    assert blocks("<\n")[0]["type"] == "para"
    assert blocks("5 < 6 < 7\n")[0]["type"] == "para"


def test_an_unknown_tag_on_its_own_line_is_still_prose():
    # ⭐ `html` is CommonMark's block-tag list, not any tag. An unknown tag
    # stays prose — which is what the extraction source does too, and one of
    # the few places the two agree about markup.
    assert blocks("<marquee>hello</marquee>\n")[0]["type"] == "para"
    assert blocks("<not-a-known-tag> stays as it was\n")[0]["type"] == "para"


def test_an_html_comment_opens_a_raw_block():
    assert blocks("<!-- a note -->\n") == [{"type": "html", "text": "<!-- a note -->"}]


def test_read_html_reports_where_it_stopped():
    lines = ["<div>", "</div>", "", "after"]
    block, index = read_html(lines, 0)
    assert block == {"type": "html", "text": "<div>\n</div>"}
    assert index == 2


def test_a_summary_outside_a_disclosure_is_raw_html_not_prose():
    # ⚠️ A divergence from the extraction source, which makes it a paragraph.
    # It is markup; `html` is where genuinely unstructured markup survives.
    assert blocks("<summary>orphaned</summary>\n")[0]["type"] == "html"
