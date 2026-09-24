"""Mirror of `generate.media.references` (R12) — a reading of a document, and of no disk.

⛔ **A SPLIT AT A SEAM, and the seam is the source module's own entry point**
(R11). ⭐ The line taken is the one `generate.media` already
draws — *"`references(document)` when only what a page will reach for is
wanted"* — so what the PASS does to a disk stays in `test_media.py`, and what a
page will reach for, which opens no file at all, is here.

⚠️ **Nothing in this module touches a filesystem**, and that is the property
worth keeping separate: a document is built inline, `references` reads it, and
no corpus is copied and no output root is minted.
"""

from __future__ import annotations

from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.generate import Reference, references
from studyforge.generate.media import MEDIA_BLOCKS
from tests.studyforge.generate.corpora import FIGURE, image


def test_references_answers_from_the_document_and_touches_nothing(tmp_path):
    document = {
        "sections": [
            {
                "blocks": [image(FIGURE), {"type": "para", "text": "no file here"}],
                "video": {"src": "media/deck.mp4", "poster": "media/deck.png"},
            }
        ]
    }

    found = list(references(document))

    assert [(one.kind, one.source) for one in found] == [
        ("images", FIGURE),
        ("video", "media/deck.mp4"),
        ("video", "media/deck.png"),
    ]


def test_the_attachments_a_section_declares_are_among_what_the_page_reaches_for():
    """⛔ The page links them, so this pass copies them — and in reading order."""
    document = {
        "sections": [
            {
                "blocks": [image(FIGURE)],
                "attachments": [
                    {"local": "media/small-graph.ttl", "remote": None},
                    {"local": "media/notebook.ipynb", "remote": None},
                ],
            }
        ]
    }

    assert [(one.kind, one.source) for one in references(document)] == [
        ("images", FIGURE),
        ("attachments", "media/small-graph.ttl"),
        ("attachments", "media/notebook.ipynb"),
    ]


def test_an_attachment_declaration_that_is_not_a_list_of_entries_reaches_for_nothing():
    for declared in ("media/small-graph.ttl", ["media/small-graph.ttl"], None):
        assert list(references({"sections": [{"blocks": [], "attachments": declared}]})) == []


def test_a_section_that_is_not_an_object_is_skipped_rather_than_crashed_on():
    assert list(references({"sections": [None, {"blocks": [image(FIGURE)]}]})) == [
        Reference("images", FIGURE)
    ]


def test_every_block_type_the_vocabulary_gives_a_file_has_a_directory_to_go_in():
    """⭐ The clause that makes the derivation worth having, and it is forward-looking.

    ⛔ A twelfth block type carrying a `src` is a file a page will show, and
    `archive.blocks` is where one would arrive. This is red the day one does and
    no unit media directory holds it — which is a decision, not an oversight to
    be discovered by a reader meeting a broken image.

    ⚠️ **It does not distinguish the derivation from a hardcoded pair today**,
    because the two agree at this ref — a known surviving plant.
    """
    for name in MEDIA_BLOCKS:
        found = list(references({"sections": [{"blocks": [{"type": name, "src": FIGURE}]}]}))
        assert [one.source for one in found] == [FIGURE]
        assert found[0].kind in UNIT_MEDIA_DIRNAMES


def test_a_document_with_no_sections_reaches_for_nothing():
    assert list(references({})) == []
