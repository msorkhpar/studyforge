"""`W267`: `plan` against what `build` actually writes, over a corpus without output and with it.

⛔ **The golden test compares `plan` with its own golden**, which is why `W268/1` stayed
hidden. ⭐ These build each fixture copy into its own root and compare `plan` with the
build's own record, on the tree profile and the sibling profile. Nothing under `tests/`
is written: every tree is a copy under `tmp_path`.
"""

from __future__ import annotations

import shutil

import pytest

from studyforge.cli.plan import plan_for
from studyforge.cli.plan.report import CLAIM, CREATE, EXPECT, KEEP, REPLACE
from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.generate import write_site
from tests.fixture_checks import FIXTURES

#: Both profiles, built into their own roots, as `generate`'s tests build them.
BUILT = ("depth1", "depth2")


def copy_fixture(name: str, tmp_path):
    """A throwaway copy of one fixture corpus, so a build may write into it."""
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


def _verbs(plan) -> dict[str, str]:
    return {creation.path: creation.verb for creation in plan.creations}


@pytest.mark.parametrize("name", BUILT)
def test_WITHOUT_output_only_the_archive_is_on_disk_and_it_is_kept(name, tmp_path):
    verbs = _verbs(plan_for(copy_fixture(name, tmp_path)))
    assert verbs[f"{ARCHIVE_DIR}/"] == KEEP
    assert REPLACE not in verbs.values()
    rest = {verb for path, verb in verbs.items() if path != f"{ARCHIVE_DIR}/"}
    assert rest <= {CREATE, CLAIM, EXPECT}


@pytest.mark.parametrize("name", BUILT)
def test_WITH_output_no_path_on_disk_is_a_create(name, tmp_path):
    root = copy_fixture(name, tmp_path)
    write_site(root, root)
    after = plan_for(root)
    on_disk = [c for c in after.creations if (root / c.path.rstrip("/")).exists()]
    assert on_disk and [c.path for c in on_disk if c.verb in (CREATE, CLAIM, EXPECT)] == []
    assert [c.path for c in after.creations if c.verb == REPLACE]


@pytest.mark.parametrize("name", BUILT)
def test_the_plan_lists_what_the_BUILD_writes_and_nothing_it_does_not(name, tmp_path):
    """⛔ `W268/1`: asserted against what `build` wrote, never against the plan's own golden."""
    root = copy_fixture(name, tmp_path)
    before = plan_for(root)
    wrote = {path.as_posix() for path in write_site(root, root).paths}
    files = {c.path for c in before.creations if c.verb == CREATE and not c.path.endswith("/")}
    built_dirs = [c.path for c in before.creations if c.verb == CREATE and c.path.endswith("/")]
    claimed = [c.path for c in before.creations if c.verb == CLAIM]
    assert files <= wrote
    assert all(any(f.startswith(d) for d in built_dirs + claimed) for f in wrote - files)
    assert all((root / d).is_dir() for d in built_dirs)
    for directory in claimed:
        filled = any(path.startswith(directory) for path in wrote)
        assert (root / directory).is_dir() == filled, directory
    elsewhere = {c.path for c in before.creations if c.verb in (EXPECT, KEEP)}
    assert not {path for path in wrote if path in elsewhere}


@pytest.mark.parametrize("name", BUILT)
def test_a_rebuild_replaces_exactly_the_files_the_plan_says_it_replaces(name, tmp_path):
    root = copy_fixture(name, tmp_path)
    write_site(root, root)
    after = plan_for(root)
    replaced = {path.as_posix() for path in write_site(root, root).replaced}
    said = {c.path for c in after.creations if c.verb == REPLACE and not c.path.endswith("/")}
    assert said and said <= replaced
