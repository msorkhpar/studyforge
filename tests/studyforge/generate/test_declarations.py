"""Mirror of `src/studyforge/generate/declarations.py` (R12)."""

from __future__ import annotations

import ast
import inspect
import shutil
from dataclasses import replace

import pytest

from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.generate import (
    BuildError,
    declared_location,
    declared_practices,
    read_corpus,
    sources,
    unit_location,
)
from tests.studyforge.generate.corpora import FIXTURES, a_corpus, with_a_unit_missing
from tests.support import repository_root

# --------------------------------------------------------------------------
# ⭐ the walk
# --------------------------------------------------------------------------


def test_every_declared_unit_with_material_is_found_in_declared_order():
    found = sources(FIXTURES / "depth1")

    assert [source.ordinal for source in found] == [1, 2, 3]
    assert [source.title for source in found] == [
        "What a triple is",
        "Reading a small graph",
        "Asking the first question",
    ]
    assert [source.directory.name for source in found] == ["unit-01", "unit-02", "unit-03"]
    assert all(source.directory.is_dir() for source in found)


def test_the_material_directory_is_the_one_the_archive_layout_names():
    """⭐ Asked of `Layout`, never composed here — the archive has one authority."""
    from studyforge.skills.adapter import Layout

    root = FIXTURES / "depth2"
    layout = Layout(root)
    for source in sources(root):
        assert source.directory == layout.unit_dir(
            source.container.address, source.container.variant, source.ordinal
        )


def test_a_declared_unit_with_no_material_is_skipped_rather_than_guessed_at(tmp_path):
    """⛔ The negative direction, with the mechanism removed rather than mocked."""
    before = [source.ordinal for source in sources(FIXTURES / "depth1")]
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")

    assert before == [1, 2, 3]
    assert [source.ordinal for source in sources(root)] == [1, 3]


def test_a_unit_directory_holding_no_document_is_skipped_too(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    for path in (root / "archive/depth-one/raw/prose/unit-03").glob("*.json"):
        path.unlink()

    assert [source.ordinal for source in sources(root)] == [1, 2]


def test_a_corpus_with_no_readable_manifest_refuses_naming_the_file(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    (root / "corpus.json").unlink()

    with pytest.raises(BuildError) as raised:
        sources(root)

    assert "corpus.json" in str(raised.value)
    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"


def test_an_unreadable_container_map_refuses_naming_the_record_and_not_the_path(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    (root / "archive/basics/01-getting-started/container.json").write_text("{", encoding="utf-8")

    with pytest.raises(BuildError) as raised:
        read_corpus(root)

    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"


# --------------------------------------------------------------------------
# ⭐ Corpus — read once, and its two sets
# --------------------------------------------------------------------------


def test_present_and_absent_partition_every_declared_unit(tmp_path):
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)

    from studyforge.contents import order

    declared = {entry.key for entry in order(corpus.contents)}
    assert len(declared) == 3
    assert corpus.absent == {"depth-one/unit-02"}
    assert corpus.present | corpus.absent == declared
    assert corpus.present & corpus.absent == frozenset()


def test_a_shipped_fixture_declares_nothing_it_has_no_material_for():
    for name in ("depth1", "depth2"):
        assert read_corpus(FIXTURES / name).absent == frozenset()


def test_the_contents_document_is_built_and_never_written(tmp_path):
    """⛔ The seam, asserted: no plan golden and no placement profile names them.

    ⚠️ `toc.json` and `status.json` are values this package hands to the shipped
    index assembler. Writing them would create two paths `studyforge plan` never
    declared — failing Ruling 99's path-for-path clause — at a location
    `CorpusLocations` does not name. ⭐ When placement grows one, this test is
    replaced by one asserting the two files are written.
    """
    from studyforge.contents import STATUS_FILENAME, TOC_FILENAME
    from studyforge.corpus.placement import CorpusLocations
    from studyforge.generate import write_site

    assert {field for field in CorpusLocations.__dataclass_fields__} == {
        "root_index",
        "assets",
        "archive",
        "site_cache",
    }, "placement now names another corpus path; check whether it is the contents"

    write_site(FIXTURES / "depth1", tmp_path)

    on_disk = {path.name for path in tmp_path.rglob("*")}
    assert TOC_FILENAME not in on_disk
    assert STATUS_FILENAME not in on_disk


# --------------------------------------------------------------------------
# ⭐ declared_practices — `exercises: false` is a declaration of ZERO
# --------------------------------------------------------------------------


def a_manifest(exercises: bool):
    document = (FIXTURES / "depth1" / "corpus.json").read_text(encoding="utf-8")
    return parse_manifest(
        document.replace('"exercises": false', f'"exercises": {str(exercises).lower()}'),
        "corpus.json",
    )


def test_a_corpus_declaring_no_exercises_declares_zero_for_every_unit():
    assert declared_practices(a_manifest(False), 0) == 0
    assert declared_practices(a_manifest(False), 3) == 0


def test_a_corpus_declaring_exercises_says_nothing_and_the_container_answers():
    assert declared_practices(a_manifest(True), 3) == 3
    assert declared_practices(a_manifest(True), 0) == 0


def test_a_prose_corpus_builds_units_that_declare_zero_rather_than_nothing(tmp_path):
    """⛔ `None` would put a *more to come* panel on every page of a finished corpus."""
    root = a_corpus(tmp_path, "depth1")
    assert {source.declared_practices for source in sources(root)} == {0}


# --------------------------------------------------------------------------
# ⚠️ A gap this package names rather than guesses at
# --------------------------------------------------------------------------


def test_an_authored_overlay_is_not_applied_because_nothing_declares_where_it_sits(tmp_path):
    """⚠️ The premise of the hole, asserted so it cannot close silently.

    `unit.content` mints `content.json` and `skills.adapter.Layout` mints every
    other archive path — but no module in `src/` says where a unit's overlay
    lives inside an archive. ⭐ The harness knows, because it was written by
    hand; the build cannot, so a unit with an overlay is built without it.

    ⛔ **When `Layout` grows that path, this test fails and is replaced by one
    asserting the section is present** — it is a marker, not a guarantee.
    """
    from studyforge.skills.adapter import Layout
    from studyforge.unit.builder import build_unit
    from tests.studyforge.render.page import pages as harness

    root = FIXTURES / "depth2"
    overlay_holder = root / "archive/basics/01-getting-started/units/unit-01/content.json"
    assert overlay_holder.is_file(), "the fixture carries an overlay"
    assert not hasattr(Layout, "content"), "Layout now names the overlay; close this gap"

    with_overlay = harness.depth2_unit_01().document
    built = next(
        source for source in sources(root) if source.container.address.key.endswith("started")
    )
    without = build_unit(built.directory, declared_practices=built.declared_practices)

    assert [section["kind"] for section in with_overlay["sections"]][0] == "shared"
    assert "shared" not in [section["kind"] for section in without["sections"]]


def test_nothing_under_tests_is_disturbed_by_a_copy(tmp_path):
    """⭐ The helper's own premise: a fixture copy is writable and separate."""
    root = a_corpus(tmp_path, "depth1")
    shutil.rmtree(root / "archive")

    assert (FIXTURES / "depth1" / "archive").is_dir()


def test_a_container_map_whose_address_is_the_wrong_depth_refuses_as_a_BuildError(tmp_path):
    """⚠️ `SF-28/1`: `corpus.container.parse` lets an `AddressError` out.

    ⛔ This package promises one exception, so it catches that one too. The
    refusal names the record and never a path (R7).
    """
    import json

    root = a_corpus(tmp_path, "depth2")
    where = "archive/basics/01-getting-started/container.json"
    document = json.loads((root / where).read_text(encoding="utf-8"))
    document["address"] = document["address"][:1]
    (root / where).write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(BuildError) as raised:
        read_corpus(root)

    assert where in str(raised.value)
    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"


@pytest.mark.parametrize("target", ["corpus.json", "container.json"])
def test_a_leak_travels_through_as_itself_and_never_as_a_BuildError(tmp_path, target):
    """⛔ Ruling 58: the tuple is caught, and its R7 member is re-raised untranslated."""
    import json

    from studyforge.archive.scrub import PersonalDataLeak

    root = a_corpus(tmp_path, "depth1")
    path = sorted(root.rglob(target))[0]
    document = json.loads(path.read_text(encoding="utf-8"))
    document["title" if target == "corpus.json" else "note"] = "/" + "home/jane/x"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(PersonalDataLeak):
        read_corpus(root)


# --------------------------------------------------------------------------
# ⛔ W290 — a placement call takes the unit WHOLE, so no call site spells a label
# --------------------------------------------------------------------------

#: ⛔ The two derivations, and how many WHOLE objects each takes. A CLOSED set
#: (`module-structure.md`): a third derivation is refused by this sweep rather
#: than admitted to the tree in silence.
DERIVATIONS = {"unit_location": 2, "declared_location": 3}

#: The package every call to one of them lives in.
FRAMEWORK = "src/studyforge"


def callee(func) -> str:
    """The name a call names, imported (`unit_location(…)`) or reached (`d.unit_location(…)`)."""
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")


def spelled_calls(source: str, where: str) -> list[str]:
    """Every call to a derivation that spells a unit's fields instead of passing it whole."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        takes = DERIVATIONS.get(callee(node.func))
        if takes is None or (len(node.args) == takes and not node.keywords):
            continue
        found.append(
            f"{where}:{node.lineno} {callee(node.func)} is called with "
            f"{len(node.args)} positional arguments and {[kw.arg for kw in node.keywords]}; "
            f"it takes {takes} whole objects"
        )
    return found


def framework_modules() -> list:
    """Every module in the framework, as `(relative path, source)`."""
    root = repository_root()
    return [
        (str(path.relative_to(root)), path.read_text(encoding="utf-8"))
        for path in sorted((root / FRAMEWORK).rglob("*.py"))
    ]


def test_the_population_this_sweep_runs_over_is_inhabited():
    # ⛔ Ruling 48: a derived-set assertion asserts inhabitation first, or a
    # package that moved makes every check below pass over nothing.
    assert framework_modules(), f"no module found under {FRAMEWORK} — did the package move?"


def test_both_derivations_are_really_called_in_the_tree():
    # ⭐ **The control, and without it this sweep rots into a green.** A sweep
    # for calls that have been renamed away passes for ever and says nothing —
    # and `declared_location` is new, so this is not hypothetical.
    called = {
        callee(node.func)
        for _path, source in framework_modules()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and callee(node.func) in DERIVATIONS
    }
    assert called == set(DERIVATIONS), called


@pytest.mark.parametrize("case", framework_modules(), ids=lambda case: case[0])
def test_W290_no_call_site_spells_a_units_arguments_out_of_it(case):
    where, source = case
    assert spelled_calls(source, where) == []


def test_W290_a_planted_call_that_drops_the_label_is_named_by_this_sweep():
    # ⛔ The other direction, and what makes the sweep above an instrument
    # rather than a wish: this is the OLD spelling with `label` dropped, which
    # is exactly what stayed writable at four call sites until this row.
    planted = (
        "at = unit_location(corpus, source.container.address, source.ordinal,\n"
        "                   source.title, origin=source.origin)\n"
    )

    named = spelled_calls(planted, "planted.py")

    assert len(named) == 1, named
    assert named[0].startswith("planted.py:1 unit_location"), named


def test_W290_a_planted_declared_call_that_drops_the_label_is_named_too():
    planted = "target = declared_location(corpus, container.address, unit.n, unit.title)\n"

    named = spelled_calls(planted, "planted.py")

    assert len(named) == 1, named
    assert "declared_location" in named[0], named


def test_W290_the_derivation_takes_the_source_whole_and_honours_its_label():
    corpus = read_corpus(FIXTURES / "depth2")
    source = corpus.units[0]

    assert list(inspect.signature(unit_location).parameters) == ["corpus", "source"]
    assert unit_location(corpus, source) == corpus.profile.unit(
        source.container.address,
        source.ordinal,
        source.title,
        origin=source.origin,
        label=source.label,
    )
    # ⚠️ The label is read off the SOURCE, so moving it there moves the unit —
    # which is the thing a call site could previously get wrong on its own.
    relabelled = replace(source, label="lab")
    assert relabelled.label != source.label, "the fixture already carries this label"
    assert unit_location(corpus, relabelled) != unit_location(corpus, source)


def test_W290_the_old_spelling_cannot_be_written_at_all():
    # ⛔ *Unwritable*, not merely RED. The five arguments a call site used to
    # compose are not parameters any more, so dropping one is a `TypeError` at
    # the call rather than a page linking beside the file the build wrote.
    corpus = read_corpus(FIXTURES / "depth2")
    source = corpus.units[0]

    with pytest.raises(TypeError):
        unit_location(
            corpus,
            source.container.address,
            source.ordinal,
            source.title,
            origin=source.origin,
        )


def test_W290_declared_location_takes_both_objects_whole_and_agrees_about_material():
    # ⭐ The two spellings are one derivation, so a unit that HAS material is
    # placed identically whether it is reached as a source or as a declaration.
    # ⛔ A disagreement here is a container page anchored beside the real page.
    corpus = read_corpus(FIXTURES / "depth2")
    assert list(inspect.signature(declared_location).parameters) == [
        "corpus",
        "container",
        "unit",
    ]

    seen = 0
    for _where, container in corpus.maps:
        for unit in container.units:
            source = next(
                (
                    item
                    for item in corpus.units
                    if item.container.address == container.address and item.ordinal == unit.n
                ),
                None,
            )
            if source is None:
                continue
            assert declared_location(corpus, container, unit) == unit_location(corpus, source)
            seen += 1
    # ⛔ Ruling 48's denominator, not `> 0`: every unit with material was
    # compared, rather than whichever one the walk reached first.
    assert seen == len(corpus.units)
