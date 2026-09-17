"""Mirror of `src/studyforge/cli/plan/derive.py` (R12).

⛔ **The acceptance clauses live here**, because they are all claims about what
a plan derived from a real corpus says.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import PurePosixPath

import pytest

from studyforge.cli.plan import UNPROJECTED, plan_for
from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import COMMIT_MODES, MANIFEST_FILENAME
from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.corpus.placement import (
    GENERATED_ROOT,
    SITE_CACHE_FILENAME,
    UNIT_MEDIA_DIRNAMES,
    profile_for,
)
from studyforge.validate.report import INVALID, OK
from tests.emission import POISON
from tests.fixture_checks import FIXTURES, VALID
from tests.support import init_repository, is_ignored, repository_root


def copy_fixture(name: str, tmp_path):
    """A throwaway copy of one FND-04 corpus, so a test may edit its manifest."""
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


def independent_paths(root) -> list[str]:
    """Every path a build must write, enumerated **without** `plan`.

    ⛔ **Deliberately a second derivation and not a second call.** It reads the
    same declarations and asks the same placement contract — which is the
    contract under test and cannot be avoided — but it walks, counts and
    assembles by its own route, so a defect in `derive`'s collection, sorting
    or de-duplication shows up as a difference rather than being reproduced on
    both sides.
    """
    from studyforge.corpus.container import parse as parse_container
    from studyforge.corpus.manifest import parse as parse_manifest

    manifest = parse_manifest((root / MANIFEST_FILENAME).read_text("utf-8"), MANIFEST_FILENAME)
    profile = profile_for(manifest.placement)
    where = profile.corpus()
    found = [
        where.root_index.as_posix(),
        f"{where.assets.as_posix()}/",
        f"{where.archive.as_posix()}/",
        where.site_cache.as_posix(),
    ]
    for path in sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME)):
        container = parse_container(path.read_text("utf-8"), path.name, manifest)
        found.append(
            profile.container(
                container.address, container.titles, origin=container.origin
            ).page.as_posix()
        )
        for unit in container.units:
            at = profile.unit(
                container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
            )
            found.append(at.page.as_posix())
            found += [f"{at.media_dir(kind).as_posix()}/" for kind in UNIT_MEDIA_DIRNAMES]
    return sorted(found)


# --------------------------------------------------------------------------
# ⛔ path for path, for both FND-04 fixtures
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_the_plan_names_every_path_a_build_must_write_and_no_other(name):
    assert list(plan_for(FIXTURES / name).paths) == independent_paths(FIXTURES / name)


@pytest.mark.parametrize("name", VALID)
def test_the_arithmetic_is_one_page_per_container_and_five_paths_per_unit(name):
    """The counting check, which shares no code with either derivation.

    ⭐ One container page each, one page plus four media directories per unit,
    plus the four a corpus gets once. A build that wrote a different number of
    things would have to disagree with this and not merely with the sort order.
    """
    root = FIXTURES / name
    maps = sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))
    units = sum(len(json.loads(path.read_text("utf-8"))["units"]) for path in maps)
    assert len(plan_for(root).paths) == 4 + len(maps) + units * (1 + len(UNIT_MEDIA_DIRNAMES))


@pytest.mark.parametrize("name", VALID)
def test_both_fixtures_plan_cleanly(name):
    plan = plan_for(FIXTURES / name)
    assert plan.refusals == ()
    assert plan.exit_code == OK


@pytest.mark.parametrize("name", VALID)
def test_the_paths_are_sorted_and_relative_to_the_corpus_root(name):
    # ⛔ R10, and R7: an absolute path in a plan is a home directory in
    # whatever the plan gets pasted into.
    paths = plan_for(FIXTURES / name).paths
    assert list(paths) == sorted(paths)
    assert not [p for p in paths if p.startswith("/") or p.startswith("~") or ".." in p]


# --------------------------------------------------------------------------
# ⛔ it reads the manifest, never the filesystem it is describing
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_it_opens_only_the_manifest_and_the_container_maps(name, monkeypatch):
    """Every file the run actually opened, recorded at `Path.read_text`.

    ⛔ **Not `Plan.read_files`, which is the module's own claim about itself.**
    A dry-run that scanned first would report what is there rather than what is
    coming, and the two differ precisely in the case that matters — the first
    run — so the claim is checked against the calls rather than trusted.
    """
    import pathlib

    opened: list[str] = []
    original = pathlib.Path.read_text

    def record(self, *args, **kwargs):
        opened.append(self.name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", record)
    plan_for(FIXTURES / name)
    assert set(opened) <= {MANIFEST_FILENAME, CONTAINER_FILENAME}


@pytest.mark.parametrize("name", VALID)
def test_read_files_is_the_exact_list_and_agrees_with_the_container_count(name):
    root = FIXTURES / name
    maps = sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))
    read = plan_for(root).read_files
    assert read[0] == MANIFEST_FILENAME
    assert len(read) == 1 + len(maps)
    assert all(entry.endswith(CONTAINER_FILENAME) for entry in read[1:])


@pytest.mark.parametrize("name", VALID)
def test_it_runs_on_a_repository_with_no_generated_output_present(name, tmp_path):
    """⭐ The case the whole contract is for, asserted in both directions."""
    root = copy_fixture(name, tmp_path)
    plan = plan_for(root)
    assert plan.exit_code == OK
    assert plan.paths
    # Nothing it names exists before the run, and nothing exists after it —
    # ⛔ except the archive, which an adapter wrote (R2) and this plan read. Until
    # `INT-06/6` this passed on the archive because the plan named a root nothing wrote.
    archive = f"{ARCHIVE_DIR}/"
    assert archive in plan.paths and (root / archive).is_dir()
    for path in plan.paths:
        if path != archive:
            assert not (root / path).exists(), path


# --------------------------------------------------------------------------
# ⛔ R3: an edit exists only where the manifest declares it
# --------------------------------------------------------------------------


def test_the_corpus_that_declares_no_edit_plans_none():
    assert plan_for(FIXTURES / "depth1").edits == ()


def test_the_declared_edit_is_named_with_its_reason():
    edit = plan_for(FIXTURES / "depth2").edits[0]
    assert edit.path == "pom.xml"
    assert len(edit.why) >= 20


def test_adding_a_permitted_edit_changes_the_plan_and_nothing_else(tmp_path):
    root = copy_fixture("depth1", tmp_path)
    before = plan_for(root)
    manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
    manifest["permitted_edits"] = [
        {
            "path": "Makefile",
            "kind": "insert-line",
            "anchor": "all:",
            "content": "\tstudyforge build .",
            "why": "so the site is rebuilt by the build everybody already runs.",
        }
    ]
    (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    after = plan_for(root)
    assert after.paths == before.paths
    assert after.ignore == before.ignore
    assert after.media == before.media
    assert len(after.edits) == 1 and before.edits == ()
    assert [line for line in after.lines() if line.startswith("edit ")]


# --------------------------------------------------------------------------
# ⛔ nothing raises; everything that goes wrong is a refusal
# --------------------------------------------------------------------------


def test_a_corpus_with_no_manifest_refuses_rather_than_planning_nothing(tmp_path):
    # ⛔ An empty `create` list would mean "this build writes nothing into your
    # repository", which is a claim, and it is one this run cannot make.
    plan = plan_for(tmp_path)
    assert plan.creations == ()
    assert plan.exit_code == INVALID
    assert len(plan.refusals) == 1


def test_a_manifest_carrying_personal_data_is_refused_before_any_line_is_printed(tmp_path):
    """R7's gate is why this command may print a corpus's own text at all.

    ⛔ The plan prints `title`, `why` and an edit's inserted line verbatim,
    where `describe` would refuse to. That is sound only because the manifest
    reader gates the whole decoded document first — so this asserts the gate,
    not the printer.
    """
    root = tmp_path / "leak"
    root.mkdir()
    (root / MANIFEST_FILENAME).write_text(
        (FIXTURES / "invalid" / "personal-data" / MANIFEST_FILENAME)
        .read_text("utf-8")
        .replace('"Invalid Demo"', f'"{POISON}"'),
        encoding="utf-8",
    )
    plan = plan_for(root)
    assert plan.exit_code == INVALID
    assert POISON not in "\n".join(plan.lines())


def test_an_unparseable_manifest_is_one_refusal_and_no_plan(tmp_path):
    (tmp_path / MANIFEST_FILENAME).write_text("{not json", encoding="utf-8")
    plan = plan_for(tmp_path)
    assert plan.exit_code == INVALID
    assert plan.paths == ()


def test_a_container_map_that_will_not_parse_is_a_refusal_and_the_rest_still_plans(tmp_path):
    root = copy_fixture("depth2", tmp_path)
    broken = sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))[0]
    broken.write_text("{not json", encoding="utf-8")
    plan = plan_for(root)
    assert plan.exit_code == INVALID
    assert len(plan.refusals) == 1
    # ⭐ Drained, not stopped: the other container is still planned, because an
    # integrator fixing one problem per run stops using the tool.
    assert [p for p in plan.paths if p.startswith("basics/")]


def test_a_sibling_unit_with_no_origin_is_refused_and_named(tmp_path):
    root = copy_fixture("depth2", tmp_path)
    path = sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))[0]
    document = json.loads(path.read_text("utf-8"))
    del document["units"][0]["origin"]
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    plan = plan_for(root)
    assert plan.exit_code == INVALID
    assert any("unit 1" in refusal.why for refusal in plan.refusals)


# --------------------------------------------------------------------------
# ⛔ `W208` — nothing raises out of `plan_for`, whatever a container map says
# --------------------------------------------------------------------------


def break_a_container_map(root, **fields):
    """Rewrite the first container map under `root`, returning its plan path."""
    path = sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))[0]
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(fields)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path.relative_to(root).as_posix()


def test_a_wrong_depth_container_address_is_a_refusal_and_not_a_crash(tmp_path):
    # ⛔ **The defect `W208` records.** `container.parse` raises SF-01's
    # `AddressError` for an arity disagreement — argued for in the reader's own
    # contract — and this site caught two of the three names that paragraph
    # gives. A wrong-depth map therefore CRASHED the one command whose whole
    # contract is that nothing raises.
    root = copy_fixture("depth2", tmp_path)
    where = break_a_container_map(root, address=["basics"], titles=["Basics"])

    plan = plan_for(root)

    assert plan.exit_code == INVALID
    assert where in [refusal.where for refusal in plan.refusals]


def test_a_leaking_container_map_is_a_refusal_and_not_a_crash(tmp_path):
    # ⭐ The pass-through this site already had, kept under the derived tuple so
    # the fix cannot be a swap of one omission for another.
    root = copy_fixture("depth1", tmp_path)
    where = break_a_container_map(root, note=f"ingested from {POISON}")

    plan = plan_for(root)

    assert plan.exit_code == INVALID
    assert where in [refusal.where for refusal in plan.refusals]


def test_an_unreadable_container_map_is_a_refusal_and_not_a_crash(tmp_path):
    # ⭐ The third shape, so the three arms of this reader's failure handling
    # are exercised together rather than one at a time as each one bites.
    root = copy_fixture("depth1", tmp_path)
    where = break_a_container_map(root, variant="no-such-variant")

    plan = plan_for(root)

    assert plan.exit_code == INVALID
    assert where in [refusal.where for refusal in plan.refusals]


def test_no_refusal_carries_the_absolute_path_it_was_read_from(tmp_path):
    # ⛔ R7: the crash this row fixes would have printed a traceback naming the
    # absolute path, so the refusal that replaces it must not.
    root = copy_fixture("depth2", tmp_path)
    break_a_container_map(root, address=["basics"], titles=["Basics"])

    for refusal in plan_for(root).refusals:
        assert str(tmp_path) not in refusal.line()


def test_the_catch_list_is_the_readers_own_tuple_and_not_a_copy():
    # ⛔ The durable half. A hand-copied list of exception types is a second
    # declaration, and this one had already drifted once — so the fix is
    # checked by reading the source, where a re-typed tuple would appear.
    source = (repository_root() / "src/studyforge/cli/plan/derive.py").read_text("utf-8")
    assert "except CONTAINER_RAISES as error:" in source
    assert "except MANIFEST_RAISES as error:" in source  # ⭐ `W213`, the manifest site
    assert "except (ContainerError" not in source, "the catch list was retyped again"
    assert "except (ManifestError" not in source, "the catch list was retyped again"
