"""Mirror of `src/studyforge/corpus/discovery/site.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

from studyforge.address import Address
from studyforge.corpus.discovery import Artifact, Site, Unidentified
from studyforge.corpus.placement import Identity

PROSE_ADDRESS = Address.of("modules")
CODE_ADDRESS = Address.of("basics", "16-streams-api")


def artifact(path, corpus="code-corpus", address=CODE_ADDRESS, **overrides):
    return Artifact(
        PurePosixPath(path),
        Identity(corpus=corpus, address=address, variant="text", **overrides),
    )


UNIT = artifact("anywhere/seven.unit.html", unit=7)
CONTAINER = artifact("anywhere/streams.section.html", kind="container")
OTHER = artifact("elsewhere/one.unit.html", corpus="prose-corpus", address=PROSE_ADDRESS, unit=1)


def test_units_and_containers_are_told_apart_by_what_they_say_they_are():
    site = Site((UNIT, CONTAINER))
    assert site.units == (UNIT,)
    assert site.containers == (CONTAINER,)


def test_a_unit_is_found_by_identity_and_never_by_path():
    site = Site((UNIT, CONTAINER, OTHER))
    assert site.unit("code-corpus", CODE_ADDRESS, 7) is UNIT
    assert site.unit("prose-corpus", PROSE_ADDRESS, 1) is OTHER
    # ⛔ The same address under a corpus that does not claim it is not a match.
    assert site.unit("prose-corpus", CODE_ADDRESS, 7) is None
    assert site.unit("code-corpus", CODE_ADDRESS, 8) is None


def test_the_same_unit_moved_anywhere_is_the_same_answer():
    # ⭐ R4 as a property of the lookup rather than of the scan: two `Site`s
    # differing only in where the file sits answer identically.
    here = Site((artifact("a/b/c/seven.unit.html", unit=7),))
    there = Site((artifact("z.unit.html", unit=7),))
    assert here.unit("code-corpus", CODE_ADDRESS, 7) is not None
    assert there.unit("code-corpus", CODE_ADDRESS, 7) is not None
    assert here.units[0].identity == there.units[0].identity


def test_the_corpora_are_sorted_rather_than_first_seen():
    # ⛔ R10: this is printed, so it may not depend on iteration order.
    site = Site((UNIT, OTHER, CONTAINER))
    assert site.corpora == ("code-corpus", "prose-corpus")


def test_of_returns_only_one_corpus_worth():
    site = Site((UNIT, CONTAINER, OTHER))
    assert site.of("prose-corpus") == (OTHER,)
    assert set(site.of("code-corpus")) == {UNIT, CONTAINER}
    assert site.of("no-such-corpus") == ()


def test_paths_covers_the_identified_and_the_unidentified_alike():
    site = Site((UNIT,), (Unidentified(PurePosixPath("orphan.unit.html"), "no block"),))
    assert site.paths == ("anywhere/seven.unit.html", "orphan.unit.html")


def test_the_document_sorts_by_path_however_the_site_was_built():
    # ⛔ R10, and it is not the scan's sort written twice: this one is what
    # makes the cache reproducible for a `Site` assembled by anything else.
    forwards = Site((UNIT, OTHER)).document
    backwards = Site((OTHER, UNIT)).document
    assert forwards == backwards
    assert [entry["path"] for entry in forwards["artifacts"]] == [
        "anywhere/seven.unit.html",
        "elsewhere/one.unit.html",
    ]


def test_the_document_carries_no_version_key():
    # ⛔ Two signals, two tests. `site_api` answers "is this the shape I
    # speak?"; this document is the content signal and must not fold one into
    # the other.
    assert set(Site((UNIT,)).document) == {"artifacts", "unidentified"}


def test_the_document_records_every_unidentified_page_by_name():
    # ⛔ R6, carried into the cache: a page that could not be identified is
    # part of what a later reader compares against.
    site = Site((), (Unidentified(PurePosixPath("orphan.unit.html"), "carries no block"),))
    assert site.document["unidentified"] == [
        {"path": "orphan.unit.html", "fault": "carries no block"}
    ]


def test_an_artifact_records_its_identity_as_the_block_wrote_it():
    assert UNIT.document["identity"] == UNIT.identity.document
    assert UNIT.document["path"] == "anywhere/seven.unit.html"


def test_a_site_holds_nothing_by_default():
    empty = Site()
    assert empty.artifacts == () and empty.unidentified == ()
    assert empty.corpora == () and empty.paths == ()
