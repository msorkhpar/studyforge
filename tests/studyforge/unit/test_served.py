"""Mirror of `src/studyforge/unit/served.py` (R12)."""

from __future__ import annotations

import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.unit.builder import API, build, render
from studyforge.unit.builder.material import of
from studyforge.unit.errors import ContentError
from studyforge.unit.served import UNIT_FILENAME, load, parse
from tests.studyforge.unit.builder import support


def document():
    return build(of([support.lesson(1), support.practice(1)], "unit-01"), declared_practices=1)


def test_a_document_this_build_wrote_reads_back_unchanged():
    # ⭐ The round trip is the contract: what the builder writes is what the
    # server reads, and nothing in between normalises it.
    built = document()
    assert parse(render(built)) == built


def test_load_reads_it_from_disk(tmp_path):
    path = tmp_path / UNIT_FILENAME
    path.write_text(render(document()), encoding="utf-8")
    assert load(path)["api"] == API


# --------------------------------------------------------------------------
# ⛔ this gates rather than trusting `validate`, which is optional
# --------------------------------------------------------------------------


@pytest.mark.parametrize("older", [0, API - 1])
def test_an_older_api_is_refused_rather_than_read(older):
    # ⛔ "Written before sections carried a video" and "this unit has no video"
    # are different answers; a reader that conflated them would render a unit
    # as silent because the build that wrote it did not know about audio.
    # ⚠️ `API - 1` is the shipped predecessor — `W215` bumped this contract for
    # `attachments`, and a document written under the version before it is
    # refused rather than migrated (R9).
    stale = document()
    stale["api"] = older
    with pytest.raises(ContentError):
        parse(json.dumps(stale))


def test_a_served_document_carrying_personal_data_is_refused():
    # ⛔ Ruling 50: `validate` is optional, so a serve-time reader assuming it
    # ran trusts a promise nobody made. This is the last boundary before a
    # browser.
    leaky = document()
    separator = "/"
    leaky["sections"][0]["heading"] = f"{separator}home{separator}jane{separator}notes"
    with pytest.raises(PersonalDataLeak):
        parse(json.dumps(leaky))


def test_text_that_is_not_json_is_refused_without_quoting_the_line():
    # ⛔ The parser's own message quotes the offending line, and this document
    # carries a corpus's text (R7).
    with pytest.raises(ContentError) as raised:
        parse("{ not json")
    assert "not json" not in str(raised.value)


# --------------------------------------------------------------------------
# ⛔ the shape, key by key and in order
# --------------------------------------------------------------------------


def test_a_missing_key_is_refused():
    short = document()
    del short["built_from"]
    with pytest.raises(ContentError, match="must carry exactly"):
        parse(json.dumps(short))


def test_keys_out_of_order_are_refused():
    # ⚠️ These bytes are compared: a document whose keys rendered in another
    # order would look changed to re-ingest detection while saying the same.
    shuffled = dict(reversed(list(document().items())))
    with pytest.raises(ContentError, match="in that order"):
        parse(json.dumps(shuffled))


def test_a_section_missing_a_key_is_refused():
    broken = document()
    del broken["sections"][0]["video"]
    with pytest.raises(ContentError, match="section 0"):
        parse(json.dumps(broken))


def test_practices_missing_a_count_is_refused():
    broken = document()
    del broken["practices"]["declared"]
    with pytest.raises(ContentError, match="'practices'"):
        parse(json.dumps(broken))


def test_a_document_with_no_provenance_is_refused_rather_than_read():
    # ⛔ An entry that cannot be compared against anything is worse than
    # absent: it reads as checked and is not.
    empty = document()
    empty["built_from"] = []
    with pytest.raises(ContentError, match="at least one archive document"):
        parse(json.dumps(empty))


def test_a_provenance_entry_off_contract_is_refused():
    broken = document()
    broken["built_from"][0]["path"] = "somewhere"
    with pytest.raises(ContentError, match="'built_from' entry 0"):
        parse(json.dumps(broken))


def test_every_section_is_checked_and_the_list_is_inhabited():
    # ⚠️ Ruling 48: a document with zero sections would pass every per-section
    # assertion, and zero sections is the bug those assertions guard.
    built = document()
    assert len(built["sections"]) == 2
    assert parse(json.dumps(built)) == built
