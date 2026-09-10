"""Mirror of `src/studyforge/contents/status.py` (R12)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePosixPath

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.contents import (
    STATUS_FILENAME,
    STATUS_KEYS,
    UNIT_STATUS_KEYS,
    ContentsError,
    digest,
    found,
    from_status_document,
    join,
    load_status,
    missing,
    order,
    parse_status,
    render_status,
    status,
    status_document,
    write_status,
)
from studyforge.corpus.discovery import Artifact, Site
from studyforge.corpus.placement import Identity
from tests.studyforge.contents.corpora import fixture_contents, written

#: ⛔ Assembled rather than written whole (R7).
HOME = "/" + "home/jane"

DEPTH2_ORDER = (
    "advanced/02-going-further/unit-01",
    "advanced/02-going-further/unit-02",
    "basics/01-getting-started/unit-01",
    "basics/01-getting-started/unit-02",
    "basics/01-getting-started/unit-03",
)


def a_site(built, keys) -> Site:
    """A scan that found a page for each of `keys`, at a path that says nothing."""
    entries = {entry.key: entry for entry in order(built)}
    return Site(
        artifacts=tuple(
            Artifact(
                path=PurePosixPath("somewhere/else/page.unit.html"),
                identity=Identity(
                    corpus=built.corpus,
                    address=entries[key].address,
                    variant="java",
                    kind="unit",
                    unit=entries[key].ordinal,
                ),
            )
            for key in keys
        )
    )


def test_every_declared_unit_gets_a_row_whether_or_not_it_is_here():
    # ⛔ "Absent" and "not mentioned" must not be the same reading.
    built = fixture_contents("depth2")
    local = status(built, present=DEPTH2_ORDER[:2])
    assert tuple(unit.key for unit in local.units) == DEPTH2_ORDER
    assert [unit.present for unit in local.units] == [True, True, False, False, False]


def test_the_rows_are_in_reading_order():
    built = fixture_contents("depth2")
    local = status(built, present=())
    assert [unit.key for unit in local.units] == [entry.key for entry in order(built)]


def test_what_is_next_is_the_first_unread_unit_in_reading_order():
    built = fixture_contents("depth2")
    assert status(built, present=(), read=()).next_key == DEPTH2_ORDER[0]
    assert status(built, present=(), read=DEPTH2_ORDER[:2]).next_key == DEPTH2_ORDER[2]


def test_a_reader_who_has_read_out_of_order_is_still_sent_to_the_first_gap():
    built = fixture_contents("depth2")
    local = status(built, present=(), read=(DEPTH2_ORDER[0], DEPTH2_ORDER[3]))
    assert local.next_key == DEPTH2_ORDER[1]


def test_a_finished_corpus_has_nothing_next():
    built = fixture_contents("depth2")
    assert status(built, present=DEPTH2_ORDER, read=DEPTH2_ORDER).next_key is None


def test_the_scan_is_read_through_identity_and_never_through_a_path():
    # ⛔ R4: every page in this site sits at one meaningless path.
    built = fixture_contents("depth2")
    site = a_site(built, DEPTH2_ORDER[:3])
    assert found(site, built.corpus) == frozenset(DEPTH2_ORDER[:3])


def test_a_scan_of_another_corpus_contributes_nothing():
    built = fixture_contents("depth2")
    site = a_site(built, DEPTH2_ORDER)
    assert found(site, "some-other-corpus") == frozenset()


def test_units_declared_and_not_generated_are_reported_rather_than_dropped():
    # ⭐ The short site made visible: 3 of 5 built, and the contents still say 5.
    built = fixture_contents("depth2")
    local = status(built, present=found(a_site(built, DEPTH2_ORDER[:3]), built.corpus))
    assert missing(built, local) == DEPTH2_ORDER[3:]
    assert len(local.units) == 5


def test_a_complete_build_is_missing_nothing():
    built = fixture_contents("depth2")
    assert missing(built, status(built, present=DEPTH2_ORDER)) == ()


def test_a_status_from_another_corpus_is_refused_rather_than_joined():
    built = fixture_contents("depth2")
    local = replace(status(built, present=()), corpus="depth1-demo")
    with pytest.raises(ContentsError) as raised:
        join(built, local)
    assert "different units in different corpora" in str(raised.value)


def test_a_status_annotating_an_older_table_of_contents_is_refused():
    # ⛔ The whole reason the split is safe: ids that no longer mean the same
    # unit would join perfectly and mean nothing.
    built = fixture_contents("depth2")
    local = status(built, present=())
    moved = replace(built, title="Depth Two Demo, Revised")
    with pytest.raises(ContentsError) as raised:
        join(moved, local)
    assert "one of the pair is stale" in str(raised.value)


def test_a_matching_pair_joins_by_key():
    built = fixture_contents("depth2")
    local = status(built, present=DEPTH2_ORDER[:1])
    annotations = join(built, local)
    assert annotations[DEPTH2_ORDER[0]].present is True
    assert annotations[DEPTH2_ORDER[1]].present is False


def test_the_status_names_the_exact_document_it_annotates():
    built = fixture_contents("depth1")
    assert status(built, present=()).toc_sha256 == digest(built)


def test_the_document_is_written_in_a_stated_key_order():
    built = fixture_contents("depth1")
    document = status_document(status(built, present=()))
    assert tuple(document) == STATUS_KEYS
    assert tuple(document["units"][0]) == UNIT_STATUS_KEYS


def test_the_stated_order_survives_into_the_BYTES():
    # ⛔ The object's order is not the document's order; a `sort_keys=True` on
    # the way out would leave the assertion above passing (R10).
    text = render_status(status(fixture_contents("depth1"), present=()))
    assert [text.index(f'"{key}"') for key in STATUS_KEYS] == sorted(
        text.index(f'"{key}"') for key in STATUS_KEYS
    )
    inner = text[text.index('"units"') :]
    assert [inner.index(f'"{key}"') for key in UNIT_STATUS_KEYS] == sorted(
        inner.index(f'"{key}"') for key in UNIT_STATUS_KEYS
    )


def test_the_local_document_carries_no_structure_of_its_own():
    # ⚠️ It annotates by id; a second copy of the hierarchy would be a second
    # thing to disagree with the first.
    text = render_status(status(fixture_contents("depth2"), present=()))
    assert "groups" not in text
    assert "levels" not in text
    assert "title" not in text


def test_a_rendered_status_reads_back_to_the_same_value():
    built = fixture_contents("depth2")
    local = status(built, present=DEPTH2_ORDER[:2], read=DEPTH2_ORDER[:1])
    assert parse_status(render_status(local)) == local


def test_a_finished_status_round_trips_with_nothing_next():
    built = fixture_contents("depth1")
    keys = tuple(entry.key for entry in order(built))
    local = status(built, present=keys, read=keys)
    assert parse_status(render_status(local)).next_key is None


@pytest.mark.parametrize("declared", [None, 0, 99, True, "1"])
def test_an_unknown_toc_api_is_refused(declared):
    document = status_document(status(fixture_contents("depth1"), present=()))
    with pytest.raises(ContentsError):
        from_status_document({**document, "toc_api": declared})


def test_an_unknown_key_is_refused():
    document = status_document(status(fixture_contents("depth1"), present=()))
    with pytest.raises(ContentsError) as raised:
        from_status_document({**document, "surprise": 1})
    assert "unknown key(s), ['surprise']" in str(raised.value)


def test_an_absent_units_list_is_refused_rather_than_read_as_empty():
    document = status_document(status(fixture_contents("depth1"), present=()))
    del document["units"]
    with pytest.raises(ContentsError) as raised:
        from_status_document(document)
    assert "annotates nothing" in str(raised.value)


@pytest.mark.parametrize("value", [1, 0, "true", None])
def test_a_flag_that_is_not_a_boolean_is_refused(value):
    # ⛔ `1` is not `true`: a number here means a generator wrote a count where
    # a flag belongs, and reading it as true would hide that.
    document = status_document(status(fixture_contents("depth1"), present=()))
    document["units"][0]["present"] = value
    with pytest.raises(ContentsError):
        from_status_document(document)


def test_an_annotation_carrying_an_unknown_key_is_refused():
    document = status_document(status(fixture_contents("depth1"), present=()))
    document["units"][0]["extra"] = 1
    with pytest.raises(ContentsError):
        from_status_document(document)


def test_text_that_is_not_json_is_refused():
    with pytest.raises(ContentsError):
        parse_status("{not json")


def test_json_that_is_not_an_object_is_refused():
    with pytest.raises(ContentsError):
        parse_status("[]")


def test_a_leak_in_the_local_document_is_refused_as_itself():
    document = status_document(status(fixture_contents("depth1"), present=()))
    document["units"][0]["key"] = f"{HOME}/x"
    with pytest.raises(PersonalDataLeak):
        from_status_document(document)


def test_a_written_status_loads_back(tmp_path):
    built = fixture_contents("depth2")
    local = status(built, present=DEPTH2_ORDER[:2])
    target = tmp_path / "out" / STATUS_FILENAME
    write_status(target, local)
    assert load_status(target) == local
    assert written(target) == render_status(local)
    assert [path.name for path in sorted(tmp_path.rglob("*"))] == ["out", STATUS_FILENAME]


def test_loading_a_status_that_is_not_there_names_the_file_and_not_the_path(tmp_path):
    with pytest.raises(ContentsError) as raised:
        load_status(tmp_path / "missing" / STATUS_FILENAME)
    assert str(tmp_path) not in str(raised.value)


def test_loading_a_status_that_is_not_utf8_is_refused(tmp_path):
    target = tmp_path / STATUS_FILENAME
    target.write_bytes(b"\xff\xfe")
    with pytest.raises(ContentsError) as raised:
        load_status(target)
    assert "UTF-8" in str(raised.value)


def test_missing_refuses_a_mismatched_pair_before_it_answers():
    # ⛔ It reports through `join`, so it cannot answer about a pair that does
    # not belong together.
    built = fixture_contents("depth2")
    local = replace(status(built, present=()), toc_sha256="0" * 64)
    with pytest.raises(ContentsError):
        missing(built, local)
