"""Mirror of `src/studyforge/corpus/placement/profile.py` (R12).

Carries SF-03's headline acceptance: one address under both profiles yields two
correct, different location sets, and a third profile can be added without
changing any consumer.
"""

from __future__ import annotations

import ast
from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import PLACEMENT_PROFILES
from studyforge.corpus.placement import (
    GENERATED_ROOT,
    ContainerLocations,
    PlacementError,
    Profile,
    origin_directory,
    profile_for,
    register,
    registered,
)
from tests.support import repository_root

ADDRESS = Address.of("basics", "16-streams-api")
TITLE = "Introduction to the Streams API"
ORIGIN = "16-streams-api/README_4.4.1.md"


def unit(profile):
    origin = ORIGIN if profile == "sibling" else None
    return profile_for(profile).unit(ADDRESS, 7, TITLE, origin=origin)


# --- the acceptance ---------------------------------------------------------


def test_one_address_under_both_profiles_gives_two_different_location_sets():
    tree, sibling = unit("tree"), unit("sibling")
    assert tree.page != sibling.page
    assert set(tree.directories).isdisjoint(sibling.directories)


def test_both_location_sets_are_correct_and_not_merely_different():
    # ⭐ "Different" is cheap; these are the two shapes each profile promises.
    assert str(unit("tree").page).startswith(f"{GENERATED_ROOT}/basics/16-streams-api/units/")
    assert str(unit("sibling").page).startswith("16-streams-api/")


def test_a_third_profile_is_added_without_changing_any_consumer():
    class BesideTheArchive(Profile):
        name = "test-third"
        describes = "a profile invented inside a test"

        def unit(self, address, ordinal, title, *, origin=None, label=None):
            raise NotImplementedError

        def container(self, address, titles, *, origin=None):
            return ContainerLocations(page=PurePosixPath("third.section.html"))

    try:
        register(BesideTheArchive())
        assert "test-third" in registered()
        # ⛔ The consumer is unchanged: it asks by name and knows none.
        assert profile_for("test-third").container(ADDRESS, ("A",)).page.name.endswith(".html")
    finally:
        from studyforge.corpus.placement.profile import _PROFILES

        _PROFILES.pop("test-third", None)


def test_nothing_downstream_branches_on_a_profile_name():
    # ⛔ The acceptance stated the only way it can be checked: an AST scan of
    # all of `src/` for a comparison against a profile name. A registry that
    # coexists with `if placement == "tree"` somewhere is a registry that has
    # already failed.
    # ⛔ Excluded by repository-relative PATH, not by basename: a basename
    # match would skip any `tree.py` anywhere under `src/`, so the day another
    # package grows one it would leave the scan silently — which is the shape
    # of exemption this check exists to refuse.
    exempt = {
        "src/studyforge/corpus/placement/tree.py",
        "src/studyforge/corpus/placement/sibling.py",
        "src/studyforge/corpus/placement/profile.py",
    }
    root = repository_root()
    offenders = []
    for path in sorted((root / "src").rglob("*.py")):
        if path.relative_to(root).as_posix() in exempt:
            continue  # each names itself once, in `name = "..."`.
        tree = ast.parse(path.read_text("utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare) and _mentions_a_profile(node):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], "a consumer branches on a profile name: " + ", ".join(offenders)


def _mentions_a_profile(node):
    literals = [n for n in ast.walk(node) if isinstance(n, ast.Constant)]
    return any(literal.value in registered() for literal in literals)


# --- the registry -----------------------------------------------------------


def test_the_two_shipped_profiles_are_registered():
    assert registered() == ("sibling", "tree")


def test_the_registry_is_sorted_because_a_plan_prints_it():
    # ⛔ R10 forbids an output that depends on import order.
    assert list(registered()) == sorted(registered())


def test_the_registry_and_the_manifests_accepted_names_are_the_same_set():
    # ⚠️ The seam SF-02 owns the other half of, drawn deliberately: the
    # manifest lists the names a corpus MAY declare, this registry holds what
    # each one does. Different questions — a manifest must be able to refuse
    # an unknown name without importing a placement engine — but they must not
    # drift, and this is what stops them.
    assert set(registered()) == set(PLACEMENT_PROFILES)


@pytest.mark.parametrize("name", ["beside", "", None, "Tree", 1])
def test_an_unknown_profile_is_refused_naming_the_ones_there_are(name):
    with pytest.raises(PlacementError) as raised:
        profile_for(name)
    assert "sibling" in str(raised.value) and "tree" in str(raised.value)


def test_a_profile_with_no_name_is_refused():
    class Nameless(Profile):
        pass

    with pytest.raises(PlacementError, match="declares no name"):
        register(Nameless())


def test_a_name_already_taken_is_refused():
    class Impostor(Profile):
        name = "tree"

    with pytest.raises(PlacementError, match="already registered"):
        register(Impostor())


def test_a_profile_prints_as_its_declared_name():
    assert repr(profile_for("tree")) == "<placement 'tree'>"


def test_every_profile_describes_itself_in_one_line():
    # `studyforge plan` prints it, and a person choosing between them reads it.
    for name in registered():
        assert profile_for(name).describes


# --- the shared half --------------------------------------------------------


def test_the_shared_artifacts_are_in_the_same_place_under_every_profile():
    # ⚠️ The profiles differ only in where PAGES land. `sibling` exists so the
    # reader's own directories gain a page beside the file they know, not so a
    # corpus's archive is scattered through them.
    assert profile_for("tree").corpus() == profile_for("sibling").corpus()


def test_the_generated_root_sorts_out_of_the_way():
    # ⚠️ Dot-prefixed, because under `sibling` the repository's directories
    # are the material.
    assert GENERATED_ROOT.startswith(".")
    corpus = profile_for("tree").corpus()
    for path in corpus.directories:
        assert str(path).startswith(GENERATED_ROOT)


def test_the_root_index_is_the_one_index_html_and_it_is_at_the_top():
    corpus = profile_for("tree").corpus()
    assert corpus.root_index == PurePosixPath("index.html")


# --- origins ----------------------------------------------------------------


def test_an_origin_gives_the_directory_its_artifacts_sit_in():
    assert origin_directory(ORIGIN, ADDRESS) == PurePosixPath("16-streams-api")


def test_a_source_file_at_the_root_places_beside_itself_at_the_root():
    assert origin_directory("README.md", ADDRESS) == PurePosixPath(".")


@pytest.mark.parametrize("origin", [None, "", "   ", 7])
def test_a_missing_origin_is_refused_rather_than_guessed_around(origin):
    # ⛔ R6 and R3: "beside the source file" has no answer for a unit with no
    # source file, and inventing a directory puts generated output somewhere
    # the corpus owner never agreed to.
    with pytest.raises(PlacementError, match="records no usable 'origin'"):
        origin_directory(origin, ADDRESS)


@pytest.mark.parametrize("origin", ["/etc/passwd", "../outside/x.md", "a/../../b.md"])
def test_an_origin_that_escapes_the_source_root_is_refused_without_being_quoted(origin):
    # ⛔ R7: the one shape being refused here is exactly the shape that carries
    # a home directory, so the fault is described and the value is not.
    with pytest.raises(PlacementError) as raised:
        origin_directory(origin, ADDRESS)
    assert origin not in str(raised.value)
    assert "basics/16-streams-api" in str(raised.value)


# --- the ignore lines (Ruling 91) -------------------------------------------


def test_every_registered_profile_answers_with_ignore_lines():
    # ⛔ Enumerated over the registry, not over two names: a third profile that
    # placed media somewhere new and inherited a stale glob would report ignore
    # rules that ignore nothing.
    for name in registered():
        assert profile_for(name).ignore_lines(media=False)
        assert profile_for(name).media_ignore_lines()


def test_the_base_profile_refuses_to_guess_a_media_glob():
    class Bare(Profile):
        name = ""

    with pytest.raises(NotImplementedError):
        Bare().media_ignore_lines()


def test_the_shared_lines_are_spelled_from_the_names_module_and_never_retyped():
    from studyforge.corpus.placement import (
        CONTAINER_SUFFIX,
        ROOT_INDEX_FILENAME,
        SHARED_IGNORE_LINES,
        SITE_CACHE_FILENAME,
        UNIT_SUFFIX,
    )

    assert f"/{ROOT_INDEX_FILENAME}" in SHARED_IGNORE_LINES
    assert f"*{UNIT_SUFFIX}" in SHARED_IGNORE_LINES
    assert f"*{CONTAINER_SUFFIX}" in SHARED_IGNORE_LINES
    assert any(SITE_CACHE_FILENAME in line for line in SHARED_IGNORE_LINES)


def test_the_archive_is_absent_from_the_shared_lines():
    # ⛔ It is the ingested record an adapter wrote (R2), and it is the one
    # thing under the generated root a clone cannot rebuild without. That is
    # why `/.studyforge/` is not one line.
    from studyforge.corpus.placement import ARCHIVE_DIRNAME, SHARED_IGNORE_LINES

    assert not [line for line in SHARED_IGNORE_LINES if ARCHIVE_DIRNAME in line]


@pytest.mark.parametrize("name", ["tree", "sibling"])
def test_media_is_left_out_unless_it_is_asked_for(name):
    # ⭐ Generated media is committed by default (§5); the caller inverts the
    # corpus's policy and this never reads a manifest.
    profile = profile_for(name)
    media = profile.media_ignore_lines()
    assert profile.ignore_lines(media=False) == tuple(
        line for line in profile.ignore_lines(media=True) if line not in media
    )


def test_the_two_shipped_profiles_do_not_ignore_media_the_same_way():
    assert profile_for("tree").media_ignore_lines() != profile_for("sibling").media_ignore_lines()
