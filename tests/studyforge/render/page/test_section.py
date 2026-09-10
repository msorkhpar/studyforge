"""Mirror of `src/studyforge/render/page/section.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.render.page import section as section_module
from studyforge.render.page.errors import PageError
from tests.studyforge.render.page.pages import sample_placement


def render(section: dict) -> str:
    """One section, placed."""
    return section_module.render(section, sample_placement())


def headed(**overrides) -> dict:
    """A section whose material carries its own heading."""
    base = {
        "key": "java",
        "kind": "lang",
        "heading": "Your first class",
        "blocks": [{"type": "heading", "level": 2, "text": "Your first class"}],
        "video": None,
        "workspace": None,
    }
    return {**base, **overrides}


def test_the_wrapper_carries_the_key_and_not_the_title():
    # ⛔ The key is structural; a retitled section must not detach the audio,
    # the progress record or the in-page links filed under it.
    markup = render(headed())
    assert 'id="s-java"' in markup
    assert 'data-section="java"' in markup
    assert 'data-kind="lang"' in markup
    assert 'data-label="Your first class"' in markup


def test_a_section_whose_material_has_a_heading_does_not_repeat_it():
    markup = render(headed())
    assert markup.count("Your first class") == 2  # data-label, and the block's own h2
    assert "<h2>Your first class</h2>" not in markup


def test_a_section_whose_material_has_no_heading_shows_the_one_it_recorded():
    # ⛔ Otherwise an authored `shared` section reaches the reader as an
    # unlabelled run of prose they cannot locate from the outline.
    markup = render(
        headed(
            key="shared",
            kind="shared",
            heading="Before you start",
            blocks=[{"type": "para", "text": "p"}],
        )
    )
    assert "<h2>Before you start</h2>" in markup


def test_the_test_is_structural_and_never_textual():
    # ⚠️ A heading at any level counts. Comparing the WORDS would put the
    # heading back the day an author changed one character.
    markup = render(headed(blocks=[{"type": "heading", "level": 4, "text": "Different"}]))
    assert "<h2>Your first class</h2>" not in markup


def test_a_section_with_no_heading_recorded_shows_none():
    markup = render(headed(heading="", blocks=[{"type": "para", "text": "p"}]))
    assert "<h2>" not in markup


def test_a_heading_is_escaped():
    markup = render(headed(heading="<b>&", blocks=[{"type": "para", "text": "p"}]))
    assert "<h2>&lt;b&gt;&amp;</h2>" in markup
    assert 'data-label="&lt;b&gt;&amp;"' in markup


def test_a_section_with_no_video_emits_no_deck():
    assert "<figure" not in render(headed())


def test_a_deck_sits_above_the_section_and_outside_it():
    # ⭐ It reads as an alternative to the section rather than as its first
    # block, and staying outside keeps it out of the outline.
    markup = render(headed(video={"src": "video/a.mp4", "poster": "video/a.jpg"}))
    assert markup.index("<figure") < markup.index("<section")
    assert 'poster="video/a.jpg"' in markup
    assert 'src="video/a.mp4"' in markup


def test_a_deck_with_no_poster_emits_no_poster_attribute():
    markup = render(headed(video={"src": "video/a.mp4", "poster": None}))
    assert "poster=" not in markup


def test_provenance_never_reaches_the_page():
    # ⛔ `remote` and `poster_remote` are the addresses the source served. A page
    # that rendered one would fetch from the network on open (R8).
    markup = render(
        headed(
            video={
                "src": "video/a.mp4",
                "poster": None,
                "mime": "video/mp4",
                "remote": "https://example.invalid/a.mp4",
                "poster_remote": "https://example.invalid/a.jpg",
            }
        )
    )
    assert "example.invalid" not in markup


def test_a_video_record_with_no_src_emits_nothing():
    assert "<figure" not in render(headed(video={"src": "  ", "poster": None}))


def test_a_section_that_is_not_an_object_is_refused():
    with pytest.raises(PageError):
        section_module.render("not a section", sample_placement())


def test_a_section_key_that_is_not_a_slug_is_refused():
    with pytest.raises(PageError):
        render(headed(key="Java"))
