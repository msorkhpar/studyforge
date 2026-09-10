"""Mirror of `src/studyforge/contents/document.py` (R12)."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.contents import (
    KNOWN_TOC_API,
    TOC_API,
    TOC_FILENAME,
    ENTRY_KEYS,
    TOC_KEYS,
    ContentsError,
    digest,
    from_document,
    load,
    order,
    parse,
    render,
    to_document,
    write,
)
from studyforge.version import CONTRACT_FIELDS
from tests.studyforge.contents.corpora import fixture_contents, written

#: ⛔ Assembled rather than written whole, so this file carries no path that
#: looks like a home directory even in a string the gate is meant to refuse.
HOME = "/" + "home/jane"


def a_document(**overrides) -> dict:
    return {**to_document(fixture_contents("depth1")), **overrides}


def test_the_document_is_written_in_a_stated_key_order():
    assert tuple(to_document(fixture_contents("depth2"))) == TOC_KEYS


def test_the_stated_order_survives_into_the_BYTES():
    # ⛔ **The object's order is not the document's order**, and only one of
    # them is what a consumer reads. `json.dumps(sort_keys=True)` would re-sort
    # every key on the way out and leave the assertion above passing — measured
    # as a surviving mutant, and this is the row that kills it (R10).
    text = render(fixture_contents("depth2"))
    assert [key for key in TOC_KEYS if f'"{key}"' in text] == list(TOC_KEYS)
    assert [text.index(f'"{key}"') for key in TOC_KEYS] == sorted(
        text.index(f'"{key}"') for key in TOC_KEYS
    )


def test_a_groups_and_a_units_keys_keep_their_order_in_the_bytes_too():
    text = render(fixture_contents("depth2"))
    inner = text[text.index('"units"') :]
    assert [inner.index(f'"{key}"') for key in ENTRY_KEYS] == sorted(
        inner.index(f'"{key}"') for key in ENTRY_KEYS
    )


def test_toc_api_is_registered_where_the_shared_guard_can_see_it():
    # ⛔ A task that versions a new contract registers it in the same commit,
    # or the tree check cannot see it.
    assert "toc_api" in CONTRACT_FIELDS
    assert KNOWN_TOC_API == frozenset({TOC_API})


def test_rendering_the_same_corpus_twice_gives_the_same_bytes():
    # ⛔ R10, and it is the whole claim of the stable half.
    built = fixture_contents("depth2")
    assert render(built) == render(fixture_contents("depth2"))
    assert render(built).endswith("}\n")


def test_the_document_carries_no_clock():
    # ⚠️ §6's `ingested` exemption is the archive's; here the same question is
    # answered by `digest` against the document itself.
    text = render(fixture_contents("depth2"))
    assert "ingested" not in text
    assert "generated" not in text


def test_a_rendered_document_reads_back_to_the_same_value():
    for name in ("depth1", "depth2"):
        built = fixture_contents(name)
        assert parse(render(built)) == built


def test_the_round_trip_preserves_the_reading_order():
    built = fixture_contents("depth2")
    assert [entry.key for entry in order(parse(render(built)))] == [
        entry.key for entry in order(built)
    ]


def test_the_digest_is_over_the_bytes_a_consumer_holds():
    built = fixture_contents("depth1")
    assert digest(built) == hashlib.sha256(render(built).encode("utf-8")).hexdigest()


def test_two_different_corpora_have_different_digests():
    assert digest(fixture_contents("depth1")) != digest(fixture_contents("depth2"))


@pytest.mark.parametrize("declared", [None, 0, 99, True, 1.0, "1"])
def test_an_unknown_toc_api_is_refused_and_never_migrated(declared):
    with pytest.raises(ContentsError) as raised:
        from_document(a_document(toc_api=declared))
    assert "never migrated" in str(raised.value)


def test_an_unknown_key_is_refused_naming_what_a_contents_document_is():
    with pytest.raises(ContentsError) as raised:
        from_document(a_document(surprise=1))
    assert "unknown key(s), ['surprise']" in str(raised.value)


def test_text_that_is_not_json_is_refused():
    with pytest.raises(ContentsError) as raised:
        parse("{not json")
    assert "not valid JSON" in str(raised.value)


def test_json_that_is_not_an_object_is_refused():
    with pytest.raises(ContentsError):
        parse("[]")


def test_a_document_with_no_levels_cannot_be_read_back():
    # ⚠️ The depth is `len(levels)`, so a document that did not say could not
    # have its unit keys parsed at all.
    with pytest.raises(ContentsError) as raised:
        from_document(a_document(levels=[]))
    assert "levels" in str(raised.value)


def test_a_groups_children_may_not_be_absent():
    document = a_document()
    del document["contents"][0]["units"]
    with pytest.raises(ContentsError) as raised:
        from_document(document)
    assert "short and says nothing" in str(raised.value)


def test_a_group_carrying_an_unknown_key_is_refused():
    document = a_document()
    document["contents"][0]["extra"] = 1
    with pytest.raises(ContentsError):
        from_document(document)


def test_a_unit_entry_carrying_an_unknown_key_is_refused():
    document = a_document()
    document["contents"][0]["units"][0]["extra"] = 1
    with pytest.raises(ContentsError):
        from_document(document)


def test_a_unit_key_that_will_not_parse_is_refused_rather_than_split_here():
    # ⛔ `Address.unit_key`'s own inverse, never a `split` written again here.
    document = a_document()
    document["contents"][0]["units"][0]["key"] = "not-a-unit-key"
    with pytest.raises(ContentsError) as raised:
        from_document(document)
    assert "unreadable" in str(raised.value)


@pytest.mark.parametrize("practices", [None, -1, True, "1", 1.5])
def test_a_practice_count_that_is_not_a_count_is_refused(practices):
    document = a_document()
    document["contents"][0]["units"][0]["practices"] = practices
    with pytest.raises(ContentsError):
        from_document(document)


def test_a_leak_anywhere_in_the_document_is_refused_as_itself():
    # ⛔ Ruling 58: `PersonalDataLeak` travels through as itself and is not
    # folded into "the contents would not build".
    with pytest.raises(PersonalDataLeak):
        from_document(a_document(title=f"{HOME}/notes"))


def test_the_refusal_does_not_reproduce_the_thing_it_refused():
    with pytest.raises(PersonalDataLeak) as raised:
        from_document(a_document(title=f"{HOME}/notes"))
    assert HOME not in str(raised.value)


def test_writing_leaves_no_staging_file_behind(tmp_path):
    built = fixture_contents("depth1")
    target = tmp_path / "out" / TOC_FILENAME
    write(target, built)
    assert written(target) == render(built)
    assert [path.name for path in sorted(tmp_path.rglob("*"))] == ["out", TOC_FILENAME]


def test_a_written_document_loads_back(tmp_path):
    built = fixture_contents("depth2")
    target = tmp_path / TOC_FILENAME
    write(target, built)
    assert load(target) == built


def test_loading_a_file_that_is_not_there_names_the_file_and_not_the_path(tmp_path):
    with pytest.raises(ContentsError) as raised:
        load(tmp_path / "missing" / TOC_FILENAME)
    assert str(tmp_path) not in str(raised.value)
    assert TOC_FILENAME in str(raised.value)


def test_loading_bytes_that_are_not_utf8_is_refused(tmp_path):
    target = tmp_path / TOC_FILENAME
    target.write_bytes(b"\xff\xfe")
    with pytest.raises(ContentsError) as raised:
        load(target)
    assert "UTF-8" in str(raised.value)


def test_the_documents_json_is_indented_and_keeps_non_ascii_as_itself():
    # ⛔ Stated rather than defaulted: both decide the bytes (R10). ⚠️ Asserted
    # against this module's own output, never against `json.dumps` — a check
    # that compared the standard library with itself would pass whatever this
    # module did.
    built = replace(fixture_contents("depth1"), title="Un aperçu")
    text = render(built)
    assert text.splitlines()[1].startswith("  ")
    assert '"title": "Un aperçu"' in text
    assert "\\u" not in text
