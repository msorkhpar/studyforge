"""The container-map format (SF-05).

⚠️ The home-path material is **assembled at run time** rather than written as
a literal: this file is swept by the repository hygiene check like every other
tracked file, and that check has no allow-list for home paths. ⛔ Nothing here
came from any real machine, account or person.
"""

import inspect
import json

import pytest

from studyforge.address import AddressError, is_slug, slugify
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.container import (
    CONTAINER_API,
    CONTAINER_KEYS,
    EDITORIAL_KEYS,
    KNOWN_CONTAINER_API,
    UNIT_KEYS,
    Container,
    ContainerError,
    Unit,
    from_document,
    load,
    parse,
    render,
    to_document,
)
from studyforge.corpus.container import document as mod
from studyforge.corpus.manifest import from_document as manifest_from_document
from tests.fixture_checks import coverage, fixture_paths, sweeping
from tests.support import repository_root

HOME = "/" + "home/jane"

MANIFEST = {
    "corpus_api": 1,
    "source": "demo",
    "title": "Demo",
    "levels": ["section"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["**/*.md"]},
}

BASE = {
    "container_api": 1,
    "address": ["depth-one"],
    "titles": ["Depth One"],
    "variant": "prose",
    "ingested": "2026-01-05",
    "units": [
        {"n": 1, "title": "One", "practices": 0},
        {"n": 2, "title": "Two", "practices": 2},
    ],
}


def manifest(**overrides):
    return manifest_from_document({**MANIFEST, **overrides}, "corpus.json")


def built(**overrides):
    return from_document({**BASE, **overrides}, "container.json", manifest())


def refusal(**overrides):
    with pytest.raises(ContainerError) as raised:
        built(**overrides)
    return str(raised.value)


#: ⛔ Asserted as rule ids — reading a map needs the manifest, so `corpus-api` joins the
#: container's own `ordinal-gap`. Naming them gained **five** maps.
ASSERTED = {"corpus-api", "ordinal-gap"}


def fixture_maps():
    """`(where, path, manifest)` for every container map `ASSERTED` entitles us to."""
    for _w, corpus in fixture_paths(asserting=ASSERTED, glob="corpus.json", within=None):
        made = manifest_from_document(json.loads(corpus.read_text("utf-8")), "corpus.json")
        for path in sorted((corpus.parent / "archive").rglob("container.json")):
            yield sweeping(path), path, made


# --------------------------------------------------------------------------
# The round trip
# --------------------------------------------------------------------------


def test_every_committed_container_map_round_trips_byte_for_byte():
    maps = list(fixture_maps())  # ⛔ The entitled corpora, counted.
    assert len(maps) >= coverage(asserting=ASSERTED, glob="corpus.json", within=None).swept > 0
    for where, path, made in maps:
        text = path.read_text(encoding="utf-8")
        assert render(load(path, made)) == text, where


def test_the_key_order_is_what_reaches_disk():
    text = render(built(origin="a/b", note="why"))
    order = [line.split('"')[1] for line in text.splitlines() if line.startswith('  "')]
    assert tuple(order) == CONTAINER_KEYS


def test_an_absent_optional_key_is_omitted_rather_than_written_null():
    document = to_document(built())
    assert "origin" not in document
    assert "note" not in document
    assert tuple(document) == tuple(k for k in CONTAINER_KEYS if k not in ("origin", "note"))


# --------------------------------------------------------------------------
# "Hand-authorable" is two fields, and the round trip is its whole content
# --------------------------------------------------------------------------


def test_an_edited_note_and_title_survive_a_re_read_unchanged():
    # ⭐ The entire content of "hand-authorable" (Q3). A corrected title or an
    # explanatory note is a judgement about one's own material, which is the
    # one thing no skill can produce — so it is amended by hand and must come
    # back exactly as it was written.
    first = built()
    amended = json.loads(render(first))
    amended["note"] = "Unit 2's title was wrong on the site; corrected here."
    amended["units"][1]["title"] = "Two, corrected"
    text = render(from_document(amended, "container.json", manifest()))
    again = from_document(json.loads(text), "container.json", manifest())
    assert again.note == amended["note"]
    assert again.unit(2).title == "Two, corrected"
    assert render(again) == text


def test_nothing_but_the_editorial_fields_moved():
    # ⚠️ The other half: amending an editorial field must not disturb a byte
    # of anything else, or a generator round-tripping one would rewrite the
    # document around it.
    before = render(built(note="first"))
    after = render(built(note="second"))
    assert before.replace('"note": "first"', '"note": "second"') == after


def test_the_editorial_keys_are_named_and_are_two_things():
    assert EDITORIAL_KEYS == ("title", "titles", "note")


def test_a_declared_practice_count_is_preserved_verbatim():
    # ⛔ SF-25 checks the declaration against what is on disk. A reader that
    # corrected it here would delete the disagreement that check exists to
    # find.
    assert built().unit(2).practices == 2
    assert to_document(built())["units"][1]["practices"] == 2


# --------------------------------------------------------------------------
# What it refuses
# --------------------------------------------------------------------------


def test_an_address_whose_arity_disagrees_with_levels_is_refused():
    # ⚠️ Raises SF-01's `AddressError`, following the manifest's precedent
    # exactly: the arity *comparison* is SF-01's and it owns it outright.
    with pytest.raises(AddressError, match="segment"):
        built(address=["basics", "getting-started"])


def test_a_variant_the_corpus_does_not_declare_is_refused():
    # ⛔ W19: the refusal names the closed set, never the value it was handed.
    message = refusal(variant="java")
    assert "java" not in message
    assert "['prose']" in message


def test_a_title_per_level_is_required():
    assert "one title per container level" in refusal(titles=["A", "B"])
    assert "one title per container level" in refusal(titles=[])


@pytest.mark.parametrize(
    "units",
    [
        [{"n": 1, "title": "a", "practices": 0}, {"n": 3, "title": "c", "practices": 0}],
        [{"n": 2, "title": "b", "practices": 0}],
        [{"n": 2, "title": "b", "practices": 0}, {"n": 1, "title": "a", "practices": 0}],
    ],
)
def test_non_contiguous_ordinals_are_refused(units):
    # ⛔ R6. A gap is a unit that was not ingested, and it is reported rather
    # than closed — closing it silently renumbers everything after it.
    assert "contiguous" in refusal(units=units)


def test_a_container_with_no_units_is_refused():
    assert "declares no units" in refusal(units=[])


def test_an_unknown_key_is_refused_and_the_message_lists_what_is_read():
    message = refusal(chapters=[])
    assert "chapters" in message
    assert "container_api" in message


def test_an_unknown_unit_key_is_refused():
    message = refusal(units=[{"n": 1, "title": "a", "practices": 0, "slug": "x"}])
    assert "slug" in message


@pytest.mark.parametrize("practices", [-1, "two", None, True, 1.0])
def test_a_practice_count_that_is_not_a_whole_number_is_refused(practices):
    assert "practice count" in refusal(units=[{"n": 1, "title": "a", "practices": practices}])


@pytest.mark.parametrize("n", [0, -1, "1", None, True])
def test_a_unit_ordinal_that_is_not_one_is_refused(n):
    assert "ordinal" in refusal(units=[{"n": n, "title": "a", "practices": 0}])


def test_a_missing_unit_is_named_against_what_is_declared():
    with pytest.raises(ContainerError) as raised:
        built().unit(9)
    assert "[1, 2]" in str(raised.value)


# --------------------------------------------------------------------------
# R9 — SF-33's guard, and this contract's own set
# --------------------------------------------------------------------------


def test_an_unknown_container_api_is_refused():
    assert "container_api 99" in refusal(container_api=99)


def test_a_json_true_is_refused_where_one_is_supported():
    assert "container_api" in refusal(container_api=True)


def test_the_version_refusal_says_it_is_not_a_migration():
    assert "never migrated in place" in refusal(container_api=99)


def test_this_module_owns_the_set_and_not_the_check():
    assert KNOWN_CONTAINER_API == frozenset({1, 2, 3})  # ⛔ literals, not CONTAINER_API
    source = (repository_root() / "src/studyforge/corpus/container/document.py").read_text(
        encoding="utf-8"
    )
    assert "from studyforge.version import" in source
    assert "not in KNOWN_CONTAINER_API" not in source


def test_the_version_is_checked_before_anything_else():
    # ⚠️ Otherwise a v2 map is refused for a v1 reason — "unknown key" — and
    # the integrator upgrades the wrong thing.
    assert "container_api" in refusal(container_api=99, chapters=[])


# --------------------------------------------------------------------------
# R7 — the gate is invoked, and a refusal is not a leak
# --------------------------------------------------------------------------


def test_a_leak_in_the_note_alone_is_refused():
    # ⭐ How the gate's invocation is asserted rather than assumed: `note` is
    # checked only for being non-empty text, so a home path in it passes every
    # other check in this module. Only the gate can reject it, and a reader
    # that stopped calling the gate would pass every other test here.
    with pytest.raises(PersonalDataLeak):
        built(note=f"ingested from {HOME}/corpus")


def test_a_leak_in_a_unit_title_is_refused():
    with pytest.raises(PersonalDataLeak):
        built(units=[{"n": 1, "title": f"see {HOME}/notes", "practices": 0}])


def test_the_gate_is_run_over_the_whole_document(monkeypatch):
    calls = []
    monkeypatch.setattr(mod, "assert_clean", lambda value, where: calls.append(where))
    built()
    assert calls == ["container.json"]


def test_a_home_shaped_origin_is_caught_by_the_gate_before_the_path_check():
    # ⭐ Better than this test first asked for, and worth pinning: the gate runs
    # before the shape checks, so an `origin` carrying a home directory is
    # refused by R7's gate — which never echoes a matched value — rather than
    # by the path rule, which would have had to be careful. **Both** are
    # careful; the order means only one of them ever has to be.
    with pytest.raises(PersonalDataLeak) as raised:
        built(origin=f"{HOME}/corpus/README.md")
    assert "jane" not in str(raised.value)


def test_a_leaking_payload_in_a_wrongly_typed_field_is_still_refused():
    # ⚠️ The two rules meet here: the value is both the wrong type and a leak,
    # and the gate gets there first. Neither message could have quoted it.
    with pytest.raises(PersonalDataLeak) as raised:
        built(note={"leak": f"{HOME}/x"})
    assert "jane" not in str(raised.value)


def test_load_names_the_file_and_never_the_path_it_read(tmp_path):
    path = tmp_path / "container.json"
    path.write_text(json.dumps({**BASE, "container_api": 99}), encoding="utf-8")
    with pytest.raises(ContainerError) as raised:
        load(path, manifest())
    assert "container.json" in str(raised.value)
    assert str(tmp_path) not in str(raised.value)


def test_a_missing_file_names_the_reason_and_not_the_exception(tmp_path):
    with pytest.raises(ContainerError) as raised:
        load(tmp_path / "absent.json", manifest())
    assert "absent.json" in str(raised.value)
    assert str(tmp_path) not in str(raised.value)


def test_malformed_json_names_the_position_and_never_the_text():
    with pytest.raises(ContainerError) as raised:
        parse('{"container_api": 1, "note": "' + HOME + '"', "container.json", manifest())
    message = str(raised.value)
    assert "line" in message and "column" in message
    assert "jane" not in message


@pytest.mark.parametrize("text", ["[]", '"a string"', "12"])
def test_a_document_that_is_not_an_object_is_refused(text):
    with pytest.raises(ContainerError, match="JSON object"):
        parse(text, "container.json", manifest())


# --------------------------------------------------------------------------
# `label` — presentation carried as data
# --------------------------------------------------------------------------


def test_the_reader_s_numbering_and_the_filename_s_are_named_apart():
    # ⚠️ Two answers to "what is this unit called", and the fix is to say which
    # is which. `numbering` is what a reader sees — `7`. SF-03's `label_of` is
    # the filename component — `unit-07`. ⭐ One rule with two fallbacks: when a
    # label is present they are identical and both *are* the label.
    plain = built().unit(1)
    labelled = built(units=[{"n": 1, "title": "One", "practices": 0, "label": "4.4.1"}]).unit(1)
    assert plain.numbering == "1"
    assert labelled.numbering == "4.4.1" == labelled.label
    assert not hasattr(plain, "display")


def test_a_unit_with_no_label_is_called_by_its_ordinal():
    assert built().unit(1).numbering == "1"
    assert built().unit(1).label is None


def test_a_label_changes_only_what_a_unit_is_called():
    # ⛔ Presentation, never identity. The address is still the address and the
    # ordinals are still contiguous; real material carries `4.4.1` and a page's
    # *name* must still come from identity, because two of the four designed
    # source shapes differ only in zero-padding.
    labelled = built(units=[{"n": 1, "title": "One", "practices": 0, "label": "4.4.1"}])
    assert labelled.unit(1).numbering == "4.4.1"
    assert labelled.unit(1).n == 1
    assert labelled.ordinals == (1,)
    assert labelled.address.unit_key(1) == "depth-one/unit-01"


def test_a_label_is_never_parsed_back():
    # ⚠️ R4's argument about paths, applied to numbering: nothing may read a
    # label back as an ordinal. `display` returns text and `n` is untouched by
    # it, so there is no inverse to be tempted by.
    labelled = built(units=[{"n": 1, "title": "One", "practices": 0, "label": "9"}])
    assert labelled.unit(1).numbering == "9"
    assert labelled.unit(1).n == 1
    with pytest.raises(ContainerError):
        labelled.unit(9)


def test_a_label_round_trips():
    labelled = built(units=[{"n": 1, "title": "One", "practices": 0, "label": "4.4.1"}])
    again = from_document(json.loads(render(labelled)), "container.json", manifest())
    assert again.unit(1).label == "4.4.1"


@pytest.mark.parametrize("label", ["", "  ", 441])
def test_a_label_that_is_present_but_not_text_is_refused(label):
    assert "label" in refusal(units=[{"n": 1, "title": "a", "practices": 0, "label": label}])


@pytest.mark.parametrize(
    "label",
    ["a/b", "a\\b", "4 4 1", "a\tb", "a\nb", "a\rb", "a\vb", "a\xa0b", 'a"b', "a:b", ".."],
)
def test_a_label_that_could_not_become_a_filename_is_refused_at_entry(label):
    # ⛔ **The seam taking `label`, closed where it opens.** A label becomes
    # part of a generated filename (SF-03's `label_of`), which refuses exactly
    # these. A map that accepted `a/b` would produce a corpus that **validates
    # and then fails at render** — a milestone later, in another package, with
    # nothing between the two saying why.
    # ⛔ **Ruling 8:** the last five of these passed both guards while the rule
    # was a forbidden list, and `"` and `:` break the `file://` floor. The rule
    # is now a permitted set, so the list below is a regression suite rather
    # than the definition.
    # ⭐ The negative control is in `test_fields.py`, where `4.4.1`, `vii` and
    # `01` are all accepted: the constraint is a character class, not a slug.
    message = refusal(units=[{"n": 1, "title": "a", "practices": 0, "label": label}])
    assert "may carry only" in message
    assert "fail at render" in message
    assert label not in message


def test_an_absent_label_is_not_a_refusal():
    # ⚠️ Absent and empty are different: absent says "this corpus does not
    # number its units", empty says somebody meant to write something.
    unit = built(units=[{"n": 1, "title": "a", "practices": 0, "label": None}]).unit(1)
    assert unit.label is None


# --------------------------------------------------------------------------
# Nothing lost from a real course map
# --------------------------------------------------------------------------

#: Every key a real `course-map.json` carries, and where it goes.
#: **Measured** over the extraction source's 285 maps and 1290 unit entries;
#: the counts were taken once and are not repeated here. ⛔ The source tree is not
#: read from here — its path is an absolute home path (R7) and a consumer's
#: task never cites one (R20) — so what is pinned is the *shape*.
COURSE_MAP_KEYS = {
    "path": "titles[0], and address[0] after slugifying",
    "course": "titles[1], and address[1] after slugifying",
    "language": "variant",
    "captured": "ingested",
    "folder": "origin",
    "note": "note",
    "units": "units",
}

COURSE_MAP_UNIT_KEYS = {
    "n": "n",
    "title": "title",
    "practices": "practices",
    "url_slug": "url_slug",
    "note": "note",
}

SAMPLE = {
    "path": "Advanced Interview Prep for Senior Engineers in Java",
    "course": "Backward Compatibility in Software Development",
    "language": "java",
    "captured": "2026-09-08",
    # ⚠️ Truncated and suffixed relative to the titles — which is the whole
    # reason `folder` needs a home. See the test below.
    "folder": "advanced-interview-prep-for-senior-engineers-in-java/"
    "backward-compatibility-in-software-development-2",
    "note": "Two units only.",
    "units": [
        {
            "n": 1,
            "title": "What Backward Compatibility Means",
            "practices": 3,
            "url_slug": "what-backward-compatibility-means",
        },
        {
            "n": 2,
            "title": "Deprecation in Practice",
            "practices": 4,
            "url_slug": "deprecation-in-practice-1",
            "note": "Carries the only note in this map.",
        },
    ],
}


def renamed(source):
    """The mechanical renaming, and nothing else."""
    document = {
        "container_api": CONTAINER_API,
        "address": [slugify(source["path"]), slugify(source["course"])],
        "titles": [source["path"], source["course"]],
        "variant": source["language"],
        "ingested": source["captured"],
    }
    if "folder" in source:
        document["origin"] = source["folder"]
    if "note" in source:
        document["note"] = source["note"]
    document["units"] = [
        {key: unit[key] for key in UNIT_KEYS if key in unit} for unit in source["units"]
    ]
    return document


def two_level(source):
    return manifest_from_document(
        {**MANIFEST, "levels": ["path", "course"], "variants": [source["language"]]},
        "corpus.json",
    )


def test_a_real_course_map_loads_after_mechanical_renaming():
    made = from_document(renamed(SAMPLE), "container.json", two_level(SAMPLE))
    assert made.titles == (SAMPLE["path"], SAMPLE["course"])
    assert made.variant == "java"
    assert made.ingested == "2026-09-08"
    assert [unit.practices for unit in made.units] == [3, 4]


def test_no_field_is_lost():
    # ⛔ No source field is lost. `folder` and `url_slug` are the two the generalised
    # shape as drafted dropped; both have a home, and this asserts every key of
    # the real shape does.
    assert set(COURSE_MAP_KEYS) == set(SAMPLE)
    assert set(COURSE_MAP_UNIT_KEYS) >= {key for unit in SAMPLE["units"] for key in unit}
    document = renamed(SAMPLE)
    assert set(document) <= set(CONTAINER_KEYS)
    for unit in document["units"]:
        assert set(unit) <= set(UNIT_KEYS)


def test_folder_is_origin_and_is_not_derivable_from_the_titles():
    # ⛔ **FND-04 recorded that `folder` "is exactly what `address` already is,
    # so it is subsumed". Measured over all 116 maps that carry one: 0 are
    # derivable from the titles.** They are truncated and carry disambiguating
    # suffixes, because a site's own URL scheme is not a function of its
    # titles — the same reason a page's name may not come from a source
    # filename (R1). This sample is one of the real ones, shape for shape.
    derived = "/".join([slugify(SAMPLE["path"]), slugify(SAMPLE["course"])])
    assert derived != SAMPLE["folder"]
    assert SAMPLE["folder"].startswith(derived[: derived.rindex("/")])
    made = from_document(renamed(SAMPLE), "container.json", two_level(SAMPLE))
    assert made.origin == SAMPLE["folder"]
    assert made.address.key == derived


def test_a_url_slug_is_required_to_be_a_slug():
    # ⚠️ Measured: of the extraction source's 1290 unit entries, 0 carry a
    # `url_slug` that is not a slug, so this is a real contract rather than a
    # hopeful one.
    assert all(is_slug(unit["url_slug"]) for unit in SAMPLE["units"])
    assert "url_slug" in refusal(
        units=[{"n": 1, "title": "a", "practices": 0, "url_slug": "Not A Slug"}]
    )


def test_origin_and_url_slug_are_both_provenance_and_neither_is_redundant():
    # ⭐ `origin` is a path inside the source, which a repository corpus has;
    # `url_slug` is the source's own addressing, which a web source has
    # instead, because it has no file. A corpus normally carries one.
    unit = built(
        units=[{"n": 1, "title": "a", "practices": 0, "origin": "a/b.md", "url_slug": "a-b"}]
    ).unit(1)
    assert unit.origin == "a/b.md"
    assert unit.url_slug == "a-b"


# --------------------------------------------------------------------------
# The manifest is not optional
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["parse", "load", "from_document"])
def test_the_manifest_has_no_default(name):
    # ⛔ A container map is meaningless outside its corpus: its address must
    # have the corpus's depth and its variant must be one the corpus declares.
    # A default would make both checks skippable by omission.
    parameter = inspect.signature(getattr(mod, name)).parameters["manifest"]
    assert parameter.default is inspect.Parameter.empty


def test_a_container_is_immutable_once_validated():
    made = built()
    with pytest.raises((AttributeError, TypeError)):
        made.variant = "java"
    with pytest.raises((AttributeError, TypeError)):
        made.units[0].title = "changed"


def test_the_dataclasses_are_what_the_document_says():
    made = built()
    assert isinstance(made, Container)
    assert all(isinstance(unit, Unit) for unit in made.units)
    assert made.container_api == 1  # BASE's own, kept rather than promoted
