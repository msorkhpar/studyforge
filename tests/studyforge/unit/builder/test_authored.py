"""Mirror of `src/studyforge/unit/builder/authored.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit.builder import authored
from studyforge.unit.builder.material import of
from studyforge.unit.content import from_document
from studyforge.unit.errors import ContentError
from tests.studyforge.unit.builder import support


def overlay(sections, **kwargs):
    return from_document(support.overlay_document(sections, **kwargs), depth=1)


def material(documents=None):
    return of(documents or [support.lesson(1), support.practice(1)], "unit-01")


# --------------------------------------------------------------------------
# ⛔ the author's order, verbatim
# --------------------------------------------------------------------------


def test_the_authors_order_is_preserved_exactly():
    # ⛔ **The authored overlay's acceptance, and the seam's whole reason.** The practice is
    # written first here, which no derived build would ever produce.
    written = overlay(
        [
            support.authored_section("practice", lang="prose", heading="Try it"),
            support.authored_section("lang", lang="prose", heading="Read it"),
        ]
    )
    built = authored.sections(written, material())
    assert [s["key"] for s in built] == ["practice-prose", "prose"]
    assert [s["heading"] for s in built] == ["Try it", "Read it"]


def test_the_heading_is_the_authors_and_not_the_archives():
    # ⚠️ The one thing an author is *for*. The archive's title is `A lesson`.
    written = overlay([support.authored_section("lang", lang="prose", heading="Read it")])
    assert authored.sections(written, material())[0]["heading"] == "Read it"


def test_an_author_may_name_fewer_sections_than_there_are_documents():
    # ⭐ The overlay is judgement, not a manifest: leaving a document out is a
    # decision, and this build does not add it back.
    written = overlay([support.authored_section("lang", lang="prose")])
    built = authored.sections(written, material())
    assert len(built) == 1
    assert built[0]["key"] == "prose"


def test_a_shared_section_is_backed_by_the_units_first_lesson():
    # ⚠️ Stated rather than assumed: `shared` has no variant in its key, so it
    # cannot be matched by the derivation, and this is where it comes from.
    written = overlay([support.authored_section("shared", heading="For everyone")])
    built = authored.sections(written, material())
    assert built[0]["key"] == "shared"
    assert built[0]["blocks"]


# --------------------------------------------------------------------------
# ⛔ the two derived fields arrive here, and only from the archive
# --------------------------------------------------------------------------


def test_the_workspace_is_added_by_this_build_not_by_the_author():
    written = overlay([support.authored_section("practice", lang="prose")])
    documents = [support.lesson(1), support.practice(1, exercise=support.EXERCISE)]
    built = authored.sections(written, of(documents, "unit-01"))
    assert built[0]["workspace"] == support.EXERCISE


def test_the_video_is_carried_from_the_archive():
    written = overlay([support.authored_section("lang", lang="prose")])
    documents = [support.lesson(1, video=dict(support.VIDEO)), support.practice(1)]
    built = authored.sections(written, of(documents, "unit-01"))
    assert built[0]["video"] == support.VIDEO


def test_an_authored_section_with_no_material_behind_it_is_refused():
    # ⛔ It would render as an exercise with no workspace and no grader —
    # which is exactly the ungraded state, and therefore indistinguishable
    # from a corpus that meant it.
    written = overlay([support.authored_section("practice", lang="prose")])
    with pytest.raises(ContentError, match="no ingested document stands behind it"):
        authored.sections(written, of([support.lesson(1)], "unit-01"))


def test_every_authored_section_is_inhabited_and_keyed():
    # ⚠️ The denominator: an overlay that produced no sections would satisfy every
    # per-section assertion above.
    written = overlay(
        [
            support.authored_section("lang", lang="prose"),
            support.authored_section("practice", lang="prose"),
        ]
    )
    built = authored.sections(written, material())
    assert len(built) == 2
    assert all(section["key"] for section in built)
