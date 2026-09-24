"""Mirror of `src/studyforge/unit/builder/document.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit.builder.document import (
    API,
    BUILT_FROM_KEYS,
    PRACTICES_KEYS,
    UNIT_KEYS,
    build,
    render,
)
from studyforge.unit.builder.material import of
from studyforge.unit.content import from_document
from studyforge.unit.errors import ContentError
from tests.studyforge.unit.builder import support


def material(documents=None):
    return of(documents or [support.lesson(1), support.practice(1)], "unit-01")


# --------------------------------------------------------------------------
# ⛔ the key order is the format (R10)
# --------------------------------------------------------------------------


def test_the_document_carries_exactly_its_keys_in_order():
    assert tuple(build(material())) == UNIT_KEYS


def test_regenerating_produces_identical_bytes():
    # ⛔ The unit builder's acceptance and R10: nobody can tell a change from a reformat
    # if a rebuild is not byte-identical.
    once = render(build(material()))
    assert render(build(material())) == once


def test_the_api_is_declared_and_is_the_registered_key():
    # ⚠️ R9's table names this contract `unit.json` / `api`.
    document = build(material())
    assert document["api"] == API


# --------------------------------------------------------------------------
# ⛔ `practices` holds two counts and no verdict
# --------------------------------------------------------------------------


def test_practices_says_declared_and_archived_and_judges_neither():
    # ⚠️ Without this the page lies by omission: a unit whose practices were
    # never ingested renders exactly like one that has none.
    document = build(material(), declared_practices=3)
    assert tuple(document["practices"]) == PRACTICES_KEYS
    assert document["practices"] == {"declared": 3, "archived": 1}


def test_a_corpus_that_never_declared_a_count_reports_nothing_not_zero():
    # ⛔ `None` and `0` are different answers and must not render the same.
    document = build(material())
    assert document["practices"]["declared"] is None
    assert document["practices"]["archived"] == 1


@pytest.mark.parametrize("declared", [-1, "3", 1.0, True])
def test_a_declared_count_that_is_not_a_count_is_refused(declared):
    with pytest.raises(ContentError, match="declared practice count"):
        build(material(), declared_practices=declared)


def test_no_verdict_word_appears_in_the_document():
    # ⭐ The verdict — complete, short, unknown — is `studyforge validate`'s
    # single job. The page only needs to know there is more to come.
    document = build(material(), declared_practices=9)
    assert set(document["practices"]) == {"declared", "archived"}


# --------------------------------------------------------------------------
# ⛔ provenance is `built_from`, and it records no path
# --------------------------------------------------------------------------


def test_every_archive_document_is_named_in_provenance():
    # ⚠️ The denominator: assert the list is inhabited, not only that its entries are
    # well shaped — an empty `built_from` satisfies every per-entry loop.
    document = build(material())
    assert len(document["built_from"]) == 2
    assert all(tuple(entry) == BUILT_FROM_KEYS for entry in document["built_from"])


def test_provenance_carries_the_digest_and_the_ingest_date():
    entry = build(material())["built_from"][0]
    assert entry["content_sha256"]
    assert entry["ingested"] == "2026-01-05"


def test_provenance_records_no_path_of_any_kind():
    # ⛔ A location is a fact about a disk, and a provenance record names
    # none. ⚠️ The array is not called `sources`, `source` or
    # `origin`, because `source` already means a corpus id one level up.
    document = build(material())
    assert "sources" not in document
    assert document["source"] == "demo"
    for entry in document["built_from"]:
        for value in entry.values():
            assert "/" not in str(value)


# --------------------------------------------------------------------------
# ⛔ an overlay and material that are not the same unit are refused
# --------------------------------------------------------------------------


def test_an_overlay_for_a_different_unit_is_refused():
    # ⛔ Nothing downstream could notice: both halves are individually valid,
    # and joined they put one author's headings over somebody else's material.
    written = from_document(
        support.overlay_document([support.authored_section("lang", lang="prose")], unit=7),
        depth=1,
    )
    with pytest.raises(ContentError, match="records unit 7"):
        build(material(), overlay=written)


def test_an_overlay_for_a_different_address_is_refused():
    document = support.overlay_document([support.authored_section("lang", lang="prose")])
    document["address"] = ["elsewhere"]
    written = from_document(document, depth=1)
    with pytest.raises(ContentError, match="different addresses"):
        build(material(), overlay=written)


# --------------------------------------------------------------------------
# the title
# --------------------------------------------------------------------------


def test_the_authors_title_wins_over_the_archives():
    # ⚠️ The archive's title is one document's heading; a unit is the whole
    # set, and an author who named the unit meant that name for all of it.
    written = from_document(
        support.overlay_document(
            [support.authored_section("lang", lang="prose")], title="The whole unit"
        ),
        depth=1,
    )
    assert build(material(), overlay=written)["title"] == "The whole unit"


def test_the_archives_title_is_the_fallback():
    assert build(material())["title"] == "A lesson"


def test_a_caller_may_name_the_unit_outright():
    assert build(material(), title="Named by the caller")["title"] == "Named by the caller"
