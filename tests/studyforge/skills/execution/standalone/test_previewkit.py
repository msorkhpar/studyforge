"""Mirror of `src/studyforge/skills/execution/standalone/previewkit.py` (R12).

⭐ Each edit is read off the text it returns for a page written here in the shape of a built one;
the tree-wide clauses (every link resolves, no dot directory) are `test_preview.py`'s.
"""

from __future__ import annotations

import re

import pytest

from studyforge.skills.execution.standalone import previewkit

PAGE = (
    "<!doctype html><html><head><title>T</title></head><body>"
    '<a href="#content">Skip to the content</a><header><h1 data-audio="a.mp3">T</h1></header>'
    '<main id="content"><p data-audio="b.mp3">Text</p></main>'
    '<footer id="player" hidden><button id="play">Play narration</button></footer>'
    '<audio id="narrator" preload="none"></audio>'
    '<script src="page.js" defer></script></body></html>'
)


def test_every_reference_to_narration_is_removed_and_one_note_stands_in_its_place():
    text, narrated = previewkit.remove_server_parts(PAGE)
    assert narrated is True
    for gone in ("data-audio", 'id="player"', 'id="narrator"', "Play narration"):
        assert gone not in text
    assert text.count('data-preview-note="narration"') == 1
    assert text.index("</header>") < text.index("data-preview-note")


def test_a_page_with_no_narration_is_not_given_the_note():
    text, narrated = previewkit.remove_server_parts("<html><body><p>x</p></body></html>")
    assert narrated is False and "data-preview-note" not in text


def test_a_code_example_without_its_summary_or_files_is_refused():
    with pytest.raises(previewkit.PageRefused, match="summary"):
        previewkit.remove_server_parts("<details data-code-example><p>x</p></details>")


def test_a_source_link_loses_its_href_and_keeps_its_path_for_the_script():
    example = (
        "<details data-code-example><summary>A</summary>"
        '<ul class="items"><li><a href="../../A.java" rel="noopener" data-code-path="a/A.java">A'
        "</a></li></ul></details>"
    )
    text, _ = previewkit.remove_server_parts(example)
    assert 'data-code-path="a/A.java"' in text and 'A.java"' in text
    assert "href=" not in text


def test_the_banner_the_style_and_the_script_are_added_once_and_in_their_places():
    done = previewkit.finish(PAGE, assets="../course")
    assert done.count("data-preview-banner") == 1
    assert done.index("Skip to the content") < done.index("data-preview-banner")
    assert done.index("data-preview-banner") < done.index("<header>")
    assert '<link rel="stylesheet" href="../course/preview.css">' in done
    assert done.index("preview.js") > done.index("page.js")
    assert 'rel="icon" href="data:,"' in done


def test_a_page_that_already_has_an_icon_keeps_it_and_gains_none():
    page = PAGE.replace("<title>", '<link rel="icon" href="x.ico"><title>')
    assert previewkit.finish(page, assets=".").count('rel="icon"') == 1


def test_a_page_without_a_head_or_a_body_is_refused():
    with pytest.raises(previewkit.PageRefused, match="head and a body"):
        previewkit.finish("<p>x</p>", assets=".")


def test_the_script_holds_no_owner_repository_or_host_and_builds_from_location():
    js = previewkit.PREVIEW_JS
    assert "window.location.hostname" in js and "window.location.pathname" in js
    assert not re.search(r"github\.(com|io)/[A-Za-z0-9]", js)
    assert previewkit.RUN_ANCHOR in js
    for note in (previewkit.PRACTICE_NOTE, previewkit.EXAMPLE_NOTE, previewkit.NARRATION_NOTE):
        assert "locally with Docker" in note
        assert previewkit.RUN_LINK in note
