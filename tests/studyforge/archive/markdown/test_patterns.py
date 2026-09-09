"""Mirror of `src/studyforge/archive/markdown/patterns.py` (R12).

Each of these pins a **width** that was corrected against material that broke.
⚠️ They are here rather than only in the reader's tests because the widths are
the part somebody tidies: a pattern with no test looks like it could be
simplified back to the version that lost a lesson.
"""

from __future__ import annotations

import re

import pytest

from studyforge.archive.markdown import patterns


def test_every_public_name_is_a_pattern_a_bound_or_a_tag_list():
    for name in dir(patterns):
        if name.isupper():
            value = getattr(patterns, name)
            assert isinstance(value, re.Pattern | int | str), name


@pytest.mark.parametrize("indent", ["", " ", "  ", "   "])
def test_a_fence_may_carry_up_to_three_spaces(indent):
    assert patterns.FENCE_OPEN.match(f"{indent}```py")


def test_four_spaces_is_an_indented_code_block_and_not_a_fence():
    assert not patterns.FENCE_OPEN.match("    ```py")
    # ⚠️ ...except inside a list item, which is the one place four spaces does
    # not mean "indented code block".
    assert patterns.INDENTED_FENCE.match("    ```py")


@pytest.mark.parametrize("indent", ["", " ", "  ", "   "])
def test_a_list_marker_may_carry_up_to_three_spaces(indent):
    assert patterns.UNORDERED.match(f"{indent}- item")
    assert patterns.ORDERED.match(f"{indent}1. item")


def test_both_ordered_markers_are_accepted():
    assert patterns.ORDERED.match("1. a")
    assert patterns.ORDERED.match("1) a")


@pytest.mark.parametrize("line", ["---", "***", "___", "- - -", "* * *", "  ___  "])
def test_a_thematic_break_in_its_several_spellings(line):
    assert patterns.THEMATIC.match(line)


@pytest.mark.parametrize("line", ["--", "a---", "| --- | --- |", "-*-"])
def test_what_is_not_a_thematic_break(line):
    # ⚠️ Three or more of the SAME character, spacing optional — so `-- -` is
    # a break (three dashes) and `-*-` is not (mixed).
    assert not patterns.THEMATIC.match(line)


def test_spacing_between_the_characters_does_not_stop_a_break():
    assert patterns.THEMATIC.match("-- -")


def test_the_disclosure_tags():
    assert patterns.DISCLOSURE_OPEN.match("<details>")
    assert patterns.DISCLOSURE_OPEN.match("<DETAILS open>")
    assert patterns.DISCLOSURE_CLOSE.match("</details>")
    assert not patterns.DISCLOSURE_OPEN.match("</details>")
    # ⛔ A `<details>` mid-sentence is prose, not a disclosure.
    assert not patterns.DISCLOSURE_OPEN.match("use <details> for this")


def test_the_html_rule_names_commonmarks_block_tags():
    for markup in ("<div>", "</div>", '<p class="x">', "<figure>", "<!-- note -->", "<TABLE>"):
        assert patterns.HTML_OPEN.match(markup), markup


def test_an_unknown_tag_is_not_an_html_block():
    # ⛔ CommonMark's type 7 would open a block for any tag alone on a line;
    # this reader deliberately does not. An `html` block is a statement about
    # structure, not a catch-all for anything angle-shaped — and a paragraph
    # that merely opens with something tag-shaped keeps its inline emphasis,
    # which an `html` block would render verbatim and lose.
    for prose in ("<marquee>hello</marquee>", "<not-a-known-tag> as it was", "<x-widget>"):
        assert not patterns.HTML_OPEN.match(prose), prose


def test_the_html_rule_is_narrow_enough_to_leave_arithmetic_alone():
    # ⛔ A pattern loose enough to catch a bare `<` turns `a < b` into markup.
    for prose in ("<", "a < b", "5 <6", "< div>"):
        assert not patterns.HTML_OPEN.match(prose), prose


def test_the_media_embed_names_its_tags_and_leaves_img_alone():
    # ⭐ `<img>` is deliberately absent: it has a block type of its own and its
    # file is archived beside the page.
    assert patterns.MEDIA_EMBED.match("<video>")
    assert patterns.MEDIA_EMBED.match('<iframe src="v"></iframe>')
    assert not patterns.MEDIA_EMBED.match('<img src="p.png">')


def test_an_unescaped_pipe_is_the_only_thing_that_ends_a_cell():
    assert patterns.UNESCAPED_PIPE.search("a | b")
    assert not patterns.UNESCAPED_PIPE.search("a \\| b")


def test_the_image_span_limit_is_a_bound_not_a_style():
    # A bound, so an unclosed `![` cannot swallow the rest of the document.
    assert isinstance(patterns.IMAGE_SPAN_LIMIT, int)
    assert 0 < patterns.IMAGE_SPAN_LIMIT < 100
