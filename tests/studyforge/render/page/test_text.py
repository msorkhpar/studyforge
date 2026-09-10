"""Mirror of `src/studyforge/render/page/text.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.page import text

#: Every scheme a page must refuse. ⚠️ A forbidden list is the wrong instrument
#: for deciding, and the right one for *testing*: `SAFE_SCHEMES` is what the
#: module decides with, and these are the cases somebody would actually try.
REFUSED = (
    "javascript:alert(1)",
    "JavaScript:alert(1)",
    "data:text/html;base64,PHNjcmlwdD4=",
    "vbscript:msgbox",
    "example.com/x",
    "",
    "   ",
)


def test_ampersand_is_escaped_first():
    # ⛔ Any other order double-escapes and the page shows `&amp;lt;`.
    assert text.escape("a & b < c") == "a &amp; b &lt; c"
    assert text.escape("&lt;") == "&amp;lt;"


def test_every_dangerous_character_in_text_is_escaped():
    assert text.escape('<&">') == "&lt;&amp;&quot;&gt;"


def test_none_escapes_to_nothing_rather_than_to_the_word():
    assert text.escape(None) == ""


def test_an_attribute_also_neutralises_the_apostrophe():
    assert text.escape_attribute("it's <b>") == "it&#39;s &lt;b&gt;"


def test_text_content_keeps_its_apostrophe():
    # ⭐ The other direction: escaping an apostrophe in prose would be visible
    # noise on every possessive in the corpus.
    assert text.escape("it's") == "it's"


@pytest.mark.parametrize("href", REFUSED)
def test_a_refused_scheme_yields_no_href(href):
    assert text.safe_href(href) is None


PERMITTED = ("http://x/y", "https://x/y", "mailto:a@b", "#a", "/a", "./a", "../a")


@pytest.mark.parametrize("href", PERMITTED)
def test_a_permitted_scheme_survives_verbatim(href):
    assert text.safe_href(href) == href


def test_a_permitted_scheme_is_the_negative_control_for_the_refused_list():
    # ⭐ Every negative control is itself run negatively: if `safe_href` returned
    # `None` for everything, the refusals above would pass and mean nothing.
    assert text.safe_href("https://example.invalid/x") is not None


def test_every_segment_kind_is_reachable_and_declared():
    found = {kind for kind, _, _ in text.segments("a `c` [l](https://x) **s** _e_")}
    assert found == set(text.SEGMENT_KINDS)


def test_the_renderer_has_a_branch_for_every_segment_kind():
    # ⛔ A parser that gains a marker and a renderer that does not is exactly how
    # markup reaches the page as text. Each kind must render as something other
    # than its own escaped body, except plain text, which is the escaped body.
    rendered = text.inline("`c` [l](https://x) **s** _e_ plain")
    for element in ("<code>", "<a href=", "<strong>", "<em>"):
        assert element in rendered
    assert "plain" in rendered


def test_every_branch_escapes_its_body():
    assert text.inline("`<b>`") == "<code>&lt;b&gt;</code>"
    assert text.inline("**<b>**") == "<strong>&lt;b&gt;</strong>"
    assert text.inline("_<b>_") == "<em>&lt;b&gt;</em>"
    assert text.inline("[<b>](https://x)") == (
        '<a href="https://x" rel="noopener noreferrer">&lt;b&gt;</a>'
    )


def test_prose_that_is_tag_shaped_is_escaped_rather_than_emitted():
    # ⛔ The clause `SF-12` exists to keep, at the lowest level it is decided.
    assert text.inline("<blink>hello</blink>") == "&lt;blink&gt;hello&lt;/blink&gt;"


def test_a_link_with_a_refused_scheme_keeps_its_words_and_loses_its_link():
    assert text.inline("[click](javascript:alert)") == "click"
    assert text.inline("[click](data:text/html,x)") == "click"


def test_a_marker_inside_inline_code_is_not_read_as_a_marker():
    # ⚠️ Code first in the alternation: a backtick span may contain any of the
    # others, and none of them may be read inside it.
    assert text.inline("`**not bold**`") == "<code>**not bold**</code>"


def test_a_non_string_renders_as_nothing_rather_than_as_its_repr():
    assert text.inline(None) == ""
    assert text.segments(None) == ()


def test_an_underscore_inside_a_word_is_not_emphasis():
    # ⚠️ `snake_case_name` is an identifier, not italics, and the corpus is full
    # of them.
    assert text.inline("snake_case_name") == "snake_case_name"
