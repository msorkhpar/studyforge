"""Mirror of `src/studyforge/render/page/blocks/figure.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.markdown import parse
from studyforge.render.page.blocks import figure
from studyforge.render.page.errors import PageError
from studyforge.render.pageassets import PLAIN, SURFACE_HOOKS, highlighted_languages
from tests.studyforge.render.page.pages import sample_placement

#: The class a caption carries when its language fell back.
FALLBACK_CLASS = SURFACE_HOOKS["code_fallback"]


def render(block: dict) -> str:
    """One figure, placed the way the dispatcher places it."""
    return figure.render(block, 0, placement=sample_placement(), section="shared")


def test_the_declared_types_are_exactly_the_branches():
    assert sorted(figure.RENDERS) == sorted(figure._RENDERERS)


def test_a_code_block_escapes_its_text():
    markup = render({"type": "code", "lang": "java", "text": '"a" < b & c'})
    assert "&quot;a&quot; &lt; b &amp; c" in markup
    assert "<pre><code" in markup


def test_a_code_block_carries_the_library_class_the_highlighter_reads():
    markup = render({"type": "code", "lang": "Java", "text": "x"})
    assert 'class="language-java"' in markup


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_a_code_block_with_no_language_carries_no_class_and_a_plain_caption(empty):
    # ⛔ Spec §8.4 (`Q7`): a fence with no info string renders as plain text and
    # the renderer never guesses. Every empty spelling, because the reader
    # writes `""` for a bare fence and a guard written for `None` alone passes.
    markup = render({"type": "code", "lang": empty, "text": "x"})
    assert "language-" not in markup
    assert f'<span class="what">{figure.UNLABELLED_CODE}</span>' in markup
    assert FALLBACK_CLASS not in markup


def test_a_bare_fence_read_from_markdown_renders_with_no_language_guessed():
    # ⭐ Spec §8.4 (`Q7`), end to end: what the reader makes of a fence with no
    # info string is what the renderer receives, so the rule is held on the
    # pair and not on a block this test typed by hand.
    (block,) = parse("```\n<channel/>\n```\n")
    assert block["type"] == "code" and not block["lang"]
    markup = render(block)
    assert "language-" not in markup
    assert f'<span class="what">{figure.UNLABELLED_CODE}</span>' in markup


@pytest.mark.parametrize("language", sorted(highlighted_languages()))
def test_a_declared_language_asks_for_its_grammar_and_carries_no_fallback_note(language):
    markup = render({"type": "code", "lang": language, "text": "x"})
    assert f'class="language-{language}"' in markup
    assert FALLBACK_CLASS not in markup


def test_an_undeclared_language_renders_as_the_declared_plain_fallback_and_says_so():
    # ⛔ INT06-9. Never an error and never unmarked: the grammar asked for is the
    # declared `plain`, the caption keeps the archive's language, and the note
    # tells the reader this block is plain on purpose.
    language = "X-" + "-".join(sorted(highlighted_languages()))
    markup = render({"type": "code", "lang": language, "text": "Given a card"})
    assert f'class="language-{PLAIN}"' in markup
    assert f"language-{language.lower()}" not in markup
    assert f'<span class="what">{language}</span>' in markup
    assert f'<span class="{FALLBACK_CLASS}">{figure.FALLBACK_NOTE}</span>' in markup


def test_the_copy_button_is_not_rendered_into_the_page():
    # ⛔ `copy-code.js` creates it. A button in the markup would sit there doing
    # nothing with scripting off, and a control that does nothing is worse than
    # no control.
    markup = render({"type": "code", "lang": "java", "text": "x"})
    assert "<button" not in markup
    assert "<figcaption>" in markup


def test_an_image_addresses_the_placed_copy_and_not_the_archive_directory():
    markup = render({"type": "image", "src": "media/diagram.svg", "alt": "A", "width": 120})
    assert 'src="images/diagram.svg"' in markup
    assert "media/" not in markup


@pytest.mark.parametrize("width", [None, 0, -3, "wide", 1.5])
def test_an_unusable_width_emits_no_width_at_all(width):
    # ⛔ The archive saying it does not know; inventing a number would be worse
    # than letting the image size itself.
    markup = render({"type": "image", "src": "a.png", "alt": "A", "width": width})
    assert " width=" not in markup


def test_a_usable_width_is_emitted_so_the_page_does_not_reflow():
    markup = render({"type": "image", "src": "a.png", "alt": "A", "width": 800})
    assert ' width="800"' in markup


def test_an_image_with_no_alt_gets_no_caption():
    markup = render({"type": "image", "src": "a.png", "alt": "  ", "width": None})
    assert "<figcaption>" not in markup


def test_an_image_escapes_its_alt_in_both_places():
    markup = render({"type": "image", "src": "a.png", "alt": "<b>&", "width": None})
    assert 'alt="&lt;b&gt;&amp;"' in markup
    assert "<figcaption>&lt;b&gt;&amp;</figcaption>" in markup


def test_a_local_video_is_a_player_beside_the_page():
    markup = render({"type": "video", "src": "media/a.mp4", "title": "T"})
    assert 'src="video/a.mp4"' in markup
    assert 'preload="metadata"' in markup
    assert "<figcaption>T</figcaption>" in markup


def test_a_remote_video_is_a_link_and_never_an_iframe():
    # ⛔ R8: an iframe fetches the moment the page opens. A link is inert until
    # the reader clicks it — and the lesson is not dropped.
    markup = render({"type": "video", "src": "https://example.invalid/v", "title": ""})
    assert "<iframe" not in markup
    assert "<video" not in markup
    assert figure.REMOTE_VIDEO_LABEL in markup
    assert 'href="https://example.invalid/v"' in markup


def test_a_remote_video_uses_its_own_title_when_it_has_one():
    markup = render({"type": "video", "src": "https://example.invalid/v", "title": "Deck"})
    assert ">Deck<" in markup
    assert figure.REMOTE_VIDEO_LABEL not in markup


def test_a_figure_that_addresses_a_file_refuses_to_render_without_a_placement():
    with pytest.raises(PageError):
        figure.render({"type": "image", "src": "a.png"}, 0)


def test_a_media_path_that_escapes_the_corpus_is_refused_without_being_quoted():
    # ⛔ R7: every shape refused here is a candidate home directory, and this
    # runs over every media reference in a corpus, into a log.
    offending = "/absolute/elsewhere/material/a.png"
    with pytest.raises(PageError) as raised:
        render({"type": "image", "src": offending, "alt": "", "width": None})
    assert offending not in str(raised.value)


def test_a_media_block_naming_nothing_is_refused():
    with pytest.raises(PageError):
        render({"type": "image", "src": "", "alt": "", "width": None})
