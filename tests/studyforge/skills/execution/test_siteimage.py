"""Mirror of `src/studyforge/skills/execution/siteimage.py` (R12): the site image, at the pin.

⭐ Over a stand-in for an INSTALLED library — a package directory with its
`COMMIT` stamp and a dist-info beside it, as a wheel installs one — so the pin
check reads what a reader's Python would.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.skills.execution import SITE_ENV, onboard, siteimage, written
from studyforge.skills.execution.binds import ExecutionRefused
from studyforge.skills.onboarding.pin import PIN_FILE, pin_document

COMMIT = "0123456789abcdef0123456789abcdef01234567"
OTHER = "fedcba9876543210fedcba9876543210fedcba98"
VERSION = "0.1.0"


def installed(where: Path, *, commit: str | None = COMMIT, version: str = VERSION) -> Path:
    package = where / "site-packages" / "studyforge"
    (package / "serve").mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "serve" / "app.py").write_text("PORT = 1\n", encoding="utf-8")
    (package / "__pycache__").mkdir()
    (package / "__pycache__" / "x.cpython-314.pyc").write_bytes(b"\x00")
    if commit is not None:
        (package / "COMMIT").write_text(commit + "\n", encoding="utf-8")
    info = package.parent / f"studyforge-{version}.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(f"Name: studyforge\nVersion: {version}\n", encoding="utf-8")
    return package


def pinned(root: Path, commit: str = COMMIT, version: str = VERSION) -> Path:
    (root / PIN_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / PIN_FILE).write_text(json.dumps(pin_document(commit, version)), encoding="utf-8")
    return root


@pytest.fixture
def root(tmp_path) -> Path:
    return pinned(tmp_path / "corpus")


def test_staging_copies_the_library_writes_the_build_and_records_the_tag(tmp_path, root):
    staged = siteimage.stage_site(root, package=installed(tmp_path))
    context = root / siteimage.SITE_DIR
    assert (context / siteimage.LIBRARY / "studyforge" / "serve" / "app.py").is_file()
    assert not list((context / siteimage.LIBRARY).rglob("__pycache__")), "no bytecode is copied"
    assert staged.tag.startswith(f"{siteimage.REPOSITORY}:{VERSION}-")
    env = (root / SITE_ENV).read_text(encoding="utf-8")
    assert f"STUDYFORGE_SITE_IMAGE={staged.tag}\n" in env and "COMPOSE_PROFILES=site\n" in env
    # ⛔ Staged, the preflight is a REQUIRED dependency: an optional one that fails
    # is only a warning to compose, which then starts every service anyway.
    assert "STUDYFORGE_PREFLIGHT=true\n" in env
    assert staged.argv == (
        "docker",
        "build",
        "--file",
        f"{siteimage.SITE_DIR}/{siteimage.BUILD_FILE}",
        "--tag",
        staged.tag,
        siteimage.SITE_DIR,
    )
    assert written.hand_edited(root) == [], "every file it records is stamped as its own"


def test_the_build_pulls_its_base_by_digest_and_runs_serve():
    text = siteimage.build_file()
    assert "FROM python:3.14-slim@sha256:" in text
    assert text.count("FROM ") == 1
    assert 'ENTRYPOINT ["python3", "-m", "studyforge.cli"]' in text


def test_the_same_library_stages_the_same_tag_and_a_moved_byte_moves_it(tmp_path, root):
    package = installed(tmp_path)
    first = siteimage.stage_site(root, package=package).tag
    assert siteimage.stage_site(root, package=package).tag == first
    (package / "serve" / "app.py").write_text("PORT = 2\n", encoding="utf-8")
    assert siteimage.stage_site(root, package=package).tag != first


def test_a_file_the_library_no_longer_ships_leaves_the_copy(tmp_path, root):
    package = installed(tmp_path)
    siteimage.stage_site(root, package=package)
    (package / "serve" / "app.py").unlink()
    siteimage.stage_site(root, package=package)
    assert not (root / siteimage.SITE_DIR / siteimage.LIBRARY / "studyforge/serve/app.py").exists()


def test_a_library_built_from_another_commit_than_the_pin_is_refused(tmp_path, root):
    with pytest.raises(ExecutionRefused, match="not the one the corpus pinned"):
        siteimage.stage_site(root, package=installed(tmp_path, commit=OTHER))
    assert not (root / SITE_ENV).exists(), "nothing is recorded for a refused library"


def test_a_library_of_another_version_than_the_pin_is_refused(tmp_path, root):
    with pytest.raises(ExecutionRefused, match="not the one the corpus pinned"):
        siteimage.stage_site(root, package=installed(tmp_path, version="0.2.0"))


def test_a_source_tree_which_carries_no_commit_is_refused(tmp_path, root):
    with pytest.raises(ExecutionRefused, match="source tree"):
        siteimage.stage_site(root, package=installed(tmp_path, commit=None))


def test_a_corpus_with_no_pin_is_refused(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    with pytest.raises(ExecutionRefused):
        siteimage.stage_site(bare, package=installed(tmp_path))


def test_the_copied_library_is_ignored_and_the_build_file_is_the_record(tmp_path, root):
    staged = siteimage.stage_site(root, package=installed(tmp_path))
    ignore = (root / siteimage.SITE_DIR / ".gitignore").read_text(encoding="utf-8")
    assert ignore == f"/{siteimage.LIBRARY}/\n"
    assert set(staged.written) == {
        f"{siteimage.SITE_DIR}/{siteimage.BUILD_FILE}",
        f"{siteimage.SITE_DIR}/.gitignore",
        SITE_ENV,
    }
    assert all(onboard.classified(one) for one in staged.written)
