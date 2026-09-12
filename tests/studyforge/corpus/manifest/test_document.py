"""Mirror of `src/studyforge/corpus/manifest/document.py` (R12).

Carries three checks that are about the whole of `src/` rather than about this
module, because they are the negative half of SF-02's acceptance and
`document.py`'s contract names them: no framework module imports anything
source-specific, no framework module names a source in its code, and no
framework module derives a capability from a variant name.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

from studyforge.address import AddressError
from studyforge.corpus.manifest import (
    CORPUS_API,
    DEFAULT_MEDIA,
    MANIFEST_FILENAME,
    Classification,
    Manifest,
    ManifestError,
    from_document,
    load,
    parse,
)
from tests.fixture_checks import INVALID_CORPORA
from tests.support import repository_root

#: A manifest with every required key, in §4's order. Each test changes one
#: thing about it, so a failure names the one thing.
BASE = {
    "corpus_api": 1,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section", "module"],
    "variants": ["java"],
    "exercises": True,
    "placement": "tree",
    "content": {"include": ["*/*/README*.md"], "exclude": []},
}

#: ⭐ Spec §1's four designed shapes, counted rather than assumed. "A contract
#: that cannot express all four is wrong." ⚠️ Two of them are **one** level
#: deep, which is why depth 1 gets its own cases everywhere below rather than
#: being treated as the degenerate end of the two-level case.
SHAPES = [
    ("two levels, 168 authoritative graders", ["section", "module"], ["java"], True),
    ("two levels, dockerised, advisory tests", ["path", "course"], ["python", "kotlin"], True),
    ("one level, prose scenarios and no build file", ["group"], ["prose"], False),
    ("one level, an exercise in every lesson and no grader", ["course"], ["sparql"], True),
]


def manifest(**overrides) -> Manifest:
    """Build a manifest from `BASE` with `overrides` applied."""
    return from_document({**BASE, **overrides})


def refusal(**overrides) -> str:
    """The message this build gives for a manifest it will not accept."""
    with pytest.raises(ManifestError) as raised:
        manifest(**overrides)
    return str(raised.value)


# --- the four shapes --------------------------------------------------------


@pytest.mark.parametrize("name,levels,variants,exercises", SHAPES)
def test_every_designed_shape_is_accepted(name, levels, variants, exercises):
    built = manifest(levels=levels, variants=variants, exercises=exercises)
    assert built.levels == tuple(levels), name
    assert built.variants == tuple(variants), name
    assert built.exercises is exercises, name


@pytest.mark.parametrize("name,levels,variants,exercises", SHAPES)
def test_depth_is_the_number_of_declared_levels(name, levels, variants, exercises):
    assert manifest(levels=levels).depth == len(levels), name


def test_a_one_level_corpus_is_not_a_special_case():
    # ⭐ Half the designed shapes are one level deep, so this is the common
    # case and not the edge. A `levels` of one is a corpus, not a corpus
    # missing a level.
    solo = manifest(levels=["course"], variants=["sparql"])
    assert solo.depth == 1
    assert solo.parse_key("basics").key == "basics"


def test_exercises_is_a_declaration_and_not_a_promise_of_graders():
    # ⛔ C5's three states: the SPARQL shape carries an exercise in every
    # lesson and no grader at all, and it is complete at M4 rather than short.
    sparql = manifest(levels=["course"], variants=["sparql"], exercises=True)
    assert sparql.exercises is True
    assert sparql.variants == ("sparql",)


# --- where depth is declared, and where it is checked -----------------------


def test_parse_key_supplies_this_corpus_s_depth():
    # ⭐ The one place declaration meets comparison. A caller never writes
    # `parse_key(key, len(manifest.levels))`, so a caller never gets it wrong.
    address = manifest().parse_key("basics/01-getting-started")
    assert address.segments == ("basics", "01-getting-started")
    assert address.depth == 2


@pytest.mark.parametrize("key", ["basics", "a/b/c", "a/b/c/d"])
def test_a_key_of_the_wrong_arity_is_refused_by_sf01_and_not_by_this_module(key):
    # ⚠️ The boundary, asserted rather than described: the refusal is an
    # `AddressError`. ⛔ A second arity check here with a different message is
    # how two tasks come to disagree about which is authoritative.
    with pytest.raises(AddressError, match="the corpus declares"):
        manifest().parse_key(key)


def test_the_same_key_is_right_at_one_depth_and_wrong_at_another():
    assert manifest(levels=["course"]).parse_key("basics").key == "basics"
    with pytest.raises(AddressError):
        manifest(levels=["section", "module"]).parse_key("basics")


# --- R9: an unknown version is refused, never migrated ----------------------


@pytest.mark.parametrize("api", [0, 4, 99, "1", 1.0, None, True])
def test_an_unknown_corpus_api_is_refused(api):
    # ⚠️ `4` is where `3` used to sit, which is where `2` used to sit. ⛔ Each
    # widening of the known set moves this case up by one rather than dropping
    # it: the refusal one degree above the top of the range is the one that
    # goes quiet first.
    assert "corpus_api" in refusal(corpus_api=api)


@pytest.mark.parametrize("api", [1, 2, 3])
def test_every_version_this_build_speaks_is_accepted(api):
    # ⭐ Literal numbers, never `KNOWN_CORPUS_API`: an assertion that reads the
    # set it is meant to pin passes whatever the set becomes.
    assert manifest(corpus_api=api).corpus_api == api


def test_a_manifest_reports_the_version_it_declared_and_not_this_build_s():
    # ⛔ The field records what the corpus declared. While the known set held
    # one number this was true by coincidence, because the default and the
    # only legal value were the same number.
    assert manifest(corpus_api=1).corpus_api == 1
    assert CORPUS_API == 3


#: A `content` block using the key that `corpus_api` 2 added.
WITH_NOT_MATERIAL = {
    "include": ["*/*/README*.md"],
    "exclude": [],
    "not_material": [
        {"glob": "LICENSE", "why": "the repository's licence; it teaches nobody anything"}
    ],
}


def test_the_key_the_second_version_added_is_accepted_at_the_second_version():
    built = manifest(corpus_api=2, content=WITH_NOT_MATERIAL)
    assert built.content.classify("LICENSE") is Classification.NOT_MATERIAL


def test_the_key_the_second_version_added_is_refused_under_the_first():
    # ⛔ The version is the corpus's statement of which contract it was written
    # to, and a manifest using v2's vocabulary under a `1` is unreadable to
    # exactly the build it claims to be readable by. ⚠️ Refused, never
    # upgraded on the corpus's behalf (R9).
    message = refusal(corpus_api=1, content=WITH_NOT_MATERIAL)
    assert "not_material" in message
    assert "corpus_api 1" in message
    assert "corpus_api 2" in message


def test_a_manifest_that_declares_no_third_state_still_parses_at_the_first_version():
    # ⭐ The compatibility claim, asserted rather than assumed: the key is
    # optional, an absent one is an empty tuple, and nothing about an existing
    # manifest changed.
    built = manifest(corpus_api=1)
    assert built.content.not_material == ()
    assert built.content.classify("LICENSE") is Classification.UNCLASSIFIED


#: A `media` block using the key that `corpus_api` 3 added.
WITH_MAX_FILES = {"commit": "auto", "max_files": 20_000}


def test_the_key_the_third_version_added_is_accepted_at_the_third_version():
    assert manifest(corpus_api=3, media=WITH_MAX_FILES).media.max_files == 20_000


@pytest.mark.parametrize("api", [1, 2])
def test_the_key_the_third_version_added_is_refused_under_every_earlier_one(api):
    # ⛔ **The gate is not `content`'s alone.** It ran over one block while one
    # block was all that had grown a key; a `media` key added beside it would
    # have shipped ungated, and an older build would then have refused the
    # corpus for an "unknown key" and blamed it for the framework's age.
    message = refusal(corpus_api=api, media=WITH_MAX_FILES)
    assert "media.max_files" in message
    assert f"corpus_api {api}" in message
    assert "corpus_api 3" in message


@pytest.mark.parametrize("api", [1, 2, 3])
def test_a_manifest_that_declares_no_count_ceiling_parses_at_every_version(api):
    # ⭐ **The backward-compatibility claim, both halves.** A manifest written
    # before this key existed carries no `media` block at all, and one that
    # carries a `media` block without the key is the same answer: unbounded,
    # and equal to the default the previous build returned.
    assert manifest(corpus_api=api).media.max_files is None
    assert manifest(corpus_api=api, media={"commit": "auto"}).media == DEFAULT_MEDIA


def test_the_version_refusal_says_why_it_is_not_migrated():
    # ⛔ R9: a migration that runs because something merely wanted to render a
    # page rewrites the record of what was ingested.
    message = refusal(corpus_api=99)
    assert "never migrated in place" in message
    assert str(CORPUS_API) in message


def test_the_version_is_checked_before_anything_else_about_the_document():
    # ⚠️ Otherwise a v2 manifest is refused for a v1 reason — "unknown key
    # 'chapters'" — and the integrator upgrades the wrong thing.
    document = {"corpus_api": 99, "chapters": []}
    with pytest.raises(ManifestError, match="corpus_api"):
        from_document(document)


# --- the keys, and what each one may be -------------------------------------


@pytest.mark.parametrize("key", sorted(BASE))
def test_every_required_key_is_required(key):
    document = {name: value for name, value in BASE.items() if name != key}
    with pytest.raises(ManifestError, match="corpus_api|missing required key"):
        from_document(document)


def test_an_unknown_key_is_refused_and_the_message_lists_what_is_read():
    message = refusal(chapters=[])
    assert "chapters" in message
    assert "levels" in message


@pytest.mark.parametrize("levels", [[], None, "section", {}, [""], [7], ["  "]])
def test_a_corpus_with_no_levels_is_refused(levels):
    assert "levels" in refusal(levels=levels)


def test_levels_are_labels_and_not_slugs():
    # ⚠️ §4: `levels` supplies the display labels the breadcrumb and index
    # use. How they are capitalised is the renderer's decision (R13), so this
    # module does not constrain it.
    assert manifest(levels=["Section", "Module › Unit"]).levels == ("Section", "Module › Unit")


@pytest.mark.parametrize("variants", [[], None, "java", [""], [7], ["Java"], ["java 8"]])
def test_a_corpus_with_no_usable_variants_is_refused(variants):
    assert "variants" in refusal(variants=variants)


def test_variants_are_slugs_because_each_names_an_archive_partition():
    assert manifest(variants=["java", "python-3"]).variants == ("java", "python-3")


def test_a_variant_may_begin_with_a_digit_because_a_slug_may():
    # ⚠️ Written the other way round first, and the fixture was wrong rather
    # than the model: SF-01 accepts a leading digit in a slug and repairs it
    # only where the slug has to become a code identifier. A variant never
    # does, so `01-java` is a legal partition name.
    assert manifest(variants=["01-java"]).variants == ("01-java",)


def test_a_slug_refusal_from_sf01_arrives_as_this_package_s_error():
    # ⛔ `errors.ManifestError` promises one type from reading a manifest, and
    # a `variants` entry is checked by SF-01's rule. A caller reading
    # `corpus.json` should not have to know that.
    with pytest.raises(ManifestError, match="variants"):
        manifest(variants=["Java"])


def test_a_title_is_a_title_and_deliberately_not_a_slug():
    assert manifest(title="ISO-8583 with jPOS: A Practical Tutorial").title.startswith("ISO")


@pytest.mark.parametrize("title", ["", "   ", None, 7])
def test_a_corpus_with_no_title_is_refused(title):
    assert "title" in refusal(title=title)


@pytest.mark.parametrize("source", ["", "Example", "example corpus", None, 7])
def test_source_is_a_slug_because_it_is_an_identity(source):
    with pytest.raises(ManifestError, match="source"):
        manifest(source=source)


@pytest.mark.parametrize("placement", ["beside", "TREE", "", None, True])
def test_an_unknown_placement_profile_is_refused(placement):
    message = refusal(placement=placement)
    assert "placement" in message
    assert "tree" in message and "sibling" in message


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_each_declared_placement_profile_is_accepted(placement):
    assert manifest(placement=placement).placement == placement


@pytest.mark.parametrize("exercises", [1, 0, "true", "yes", None, []])
def test_exercises_must_be_a_real_bool(exercises):
    # ⛔ A manifest is hand-written, and a string that looks like a flag is a
    # mistake worth naming rather than coercing.
    assert "exercises" in refusal(exercises=exercises)


# --- the optional keys, and what their absence means ------------------------


def test_an_absent_media_key_means_committed_with_default_limits():
    # ⭐ SF-02's acceptance in as many words: asserted, not assumed.
    built = manifest()
    assert "media" not in BASE
    assert built.media == DEFAULT_MEDIA
    assert built.media.commits is True
    assert built.media.has_limits is True


def test_an_unknown_media_commit_mode_is_refused_through_the_document():
    assert "media.commit" in refusal(media={"commit": "sometimes"})


def test_absent_and_empty_permitted_edits_both_mean_nothing_is_declared():
    assert manifest().permitted_edits == ()
    assert manifest(permitted_edits=[]).permitted_edits == ()
    assert manifest().allows_edit_to("pom.xml") is False


def test_a_declared_edit_is_what_ops05_asks_about():
    # ⛔ `OPS-05` reads the declaration; it never hardcodes a corpus's
    # exception. The Java repo's pom line is one entry in a list.
    built = manifest(
        permitted_edits=[
            {
                "path": "pom.xml",
                "kind": "insert-line",
                "anchor": "<modules>",
                "content": "  <module>practice</module>",
                "why": "Maven compiles only what sits on a source root (spec §7).",
            }
        ]
    )
    assert built.allows_edit_to("pom.xml") is True
    assert built.allows_edit_to("README.md") is False
    assert built.permitted_edits[0].reversal.kind == "remove-line"


def test_a_permitted_edit_naming_a_forbidden_target_is_refused_by_the_document():
    # ⭐ And the third prohibition is checkable only because `content` is
    # parsed first and handed to the edits: this corpus's own policy says the
    # module READMEs are material.
    edit = {
        "path": "basics/01-getting-started/README.md",
        "kind": "insert-line",
        "anchor": "## Practice",
        "content": "See the practice module.",
        "why": "a link the generated site would like to have in the lesson text",
    }
    assert "depends on as content" in refusal(permitted_edits=[edit])


def test_content_is_reachable_from_the_manifest():
    built = manifest()
    assert built.content.classify("basics/01-x/README.md") is Classification.INCLUDED
    assert built.content.classify("pom.xml") is Classification.UNCLASSIFIED


# --- the document as text, and as a file ------------------------------------


def test_parse_reads_the_text_of_a_manifest():
    built = parse(json.dumps(BASE))
    assert built.source == "example-corpus"
    assert built.depth == 2


@pytest.mark.parametrize("text", ["", "{", "[]", "null", '"corpus"', "7"])
def test_text_that_is_not_a_manifest_object_is_refused(text):
    with pytest.raises(ManifestError, match="not valid JSON|must be a JSON object"):
        parse(text)


def test_the_refusal_names_the_file_it_was_reading():
    with pytest.raises(ManifestError, match="corpus.json"):
        parse("{", MANIFEST_FILENAME)


def test_load_reads_one_manifest_from_disk(tmp_path):
    path = tmp_path / MANIFEST_FILENAME
    path.write_text(json.dumps(BASE), encoding="utf-8")
    assert load(path).title == "Example Corpus"


def test_a_missing_manifest_is_refused_with_its_name_and_not_a_traceback(tmp_path):
    with pytest.raises(ManifestError, match="cannot read corpus.json"):
        load(tmp_path / MANIFEST_FILENAME)


def test_a_missing_manifest_refusal_carries_no_absolute_path(tmp_path):
    # ⛔ R7. A failure message ends up in a log and a bug report, and an
    # absolute path in one carries the user's home directory.
    with pytest.raises(ManifestError) as raised:
        load(tmp_path / MANIFEST_FILENAME)
    assert str(tmp_path) not in str(raised.value)


@pytest.mark.parametrize("fixture", ["depth1", "depth2"])
def test_the_shared_fixtures_parse_under_this_module(fixture):
    # ⭐ FND-04's fixtures are SF-02's test material, and the direction of
    # agreement matters: when `content` became a required key the **fixtures**
    # moved, because a manifest without one cannot say what its material is.
    built = load(repository_root() / "tests" / "fixtures" / fixture / MANIFEST_FILENAME)
    assert built.depth == (1 if fixture == "depth1" else 2)
    assert built.content.include


def test_the_depth1_fixture_declares_the_aggregate_it_withholds():
    built = load(repository_root() / "tests" / "fixtures" / "depth1" / MANIFEST_FILENAME)
    assert built.content.classify("depth-one/ALL.md") is Classification.EXCLUDED
    assert "twice" in built.content.why_excluded("depth-one/ALL.md")


#: ⛔ **The declared divergence, with its `why`** — the `personal-data-shapes.md`
#: precedent, not a fresh mechanism. Exactly one invalid corpus does *not* have
#: a readable manifest, and it says so here rather than by being absent from a
#: hand-written list.
WITHOUT_A_VALID_MANIFEST = {
    "bad-corpus-api": (
        "its corpus.json declares corpus_api 99, so `load` refuses it before "
        "depth or content can be read — which is the rule it exists to break"
    ),
}

#: FND-04's invalid fixtures whose fault is elsewhere, **derived** from the
#: declaration rather than listed.
#:
#: ⚠️ **This was a hand-written four and the tree had grown to seven.**
#: `count-mismatch` and `user-authoritative` both carry a perfectly readable
#: manifest and both landed in `INVALID_CORPORA` without reaching this list —
#: silently, exactly as `FND-09` predicted, in the second of the two places the
#: scope was not looking. ⛔ Deriving it is what makes an eighth impossible.
FIXTURES_WITH_A_VALID_MANIFEST = sorted(set(INVALID_CORPORA) - set(WITHOUT_A_VALID_MANIFEST))


def test_the_divergence_from_the_declaration_is_declared():
    # ⛔ `FND-09` acceptance 5: a deliberate divergence is legal and states its
    # `why`. ⚠️ Ruling 48's denominator too — a subtraction that removed
    # everything would parametrize nothing and look identical to a clean pass.
    assert set(WITHOUT_A_VALID_MANIFEST) < set(INVALID_CORPORA)
    assert len(FIXTURES_WITH_A_VALID_MANIFEST) == len(INVALID_CORPORA) - 1
    for name, why in WITHOUT_A_VALID_MANIFEST.items():
        assert len(why) > 60, name


@pytest.mark.parametrize("fixture", FIXTURES_WITH_A_VALID_MANIFEST)
def test_an_invalid_fixture_whose_fault_is_elsewhere_still_has_a_readable_manifest(fixture):
    # ⭐ "Exactly one rule" is the property that makes those fixtures useful,
    # and it is only true if their manifests are otherwise clean. ⚠️ They were
    # not: `content` became required and four fixtures were suddenly invalid
    # twice over. **The fixtures moved**, because a manifest that cannot say
    # what its material is has not stated a policy at all.
    built = load(repository_root() / "tests" / "fixtures" / "invalid" / fixture / MANIFEST_FILENAME)
    assert built.depth == 1


def test_the_bad_corpus_api_fixture_is_refused_for_its_version_and_nothing_else():
    path = repository_root() / "tests" / "fixtures" / "invalid" / "bad-corpus-api"
    with pytest.raises(ManifestError, match="corpus_api 99"):
        load(path / MANIFEST_FILENAME)


def test_a_manifest_is_immutable_once_validated():
    built = manifest()
    with pytest.raises((AttributeError, TypeError)):
        built.placement = "sibling"


# --- what no framework module may do (R1), over the whole of `src/` ---------

#: Tokens that name a source rather than a shape. ⚠️ Checked against
#: **identifiers**, never against prose: a docstring that names the case a
#: module was designed against is documentation, and an identifier that names
#: one is a branch.
SOURCE_TOKENS = ("codesignal", "jpos", "iso8583", "sparql", "fuseki", "jupyter")

#: A module-level name suggesting the thing the extraction source got wrong:
#: one list answering both "can this be filed here?" and "can we generate a
#: test for it?".
CAPABILITY_WORDS = ("LANGUAGE", "RUNNABLE", "GRADABLE", "BUILDABLE", "EXECUTABLE")

COLLECTION_NODES = (ast.Tuple, ast.List, ast.Set, ast.Dict)


def source_modules() -> list[Path]:
    """Every module under `src/`, which is the whole of the framework."""
    return sorted((repository_root() / "src").rglob("*.py"))


def tree_of(path: Path) -> ast.Module:
    return ast.parse(path.read_text("utf-8"), filename=path.name)


def relative(path: Path) -> str:
    """A path relative to the repository root — ⛔ never an absolute one (R7)."""
    return path.relative_to(repository_root()).as_posix()


def test_no_framework_module_imports_anything_source_specific():
    # ⛔ R1, stated the only way that is checkable: the framework imports the
    # standard library and itself, and nothing else. An adapter is on disk
    # (R2), so there is nothing for a framework module to import from one.
    allowed = set(sys.stdlib_module_names) | {"studyforge", "__future__"}
    offenders = []
    for path in source_modules():
        for node in ast.walk(tree_of(path)):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            else:
                continue
            offenders += [
                f"{relative(path)}: {name}" for name in names if name.split(".")[0] not in allowed
            ]
    assert offenders == [], "framework module imports something foreign: " + ", ".join(offenders)


def test_no_framework_module_names_a_source_in_its_code():
    offenders = []
    for path in source_modules():
        for node in ast.walk(tree_of(path)):
            name = getattr(node, "name", None) or getattr(node, "id", None)
            if not isinstance(name, str):
                continue
            offenders += [
                f"{relative(path)}: {name}"
                for token in SOURCE_TOKENS
                if token in name.lower().replace("_", "")
            ]
    assert offenders == [], "a source is named in framework code: " + ", ".join(offenders)


def test_no_module_maps_a_variant_to_a_capability():
    # ⭐ The regression test for the defect §4 records: the extraction source's
    # module-level `LANGUAGES` tuple answered both "can this be filed here?"
    # and "can we generate a test for it?", so eight SQL courses could not be
    # filed at all. ⚠️ `variants` is a filing and presentation key and nothing
    # more; runnability is declared per exercise (§7); a code fence's language
    # is a block's own attribute. Three questions, three answers.
    offenders = []
    for path in source_modules():
        for node in tree_of(path).body:
            targets = _assigned_names(node)
            value = getattr(node, "value", None)
            if not isinstance(value, COLLECTION_NODES):
                continue
            offenders += [
                f"{relative(path)}: {name}"
                for name in targets
                if any(word in name.upper() for word in CAPABILITY_WORDS)
                or "VARIANT" in name.upper()
            ]
    assert offenders == [], (
        "a module-level collection derives a capability from a variant name: "
        + ", ".join(offenders)
    )


def _assigned_names(node: ast.stmt) -> list[str]:
    """The names a module-level assignment binds, or an empty list."""
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    if isinstance(node, ast.Assign):
        return [target.id for target in node.targets if isinstance(target, ast.Name)]
    return []
