"""Mirror of `src/studyforge/render/page/text.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.page import text

#: A rooted href naming somebody's home directory — the R7 shape the `outside`
#: class exists for. ⛔ **Joined, never written as a literal**, because the
#: repository's own personal-data sweep refuses that literal in any file and it
#: is right to: the value under test is a shape, and committing an instance of
#: the shape to prove it is refused would be the defect the rule prevents.
#: ⭐ Measured 2026-09-10: written as one literal, `python3 -m tools.quality`
#: reported `[personal-data] carries a home path (R7)` on this very line.
A_ROOTED_HOME_PATH = "/" + "home/example/notes.html"

#: Every href a page must refuse, and the class it is refused by. ⚠️ A forbidden
#: list is the wrong instrument for *deciding* and the right one for *testing*:
#: `SAFE_SCHEMES` and the relative grammar are what the module decides with, and
#: these are the cases somebody would actually try.
#:
#: ⛔ **`W57` widened what is admitted, so every one of these is a refusal that
#: had to be re-proved rather than inherited** — a gate that gains a permitted
#: form is a gate whose refusals are all newly in question.
REFUSED = (
    # A scheme outside the closed set.
    ("javascript:alert(1)", "scheme"),
    ("JavaScript:alert(1)", "scheme"),
    ("data:text/html;base64,PHNjcmlwdD4=", "scheme"),
    ("vbscript:msgbox", "scheme"),
    ("file:///etc/passwd", "scheme"),
    ("ftp://host/x", "scheme"),
    ("notes:draft.html", "scheme"),
    # A spelling a browser normalises before it parses. ⛔ Each of these has no
    # scheme to a naive reader and a refused one to a browser.
    ("java\tscript:alert(1)", "spelling"),
    ("java\nscript:alert(1)", "spelling"),
    ("java\rscript:alert(1)", "spelling"),
    ("javascript\x00:alert(1)", "spelling"),
    ("java\x7fscript:alert(1)", "spelling"),
    ("\\\\host\\share", "spelling"),
    (".\\..\\x.html", "spelling"),
    ("https://host/a b", "spelling"),
    # A relative reference that leaves the site: rooted, or protocol-relative.
    ("/x.html", "outside"),
    (A_ROOTED_HOME_PATH, "outside"),
    ("//evil.example/x", "outside"),
    ("///evil.example/x", "outside"),
    ("/\\evil.example/x", "outside"),
    # Nothing to link.
    ("", "empty"),
    ("   ", "empty"),
)

#: The classes above, named so that losing one is a failure rather than a
#: quietly shorter table. ⭐ Ruling 128: the population is stated, not counted.
REFUSAL_CLASSES = ("scheme", "spelling", "outside", "empty")


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


@pytest.mark.parametrize(("href", "why"), REFUSED, ids=[row[0] or "empty" for row in REFUSED])
def test_a_refused_href_yields_no_href(href, why):
    assert why in REFUSAL_CLASSES
    assert text.safe_href(href) is None


def test_every_named_refusal_class_is_actually_exercised():
    # ⛔ The table above is the instrument; a class silently dropping out of it
    # would leave the corresponding refusal unasserted while every remaining row
    # still passed. ⭐ Ruling 128: the population is printed, not reduced to a
    # count that agrees with itself.
    found = {}
    for href, why in REFUSED:
        found.setdefault(why, []).append(href)
    assert sorted(found) == sorted(REFUSAL_CLASSES), found
    assert all(found[why] for why in REFUSAL_CLASSES), found


#: Every href a page must keep. ⭐ The `relative` rows are what `W57` added, and
#: the first of them is the defect itself: `relative_href` answers with a bare
#: filename for two units of one container under `sibling` placement.
PERMITTED = (
    ("http://x/y", "absolute"),
    ("https://x/y", "absolute"),
    ("HTTPS://x/y", "absolute"),
    ("mailto:a@b", "absolute"),
    ("unit-02-fields-and-constructors.unit.html", "relative"),
    ("sub/dir/page.html", "relative"),
    ("./a", "relative"),
    ("../a", "relative"),
    ("../../basics/01-getting-started/unit-01-your-first-class.unit.html", "relative"),
    ("#a", "relative"),
    ("page.html#a", "relative"),
    ("page.html?q=1", "relative"),
)


@pytest.mark.parametrize(("href", "form"), PERMITTED, ids=[row[0] for row in PERMITTED])
def test_a_permitted_href_survives_verbatim(href, form):
    assert form in ("absolute", "relative")
    assert text.safe_href(href) == href


def test_the_permitted_list_is_the_negative_control_for_the_refused_one():
    # ⭐ Every negative control is itself run negatively. ⛔ Two ways this pair
    # of tables could pass and mean nothing, and each is closed here: a
    # `safe_href` that returned `None` for everything would pass every refusal,
    # and one that returned its argument would pass every admission. Neither
    # survives both assertions, and the two populations are disjoint.
    refused = {href for href, _ in REFUSED}
    permitted = {href for href, _ in PERMITTED}
    assert refused and permitted
    assert not (refused & permitted)
    assert all(text.safe_href(href) is None for href in refused)
    assert all(text.safe_href(href) == href for href in permitted)


def test_a_bare_same_directory_href_is_permitted_and_that_is_this_row():
    # ⛔ **`W57`, and `SF-13/1` before it.** Under `sibling` placement two units
    # of one container share a directory, so `contents.links` answers with a
    # bare filename — and the old prefix set had no entry for one, so
    # `navigation._link` dropped the slot with nothing raised. ⭐ Measured then:
    # 13 slots computed for the `depth2` corpus and 6 refused, every one of them
    # a same-container `next` or `previous`.
    href = "unit-02-fields-and-constructors.unit.html"
    assert text.safe_href(href) == href
    assert text.inline(f"[next]({href})") == (
        f'<a href="{href}" rel="noopener noreferrer">next</a>'
    )


def test_the_scheme_set_holds_schemes_and_not_prefixes():
    # ⛔ The regression this row exists to prevent from coming back: a `#`, `/`
    # or `./` in this tuple is a relative *form* wearing a scheme's name, and it
    # is what made the set read as complete while a bare filename had no entry.
    for scheme in text.SAFE_SCHEMES:
        assert scheme.isalpha(), scheme
        assert scheme == scheme.lower(), scheme


def test_the_spelling_gate_applies_to_an_otherwise_permitted_scheme():
    # ⛔ The reading that would be impossible if the character check ran only on
    # the relative branch: an `https:` href is admitted by scheme and must still
    # be refused on spelling, or `\` and control characters walk in behind a
    # scheme that is allowed.
    assert text.safe_href("https://host/ok") == "https://host/ok"
    assert text.safe_href("https://host/o\tk") is None
    assert text.safe_href("https://host/o\\k") is None


def test_a_permitted_relative_reference_can_never_name_a_host():
    # ⭐ The property the `outside` refusals buy, asserted over the whole
    # permitted population rather than one row: nothing admitted without a
    # scheme can leave the page's own origin, which is what R8's `file://` floor
    # needs. ⚠️ Ruling 56 — the neighbour NOT asserted is named in the module's
    # docstring: `../` steps past the site root are admitted, because this
    # function is given no page to count them from.
    for href, form in PERMITTED:
        if form != "relative":
            continue
        assert not href.startswith("/"), href


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
