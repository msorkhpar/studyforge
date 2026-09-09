"""Placement run over whole corpora — the fixtures always, the real one when it is here.

Mirrors no source module. ⭐ It answers the acceptance clause a unit test
cannot: *no two units produce the same artifact name*, which is a property of a
corpus rather than of a call.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import load
from studyforge.corpus.placement import identity, profile_for, registered
from tests.support import repository_root

FIXTURES = ("depth1", "depth2")

#: Where sibling repositories live, as `tests/test_knowledge_index.py` finds
#: them. ⚠️ A worktree is not beside them, hence the override.
WORKSPACE_ENV = "STUDYFORGE_WORKSPACE"

#: The corpus SF-03's acceptance names by name.
JAVA_CORPUS = "Claude-senior-java-engineer"


def workspace_root() -> Path:
    override = os.environ.get(WORKSPACE_ENV)
    return Path(override).expanduser() if override else repository_root().parent


def containers(fixture):
    """`(manifest, container document)` for every container of a fixture corpus."""
    root = repository_root() / "tests" / "fixtures" / fixture
    manifest = load(root / "corpus.json")
    for path in sorted((root / "archive").rglob("container.json")):
        yield manifest, json.loads(path.read_text("utf-8"))


def placed(fixture, profile_name):
    """Every unit of a fixture corpus, placed under one profile."""
    profile = profile_for(profile_name)
    for manifest, container in containers(fixture):
        address = manifest.parse_key("/".join(container["address"]))
        for unit in container["units"]:
            yield (
                container,
                unit,
                profile.unit(address, unit["n"], unit["title"], origin=unit.get("origin")),
            )


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
    # ⭐ Placement and identity, end to end, a milestone before SF-04 needs it:
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


def java_modules():
    """`{directory: [unit source filename, ...]}` for the real Java corpus.

    ⚠️ **Unpinned evidence, and named as such.** It reads a sibling repository
    that may not be checked out; when it is not, the synthetic stand-in below
    still proves the property. ⛔ R3: read-only, and nothing is written there.
    """
    root = workspace_root() / JAVA_CORPUS
    if not root.is_dir():
        return {}
    found = {}
    for module in sorted(path for path in root.iterdir() if path.is_dir()):
        units = sorted(p.name for p in module.glob("README_*.md"))
        if units:
            found[module.name] = units
    return found


def shape_to_place():
    """The Java corpus's real shape, or a stand-in of the same shape.

    ⭐ Never a skip. The property under test — no two units in a corpus of this
    size and shape collide — is provable without the repository, and the
    repository only makes the evidence *this* corpus's rather than one like it.
    """
    real = java_modules()
    if real:
        return real, "measured"
    return {f"{n:02d}-module": [f"README_{n}.{u}.md" for u in range(1, 6)] for n in range(1, 49)}, (
        "synthetic"
    )


def test_no_two_units_in_the_java_corpus_produce_the_same_artifact_name():
    modules, provenance = shape_to_place()
    assert modules, "no shape to place"
    profile = profile_for("sibling")
    paths = []
    for module, units in modules.items():
        address = Address.of("basics", module)
        for ordinal, filename in enumerate(units, start=1):
            title = re.sub(r"[^A-Za-z0-9]+", " ", Path(filename).stem).strip()
            where = profile.unit(
                address, ordinal, title or f"unit {ordinal}", origin=f"{module}/{filename}"
            )
            paths += [where.page, *where.directories]
    duplicates = sorted({str(p) for p in paths if paths.count(p) > 1})
    assert duplicates == [], f"{provenance} shape collides: {duplicates}"
    assert len(paths) >= 200, f"{provenance} shape placed only {len(paths)} paths"
