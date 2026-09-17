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
        "attachments": [],
    }
    return {**base, **overrides}


def attachment(local: str = "media/small-graph.ttl", **overrides) -> dict:
    """One declared companion file, as `unit.builder.parts` carries it."""
    return {
        "remote": None,
        "local": local,
        "sha256": "0" * 64,
        "bytes": 103,
        "content_type": "text/turtle",
        "kind": "dataset",
        **overrides,
    }


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


# --------------------------------------------------------------------------
# ⭐ `W215` / spec C4 — the files the page LINKS rather than shows
# --------------------------------------------------------------------------


def test_a_declared_attachment_is_linked_for_download():
    # ⛔ Spec C4: "the page links them for download rather than rendering them".
    markup = render(headed(attachments=[attachment()]))
    assert '<a href="attachments/small-graph.ttl" download>small-graph.ttl</a>' in markup


def test_a_unit_with_no_attachments_emits_no_region_at_all():
    # ⛔ A heading over an empty list reads as "the files are missing", where a
    # unit with no companion files simply has none.
    markup = render(headed())
    assert "attachments" not in markup
    assert "<h2>Files</h2>" not in markup


def test_the_link_is_relative_to_the_page_and_carries_no_archive_directory():
    # ⛔ R8: the page works over `file://` with no server, and `media/` is a fact
    # about the archive that placement never reproduces.
    markup = render(headed(attachments=[attachment("media/nested/data.ttl")]))
    assert 'href="attachments/data.ttl"' in markup
    assert "media/" not in markup
    assert "/" not in markup.split('href="attachments/', 1)[1].split('"', 1)[0]


def test_the_links_sit_after_the_material_and_outside_the_section():
    # ⭐ A reader takes a file away once they know what it is for, so the region
    # follows the prose — and staying outside `<section>` keeps it out of the
    # outline, exactly as the deck does above it.
    markup = render(headed(attachments=[attachment()]))
    assert markup.index("</section>") < markup.index("<h2>Files</h2>")


def test_every_declared_attachment_gets_its_own_link_in_the_order_declared():
    markup = render(headed(attachments=[attachment("media/a.ttl"), attachment("media/b.ttl")]))
    assert markup.index("a.ttl") < markup.index("b.ttl")
    assert markup.count("<li>") == 2


def test_provenance_never_reaches_an_attachment_link():
    # ⛔ `remote` is the address the source served; a page that rendered one
    # would reach off this machine on open (R8).
    markup = render(headed(attachments=[attachment(remote="https://example.invalid/small.ttl")]))
    assert "example.invalid" not in markup


def test_an_attachment_naming_no_file_is_refused_rather_than_dropped():
    # ⛔ The gate every file reference on this page passes. A link to nothing,
    # emitted quietly, would leave a reader told about a dataset that never
    # appears — and the build refuses the same entry from its own side.
    for local in (None, "", "/absolute/data.ttl", "../outside.ttl"):
        with pytest.raises(PageError):
            render(headed(attachments=[attachment(local)]))


def test_a_declaration_that_is_not_a_list_of_entries_emits_no_region():
    assert "<h2>Files</h2>" not in render(headed(attachments="media/small-graph.ttl"))
    assert "<h2>Files</h2>" not in render(headed(attachments=["media/small-graph.ttl"]))


def test_an_attachments_filename_is_escaped():
    markup = render(headed(attachments=[attachment('media/a&b".ttl')]))
    assert "a&amp;b&quot;.ttl</a>" in markup
    assert 'href="attachments/a&amp;b&quot;.ttl"' in markup
