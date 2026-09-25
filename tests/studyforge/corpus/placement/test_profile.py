"""Mirror of `src/studyforge/corpus/placement/profile.py` (R12).

Carries placement's headline acceptance: one address under both profiles yields two
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
    CACHE_IGNORE_LINES,
    GENERATED_IGNORE_HOME,
    GENERATED_ROOT,
    SELF_IGNORE_LINE,
    SITE_CACHE_FILENAME,
    UNIT_MEDIA_DIRNAMES,
    ContainerLocations,
    PlacementError,
    Profile,
    TreeProfile,
    origin_directory,
    profile_for,
    register,
    registered,
)
from studyforge.corpus.placement.names import UNCOMMITTED_DIRNAMES
from tests.support import init_repository, is_ignored, repository_root

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
    # ⚠️ The seam the manifest owns the other half of, drawn deliberately: the
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
    from studyforge.corpus.placement import ARCHIVE_DIRNAME

    corpus = profile_for("tree").corpus()
    assert str(corpus.assets).startswith(GENERATED_ROOT)
    # ⛔ The archive is the one exception, and it is ruled: it sits at
    # `ARCHIVE_DIRNAME` beside `corpus.json`, where `validate` reads it.
    assert corpus.archive == PurePosixPath(ARCHIVE_DIRNAME)


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


# --- the ignore file and the committed output -------------

#: Paths no generated rule may ignore, at the root and below it: pages, the root
#: index, the bundle, a JSON document and the archive.
#: ⛔ §5's reading floor, as data a git answer is asked about.
#: ⚠️ **The discovery cache is on `ALWAYS_IGNORED` instead**, because nothing
#: reads it: `assemble` scans on
#: every call and returns the scan, so a clone carrying the cache gains
#: nothing, while every reader who serves the corpus gets a modified file.
NEVER_IGNORED = (
    "index.html",
    "a.unit.html",
    "d/e/a.unit.html",
    "d/a.section.html",
    f"{GENERATED_ROOT}/assets/page.css",
    f"{GENERATED_ROOT}/d/units/unit-01/a.unit.html",
    "d/x.json",
    "archive/d/container.json",
)

#: ⛔ What every generated ignore file covers, whatever the media
#: policy says — the cache this framework writes into a corpus by serving it,
#: and the name it is staged under.
ALWAYS_IGNORED = (
    f"{GENERATED_ROOT}/{SITE_CACHE_FILENAME}",
    f"{GENERATED_ROOT}/{SITE_CACHE_FILENAME}.writing",
)


def test_every_registered_profile_answers_each_ignore_question():
    # ⛔ Enumerated over the registry, not over two names: a third profile that
    # placed media somewhere new and inherited a stale glob would report ignore
    # rules that ignore nothing.
    for name in registered():
        profile = profile_for(name)
        assert profile.media_ignore_lines()
        assert profile.ignore_home() is None or isinstance(profile.ignore_home(), PurePosixPath)


@pytest.mark.parametrize("question", ["media_ignore_lines", "ignore_home"])
def test_the_base_profile_refuses_to_guess(question):
    class Bare(Profile):
        name = ""

    with pytest.raises(NotImplementedError):
        getattr(Bare(), question)()


@pytest.mark.parametrize("name", registered())
def test_with_media_committed_the_only_rules_are_the_frameworks_own_caches(name):
    # ⛔ Pages, the root index and the bundle are what a clone
    # reads, so no rule about the CORPUS is written when media is committed.
    # ⭐ The framework's own cache is the exception, and the file that
    # carries nothing else hides itself, because it is this machine's own.
    assert profile_for(name).ignore_lines(media=False) == ()
    wanted = profile_for(name).ignore_file(media=False)
    assert wanted.home == GENERATED_IGNORE_HOME
    assert wanted.lines == (*CACHE_IGNORE_LINES, SELF_IGNORE_LINE)


@pytest.mark.parametrize("name", registered())
def test_a_file_that_also_carries_the_media_policy_does_not_hide_itself(name):
    # ⛔ The half that is easy to get wrong: a
    # clone has to READ the media rules, so that file is committed — while a
    # file holding only machine-local rules must never be. Asked of every
    # profile that has a home for media rules at all.
    if profile_for(name).ignore_home() is None:
        pytest.skip(f"{name} has no home for media rules, which its own test covers")
    wanted = profile_for(name).ignore_file(media=True)
    assert wanted.lines[: len(CACHE_IGNORE_LINES)] == CACHE_IGNORE_LINES
    assert SELF_IGNORE_LINE not in wanted.lines


@pytest.mark.parametrize("name", registered())
def test_every_profiles_ignore_file_covers_the_cache_this_framework_writes(name, tmp_path):
    # ⭐ Asked of git rather than of a reviewer, and in both media
    # policies: a reader who serves a corpus must not have to add a line.
    for media in (False, True):
        if media and profile_for(name).ignore_home() is None:
            continue
        wanted = profile_for(name).ignore_file(media=media)
        repository = init_repository(tmp_path / f"{name}-{media}")
        home = repository / wanted.home
        home.parent.mkdir(parents=True, exist_ok=True)
        home.write_text(wanted.text(), encoding="utf-8")
        missed = [path for path in ALWAYS_IGNORED if not is_ignored(path, cwd=repository)]
        assert missed == [], f"{name} with media={media} leaves {missed} unignored"


def test_an_ignore_home_is_inside_the_generated_root_and_never_the_repository_root():
    homes = [profile_for(name).ignore_home() for name in registered()]
    assert [home for home in homes if home is not None], "no profile has a home to check"
    for home in homes:
        assert home is None or (len(home.parts) >= 2 and home.parts[0] == GENERATED_ROOT)


def test_a_profile_answering_the_root_ignore_file_as_its_home_is_refused():
    # ⛔ R3, structurally: the guard does not trust a profile's own answer.
    class Rooted(TreeProfile):
        name = "rooted"

        def ignore_home(self):
            return PurePosixPath(".gitignore")

    with pytest.raises(PlacementError):
        Rooted().ignore_file(media=True)


def test_sibling_media_that_is_not_committed_has_no_home_and_is_refused():
    with pytest.raises(PlacementError) as raised:
        profile_for("sibling").ignore_file(media=True)
    assert "is never edited" in str(raised.value)


@pytest.mark.parametrize("name", registered())
def test_no_rule_a_profile_writes_ignores_a_page_json_or_the_archive(name, tmp_path):
    """§5's reading floor, asked of git rather than of a reviewer."""
    wanted = profile_for(name).ignore_file(media=True) if profile_for(name).ignore_home() else None
    repository = init_repository(tmp_path / name)
    if wanted is not None:
        home = repository / wanted.home
        home.parent.mkdir(parents=True, exist_ok=True)
        home.write_text(wanted.text(), encoding="utf-8")
        # ⭐ The control: these rules do ignore something, so a clean answer
        # below is a measurement rather than an empty file.
        clip = profile_for(name).unit(ADDRESS, 1, TITLE, origin=ORIGIN).audio / "c.mp3"
        assert is_ignored(clip.as_posix(), cwd=repository)
    assert [path for path in NEVER_IGNORED if is_ignored(path, cwd=repository)] == []


def test_the_two_shipped_profiles_do_not_ignore_media_the_same_way():
    assert profile_for("tree").media_ignore_lines() != profile_for("sibling").media_ignore_lines()


@pytest.mark.parametrize("name", registered())
def test_media_never_ignores_the_clips_and_no_other_media_kind(name, tmp_path):
    """⛔ `media.commit: never` keeps the clips out of git, and nothing a clone reads.

    ⭐ Asked of git, one file per kind in the unit's own directories. Images,
    video and attachments are copies of files the archive commits, and a
    committed page reaches for them. ⚠️ A profile with no home for the rules
    (`sibling`) never writes them, so there is nothing of its to ask git.
    """
    profile = profile_for(name)
    if profile.ignore_home() is None:
        pytest.skip(f"{name} has no home for media rules, which its own test covers")
    repository = init_repository(tmp_path / name)
    wanted = profile.ignore_file(media=True)
    home = repository / wanted.home
    home.parent.mkdir(parents=True, exist_ok=True)
    home.write_text(wanted.text(), encoding="utf-8")
    at = profile.unit(ADDRESS, 1, TITLE, origin=ORIGIN)
    ignored = {
        kind
        for kind in UNIT_MEDIA_DIRNAMES
        if is_ignored((at.media_dir(kind) / "f.bin").as_posix(), cwd=repository)
    }
    assert ignored == set(UNCOMMITTED_DIRNAMES) == {"audio"}
