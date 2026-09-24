"""Placement run over whole corpora — the fixtures always, the real one when it is here.

Mirrors no source module. ⭐ It answers the acceptance clause a unit test
cannot: *no two units produce the same artifact name*, which is a property of a
corpus rather than of a call.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.corpus.container.fields import optional_origin
from studyforge.corpus.manifest import load
from studyforge.corpus.placement import identity, profile_for, registered
from tests.fixture_checks import FIXTURES as FIXTURE_ROOT
from tests.fixture_checks import fixture_paths

# ⭐ **The one resolver, imported rather than re-derived**: a sibling checkout is
# found through `STUDYFORGE_WORKSPACE` and nothing else.
from tests.harness.workspace import WORKSPACE_ENV, sibling
from tests.support import repository_root

#: ⛔ **What this module's sweeps assert, as a rule id**, never a directory. Placing a
#: corpus reads its manifest first, and `corpus-api` is the one rule that
#: refuses before any unit can be placed. ⚠️ Nothing else here is a property an
#: invalid fixture declares: an address that disagrees with its directory still
#: places, and so does a container with a gap in its ordinals — which is the
#: whole reason a sweep excludes by declaration and not by directory.
ASSERTED = {"corpus-api"}

#: Every fixture corpus this module is entitled to place. ⛔ A list such as
#: `("depth1", "depth2")` would drop five corpora that place perfectly and
#: break something this module never asserts.
FIXTURES = tuple(
    path.parent.relative_to(FIXTURE_ROOT).as_posix()
    for _where, path in fixture_paths(asserting=ASSERTED, glob="corpus.json", within=None)
)


def test_the_fixture_set_is_read_from_the_declaration():
    # ⛔ The denominator: a walk that matched nothing would parametrize zero tests
    # and every sweep below would pass by never running.
    assert len(FIXTURES) >= 8, FIXTURES
    assert "depth1" in FIXTURES and "depth2" in FIXTURES
    assert "shared-origin" in FIXTURES
    assert "invalid/bad-corpus-api" not in FIXTURES


#: The corpus placement's acceptance names by name.
JAVA_CORPUS = "Claude-senior-java-engineer"


def containers(fixture):
    """`(manifest, container document)` for every container of a fixture corpus."""
    root = repository_root() / "tests" / "fixtures" / fixture
    manifest = load(root / "corpus.json")
    for path in sorted((root / "archive").rglob("container.json")):
        yield manifest, json.loads(path.read_text("utf-8"))


def placed(fixture, profile_name):
    """Every unit of a fixture corpus, placed under one profile.

    ⛔ **`origin` is read through the map's own reader, never taken raw.** It
    carries two shapes — a path for a whole file, `{path, section}`
    for a unit that is a *region* of a shared one — and placement wants the
    path in both cases. ⚠️ `unit["origin"]` was a second reader of a field that
    has one, and it handed `sibling` a dict the moment a fixture declared the
    region shape: `PlacementError`, on a corpus that places perfectly.
    """
    profile = profile_for(profile_name)
    for manifest, container in containers(fixture):
        address = manifest.parse_key("/".join(container["address"]))
        for unit in container["units"]:
            origin, _section = optional_origin(
                unit.get("origin"), f"unit {unit['n']} origin", fixture
            )
            yield (container, unit, profile.unit(address, unit["n"], unit["title"], origin=origin))


@pytest.mark.parametrize("profile", registered())
@pytest.mark.parametrize("fixture", FIXTURES)
def test_every_unit_of_every_fixture_corpus_places(fixture, profile):
    units = list(placed(fixture, profile))
    assert units, f"{fixture} placed nothing"
    for _container, _unit, where in units:
        assert where.page.name.endswith(".unit.html")
        assert not where.page.is_absolute()


@pytest.mark.parametrize("profile", registered())
@pytest.mark.parametrize("fixture", FIXTURES)
def test_no_two_artifacts_in_a_corpus_share_a_path(fixture, profile):
    # ⭐ The acceptance clause. Every path a build would write, across the
    # whole corpus, compared as a set.
    paths = []
    for _container, _unit, where in placed(fixture, profile):
        paths += [where.page, *where.directories]
    duplicates = sorted({str(p) for p in paths if paths.count(p) > 1})
    assert duplicates == [], f"{fixture}/{profile} would write to one path twice: {duplicates}"


@pytest.mark.parametrize("fixture", FIXTURES)
def test_the_two_profiles_disagree_about_every_page_in_a_real_corpus(fixture):
    tree = {str(w.page) for _c, _u, w in placed(fixture, "tree")}
    sibling = {str(w.page) for _c, _u, w in placed(fixture, "sibling")}
    assert tree and sibling
    assert tree.isdisjoint(sibling)


@pytest.mark.parametrize("fixture", FIXTURES)
def test_every_placed_unit_can_stamp_and_recover_its_own_identity(fixture):
    # ⭐ Placement and identity, end to end, a milestone before discovery needs it:
    # a page written anywhere reads back as the unit it is.
    for manifest, container in containers(fixture):
        address = manifest.parse_key("/".join(container["address"]))
        for unit in container["units"]:
            stamped = identity.Identity(
                corpus=manifest.source,
                address=address,
                variant=container["variant"],
                unit=unit["n"],
            )
            html = "<html><head>" + identity.render(stamped) + "</head></html>"
            assert identity.parse(html, manifest.depth) == stamped


# --- the corpus the acceptance names ---------------------------------------


#: The stand-in's shape, as two numbers rather than two literals buried in a
#: comprehension. ⚠️ A `48 × 5` grid is exactly the shape that makes a
#: uniqueness claim easy, which is why the case that places it says
#: `synthetic` in its own name.
SYNTHETIC_MODULES = 48
SYNTHETIC_UNITS_PER_MODULE = 5

#: The floor every placed shape must clear, so a sweep that placed almost
#: nothing cannot pass by never running.
MINIMUM_PATHS = 200


def java_modules():
    """`{directory: [unit source filename, ...]}` for the real Java corpus, or `{}`.

    ⚠️ **Unpinned evidence, and named as such.** It reads a sibling repository
    that may not be checked out. ⛔ **`{}` is the ABSENCE and nothing else** —
    no caller of this may turn it into a stand-in without saying so.
    ⛔ R3: read-only, and nothing is written there.
    """
    root = sibling(JAVA_CORPUS)
    if root is None:
        return {}
    found = {}
    for module in sorted(path for path in root.iterdir() if path.is_dir()):
        units = sorted(p.name for p in module.glob("README_*.md"))
        if units:
            found[module.name] = units
    return found


def the_java_corpus_or_skip():
    """The real corpus's shape, or a SKIP THAT SAYS SO.

    ⛔ **Never a silent stand-in.** Answering the absence with a synthetic grid
    and a `provenance` string read only inside an assertion message, which
    fires on red, would discharge on green a clause naming *the Java corpus*
    with a `48 × 5` grid that no instrument reports. ⭐ A caller may not pass
    silently on a stand-in it did not ask for: the absence skips, and the skip
    is admissible because it SAYS SO.
    """
    modules = java_modules()
    if not modules:
        pytest.skip(
            f"{JAVA_CORPUS} is not checked out in a workspace {WORKSPACE_ENV} names, so "
            f"this clause is proved of no corpus here; the synthetic stand-in of the "
            f"same shape is placed by its own case, which says it is synthetic"
        )
    return modules


def synthetic_modules():
    """A stand-in of roughly the Java corpus's shape, KEPT and NAMED.

    ⭐ **The stand-in is the right thing to have**:
    a caller must be able to tell the reader which shape it placed, so the
    grid has a name that reports itself.
    """
    return {
        f"{n:02d}-module": [f"README_{n}.{u}.md" for u in range(1, SYNTHETIC_UNITS_PER_MODULE + 1)]
        for n in range(1, SYNTHETIC_MODULES + 1)
    }


def place_one(module, filename, ordinal):
    """Every path a `sibling` build would write for one unit of one module."""
    profile = profile_for("sibling")
    address = Address.of("basics", module)
    title = re.sub(r"[^A-Za-z0-9]+", " ", Path(filename).stem).strip()
    where = profile.unit(
        address, ordinal, title or f"unit {ordinal}", origin=f"{module}/{filename}"
    )
    return [where.page, *where.directories]


def artifact_paths(modules):
    """Every path a `sibling` build would write for `{module: [filename, ...]}`."""
    paths = []
    for module, units in modules.items():
        for ordinal, filename in enumerate(units, start=1):
            paths += place_one(module, filename, ordinal)
    return paths


def collisions(paths):
    """Every path the shape would write TWICE, as strings, sorted (R10)."""
    return sorted({str(p) for p in paths if paths.count(p) > 1})


def shape_of(modules):
    """`(modules, units)` — the two numbers that say which corpus was placed."""
    return len(modules), sum(len(units) for units in modules.values())


def test_no_two_units_in_the_java_corpus_produce_the_same_artifact_name():
    # ⭐ The clause placement's acceptance names BY NAME, and it is proved of
    # that corpus or of nothing — never of a grid standing in for it.
    modules = the_java_corpus_or_skip()
    paths = artifact_paths(modules)
    assert collisions(paths) == [], f"{JAVA_CORPUS} would write to one path twice"
    assert len(paths) >= MINIMUM_PATHS, f"{JAVA_CORPUS} placed only {len(paths)} paths"


def test_no_two_units_in_the_synthetic_stand_in_of_the_same_shape_collide():
    # ⚠️ Its own case, and its name carries its provenance: this proves the
    # property of a corpus LIKE the one the acceptance names, which is worth
    # having and is not the same claim.
    paths = artifact_paths(synthetic_modules())
    assert collisions(paths) == [], "the synthetic stand-in would write to one path twice"
    assert len(paths) >= MINIMUM_PATHS, f"the stand-in placed only {len(paths)} paths"


def test_the_java_corpus_and_the_synthetic_stand_in_are_not_the_same_shape():
    """⛔ The reason the substitution mattered, asserted rather than asserted of.

    ⚠️ A stand-in that happened to be the same shape would make the old silent
    substitution harmless. It is not: the grid is wider and much deeper than
    the corpus it stood in for, and a uniqueness claim is easiest in exactly
    that shape.
    """
    real = shape_of(the_java_corpus_or_skip())
    stand_in = shape_of(synthetic_modules())
    assert real != stand_in, f"the two shapes agree at {real}, so the stand-in proved the claim"
    assert real[0] < stand_in[0], f"modules: corpus {real[0]}, stand-in {stand_in[0]}"
    assert real[1] < stand_in[1], f"units: corpus {real[1]}, stand-in {stand_in[1]}"


#: Two source filenames one module can carry side by side whose stems slugify
#: to ONE name. ⚠️ Not invented: `README_1.1.1.md` is the corpus's own
#: spelling, and the second differs from it only where `slugify` does not look.
COLLIDING_SOURCES = ("README_1.1.1.md", "README_1-1-1.md")

#: A module name the corpus actually carries, used by the controls below.
A_MODULE = "01-java-basics"


def test_the_collision_check_goes_red_when_two_units_genuinely_collide():
    """⭐ The control is seen to FIND and to REFUSE, in one test.

    ⛔ Without this the clause above is a green with no red behind it.
    """
    one, two = COLLIDING_SOURCES
    together = place_one(A_MODULE, one, 1) + place_one(A_MODULE, two, 1)
    assert collisions(together), "the check cannot go red, so its green says nothing"
    apart = place_one(A_MODULE, one, 1) + place_one(A_MODULE, two, 2)
    assert collisions(apart) == [], "the check fires on a shape that does not collide"


def test_the_sweeps_positional_ordinal_is_what_separates_those_two_and_not_the_corpus():
    """⚠️ A limit of this sweep, recorded here rather than discovered later.

    ⛔ **This sweep numbers a module's units by POSITION**, so within a module
    every unit gets a distinct ordinal and a collision is unrepresentable
    whatever the material says — while a real build numbers them from the
    archive's own `unit["n"]`, which two units CAN share. ⭐ So the green above
    is a property of this harness's numbering as much as of the corpus, and the
    day the numbering becomes the corpus's own, this test goes red and points
    at the finding instead of the change silently meaning more than it says.
    """
    assert collisions(artifact_paths({A_MODULE: list(COLLIDING_SOURCES)})) == []
