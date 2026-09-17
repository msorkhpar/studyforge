"""The archive document format (SF-06).

⚠️ The home-path material is **assembled at run time** rather than written as
a literal: this file is swept by the repository hygiene check like every other
tracked file, and that check has no allow-list for home paths. ⛔ Nothing here
came from any real machine, account or person.
"""

import json
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.archive import document as doc
from studyforge.archive.document import (
    DOCUMENT_KEYS,
    KNOWN_RAW_API,
    OPTIONAL_KEYS,
    RAW_API,
    build,
    content_sha256,
    load,
    parse,
    render,
)
from studyforge.archive.errors import ArchiveError
from studyforge.archive.scrub import PersonalDataLeak, shape_in
from tests.fixture_checks import coverage, fixture_paths
from tests.support import repository_root

HOME = "/" + "home/jane"
EMAIL = "jane.doe@example.invalid"

FIXTURES = Path("tests/fixtures")
LEAKING = FIXTURES / "invalid/personal-data/archive/solo/raw/prose/unit-01/lesson-1.json"

BLOCKS = [
    {"type": "heading", "level": 2, "text": "One"},
    {"type": "para", "text": "Two."},
]

#: A decorator on its own line — address-shaped once serialised, and not
#: before. See `test_the_gate_reads_decoded_strings_and_not_the_rendered_bytes`.
DECORATOR = {
    "type": "code",
    "lang": "python",
    "text": 'import flask\n@app.route("/x")\ndef x(): ...',
}

#: A minimal record for the one optional key that has a shape of its own.
#: ⚠️ Safe-pattern clean by construction — `studyforge.exercise` refuses
#: anything else, and `tests/studyforge/exercise/` is where that is proved.
GRADED_EXERCISE = {
    "main_path": "practice/src/main/java/Solution.java",
    "test_path": "practice/src/test/java/SolutionTest.java",
    "run_command": ["mvn", "-q", "compile"],
    "test_command": ["mvn", "-q", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
}

BASE = {
    "source": "demo",
    "address": ["solo"],
    "variant": "prose",
    "unit": 1,
    "kind": "lesson",
    "ordinal": 1,
    "ingested": "2026-01-05",
    "title": "Unit 1",
    "blocks": BLOCKS,
}


#: ⛔ **What this module's sweeps assert, as rule ids** (Ruling 46). `build`
#: recomputes `counts` and `content_sha256`, and both `parse` and `build`
#: refuse an R7 leak and a user-authoritative exercise — so a fixture declared
#: to break any of the four is a fixture this module is not entitled to read.
#:
#: ⚠️ **Naming them gained five documents.** This used to say `depth1, depth2`,
#: which dropped every invalid corpus including the four that break nothing
#: this module asserts. ⛔ `by directory name` is not a reason (`FND-09`).
ASSERTED = {"counts", "digest", "personal-data", "exercise-trust"}


def archive_paths():
    """Every archive document a sweep asserting `ASSERTED` is entitled to read."""
    return [path for _where, path in fixture_paths(asserting=ASSERTED, within="/raw/")]


def parts_of(document):
    """The `build` keyword arguments that reproduce `document`."""
    derived = ("raw_api", "counts", "content_sha256")
    parts = {key: document[key] for key in DOCUMENT_KEYS if key not in derived}
    for key in OPTIONAL_KEYS:
        if key in document:
            parts[key] = document[key]
    return parts


# --------------------------------------------------------------------------
# The round trip, byte for byte
# --------------------------------------------------------------------------


def test_every_committed_document_round_trips_byte_for_byte():
    # ⭐ R10's acceptance. `parse` then `render` must reproduce the file, or
    # an unchanged document re-renders differently and every digest downstream
    # becomes noise.
    paths = archive_paths()
    # ⛔ Ruling 48: the denominator, not `assert paths`. An exclusion widened by
    # mistake leaves a non-empty list and a sweep that reads half the tree.
    assert len(paths) == coverage(asserting=ASSERTED).swept
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert render(parse(text, path.name)) == text, path.name


def test_build_reproduces_every_committed_document_byte_for_byte():
    # ⚠️ Stronger than the round trip: it proves the *key order* and the
    # derived fields — `counts` and `content_sha256` — are this module's and
    # not merely copied through from the file.
    seen = set()
    for path in archive_paths():
        text = path.read_text(encoding="utf-8")
        document = json.loads(text)
        assert render(build(**parts_of(document))) == text, path.name
        seen.update(key for key in OPTIONAL_KEYS if key in document)
    # ⛔ "Including every optional key" is part of the acceptance, so the
    # sweep asserts it actually met all three rather than none.
    assert seen == set(OPTIONAL_KEYS)


def test_the_key_order_is_what_reaches_disk():
    text = render(build(**BASE))
    order = [line.split('"')[1] for line in text.splitlines() if line.startswith('  "')]
    assert tuple(order) == DOCUMENT_KEYS


def test_W289_a_non_object_block_is_refused_through_the_builder_and_never_raises():
    # ⛔ `W282/1`, from the side `W282` could not reach: `check_counts` filters
    # to object blocks first, and the builder calls `counts_of` unfiltered — so
    # `AttributeError` used to travel out of `build`, naming a TYPE and never
    # the block. ⭐ The positive direction first, or the refusal proves nothing.
    assert build(**BASE)["counts"]["paras"] == 1

    with pytest.raises(ArchiveError) as raised:
        build(**{**BASE, "blocks": [*BLOCKS, "not an object"]})

    assert "blocks[2]" in str(raised.value), "the refusal names which block"
    assert "solo/unit-1/lesson-1" in str(raised.value), "and which document"


def test_optional_keys_are_appended_after_the_digest():
    # ⛔ So adding one cannot disturb `content_sha256`, and a document written
    # before a key existed still renders what it always did.
    # ⚠️ Built as a **practice**: `exercise` joined `OPTIONAL_KEYS` at SF-23 and
    # belongs to a practice document, so asserting "every optional key, in
    # order" now needs the one document kind that may carry all of them.
    document = build(
        **{**BASE, "kind": "practice"},
        starting_code="x",
        assets_sha256="a" * 64,
        media_skipped=True,
        exercise=GRADED_EXERCISE,
    )
    assert tuple(document)[: len(DOCUMENT_KEYS)] == DOCUMENT_KEYS
    assert tuple(document)[len(DOCUMENT_KEYS) :] == OPTIONAL_KEYS


def test_media_skipped_is_written_only_when_something_was_skipped():
    # ⚠️ Falsy means "nothing was skipped", which is what the absent key
    # already meant, so every document written before it existed keeps
    # asserting exactly what it always did.
    assert "media_skipped" not in build(**BASE)
    assert "media_skipped" not in build(**BASE, media_skipped=False)
    assert build(**BASE, media_skipped=True)["media_skipped"] is True


def test_starting_code_is_written_even_when_empty():
    # ⚠️ Unlike the other two: an empty starting fence is a fact about the
    # practice, not the absence of one.
    assert build(**BASE, starting_code="")["starting_code"] == ""


# --------------------------------------------------------------------------
# The digest answers exactly one question
# --------------------------------------------------------------------------


def test_editing_a_block_changes_the_digest():
    before = build(**BASE)
    edited = [dict(BLOCKS[0]), {"type": "para", "text": "Two, revised."}]
    after = build(**{**BASE, "blocks": edited})
    assert after["content_sha256"] != before["content_sha256"]


def test_changing_the_ingestion_date_does_not_change_the_digest():
    # ⛔ Folding `ingested` in would make every re-ingest differ regardless of
    # content, and the one signal the digest exists for would be worthless.
    before = build(**BASE)
    after = build(**{**BASE, "ingested": "2027-02-02"})
    assert after["content_sha256"] == before["content_sha256"]
    assert after["ingested"] != before["ingested"]


def test_media_is_outside_the_digest():
    # ⛔ Otherwise re-downloading a 6 MB video looks like a source edit.
    video = {"src": "media/x.mp4", "poster": None, "mime": "video/mp4"}
    assert build(**BASE, video=video)["content_sha256"] == build(**BASE)["content_sha256"]


def test_the_digest_is_recomputable_from_the_file_alone():
    for path in archive_paths():
        document = json.loads(path.read_text(encoding="utf-8"))
        assert content_sha256(document["blocks"]) == document["content_sha256"], path.name


# --------------------------------------------------------------------------
# R9: an unknown version is refused, never migrated
# --------------------------------------------------------------------------


def test_an_unknown_raw_api_is_refused():
    text = json.dumps({**build(**BASE), "raw_api": 99})
    with pytest.raises(ArchiveError, match="raw_api 99"):
        parse(text, "lesson-1.json")


def test_a_json_true_is_refused_where_one_is_supported():
    # ⛔ The guard's whole reason for existing: `True in {1}` is true in Python.
    text = json.dumps({**build(**BASE), "raw_api": True})
    with pytest.raises(ArchiveError, match="raw_api"):
        parse(text, "lesson-1.json")


def test_the_version_refusal_says_it_is_not_a_migration():
    text = json.dumps({**build(**BASE), "raw_api": 99})
    with pytest.raises(ArchiveError) as raised:
        parse(text, "lesson-1.json")
    assert "never migrated in place" in str(raised.value)


def test_this_module_owns_the_set_and_not_the_check():
    # ⛔ SF-33 ships a tree test that fails any module rolling its own
    # membership test. This is the same rule asserted from the other side.
    assert KNOWN_RAW_API == frozenset({RAW_API})
    source = (repository_root() / "src/studyforge/archive/document.py").read_text(encoding="utf-8")
    assert "from studyforge.version import" in source
    assert "not in KNOWN_RAW_API" not in source


def test_the_version_is_checked_before_the_gate():
    # ⚠️ Otherwise a v2 archive carrying a v2-shaped field is refused for a
    # v1 reason and the integrator upgrades the wrong thing.
    text = json.dumps({"raw_api": 99, "source": f"ran from {HOME}"})
    with pytest.raises(ArchiveError, match="raw_api"):
        parse(text, "lesson-1.json")


# --------------------------------------------------------------------------
# R7: the gate is invoked, and it refuses
# --------------------------------------------------------------------------


def test_the_committed_leaking_document_is_refused_not_cleaned():
    # ⚠️ The second assertion is what stops this becoming a test of nothing:
    # if the negative fixture were ever neutered into clean input, `load`
    # would still be "correct" and the acceptance would be protecting an
    # empty box. ⛔ Asked through the shape, never by spelling the value.
    path = repository_root() / LEAKING
    with pytest.raises(PersonalDataLeak):
        load(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    assert shape_in(document["blocks"][1]["text"]) == "home path"


def test_a_leak_in_the_metadata_alone_is_refused_by_build():
    # ⭐ **This is how the gate's invocation is asserted rather than assumed.**
    # The leak is in `source`, which is not a block and not the title, so only
    # the whole-document gate can see it. A build that stopped calling that
    # gate would pass every "clean input passes" test and fail this one.
    with pytest.raises(PersonalDataLeak):
        build(**{**BASE, "source": f"ingested from {HOME}/corpus"})


def test_a_leak_in_the_metadata_alone_is_refused_by_parse():
    text = json.dumps({**build(**BASE), "source": f"ingested from {HOME}/corpus"})
    with pytest.raises(PersonalDataLeak):
        parse(text, "lesson-1.json")


def test_a_leak_inside_a_nested_block_is_refused():
    quote = {"type": "quote", "blocks": [{"type": "para", "text": f"mail {EMAIL}"}]}
    with pytest.raises(PersonalDataLeak):
        build(**{**BASE, "blocks": [quote]})


def test_a_leak_in_an_asset_record_is_refused():
    assets = [{"remote": None, "local": f"{HOME}/media/x.png", "sha256": None}]
    with pytest.raises(PersonalDataLeak):
        build(**BASE, assets=assets)


def test_build_runs_the_gate_more_than_once(monkeypatch):
    # ⚠️ Belt and braces is part of the contract, not an implementation
    # detail: a match at the inner gate is the news that an upstream stage
    # failed (R6), and one call would lose that.
    calls = []
    monkeypatch.setattr(doc, "assert_clean", lambda value, where: calls.append(where))
    build(**BASE)
    assert len(calls) >= 3


def test_parse_runs_the_gate(monkeypatch):
    text = render(build(**BASE))
    calls = []
    monkeypatch.setattr(doc, "assert_clean", lambda value, where: calls.append(where))
    parse(text, "lesson-1.json")
    assert calls == ["lesson-1.json"]


def test_the_gate_reads_decoded_strings_and_not_the_rendered_bytes():
    # ⛔ The measured defect: in JSON a newline is a backslash and an `n`, so a
    # decorator on its own line serialises with `n` immediately before the `@`
    # and is address-shaped. Three clean lessons were refused that way.
    document = build(**{**BASE, "blocks": [DECORATOR]})
    parse(render(document), "lesson-1.json")


def test_and_the_rendered_bytes_really_would_have_matched():
    # ⭐ Without this the test above is vacuous — it would pass on any clean
    # document. Here is the proof that the hazard is real.
    assert shape_in(render(build(**{**BASE, "blocks": [DECORATOR]}))) == "email address"


def test_a_document_of_card_shaped_strings_passes():
    # ⛔ ISO-8583's subject matter. The gate is not a content classifier.
    cards = ("4111111111111111", "5500 0000 0000 0004")
    pans = [{"type": "para", "text": f"Field 2 carries {n}."} for n in cards]
    build(**{**BASE, "blocks": pans})


# --------------------------------------------------------------------------
# Refusals that do not become leaks themselves
# --------------------------------------------------------------------------


def test_load_names_the_file_and_never_the_path_it_read(tmp_path):
    # ⛔ R7: an absolute path in a refusal is personal data in a log, from the
    # module whose own gate exists to prevent exactly that.
    path = tmp_path / "lesson-1.json"
    path.write_text(json.dumps({**build(**BASE), "raw_api": 99}), encoding="utf-8")
    with pytest.raises(ArchiveError) as raised:
        load(path)
    message = str(raised.value)
    assert "lesson-1.json" in message
    assert str(tmp_path) not in message


def test_a_missing_file_names_the_reason_and_not_the_exception(tmp_path):
    # ⛔ `OSError` formats itself with the filename it was given, so `{exc}`
    # here would produce a refusal carrying an absolute path. Name `strerror`.
    with pytest.raises(ArchiveError) as raised:
        load(tmp_path / "absent.json")
    message = str(raised.value)
    assert "absent.json" in message
    assert str(tmp_path) not in message


def test_malformed_json_names_the_position_and_never_the_text():
    with pytest.raises(ArchiveError) as raised:
        parse('{"raw_api": 1, "source": "' + HOME + '"', "lesson-1.json")
    message = str(raised.value)
    assert "not valid JSON" in message
    assert "line" in message and "column" in message
    assert "jane" not in message


@pytest.mark.parametrize("text", ["[]", '"a string"', "12"])
def test_a_document_that_is_not_an_object_is_refused(text):
    with pytest.raises(ArchiveError, match="JSON object"):
        parse(text, "lesson-1.json")


# --------------------------------------------------------------------------
# What build refuses to make
# --------------------------------------------------------------------------


def test_an_unknown_kind_is_refused():
    with pytest.raises(ArchiveError, match="kind"):
        build(**{**BASE, "kind": "quiz"})


@pytest.mark.parametrize("ingested", ["2026-1-5", "January 2026", "", None, 20260105])
def test_an_ingested_value_that_is_not_an_iso_date_is_refused(ingested):
    with pytest.raises(ArchiveError, match="ingested"):
        build(**{**BASE, "ingested": ingested})


def test_the_refusal_of_a_bad_date_does_not_echo_it():
    with pytest.raises(ArchiveError) as raised:
        build(**{**BASE, "ingested": f"{HOME}/when"})
    assert "jane" not in str(raised.value)


def test_the_address_is_slugs_and_not_a_path():
    # ⛔ Where the document lands is placement's decision (R2). An address
    # carrying a separator would have made the two the same thing.
    with pytest.raises(Exception, match="slug"):
        build(**{**BASE, "address": ["basics/getting-started"]})


def test_an_address_object_and_a_list_build_the_same_document():
    from_list = build(**BASE)
    from_address = build(**{**BASE, "address": Address.of("solo")})
    assert from_list == from_address
    assert from_list["address"] == ["solo"]
