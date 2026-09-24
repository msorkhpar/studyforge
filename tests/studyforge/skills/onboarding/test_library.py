"""Mirror of `src/studyforge/skills/onboarding/library.py` (R12).

⭐ The version is read from the library this Python imports — a wheel's
distribution metadata beside the package, or a source tree's `pyproject.toml`
— and a pin is read back gated, refusing one that predates the installed scheme.
"""

from __future__ import annotations

import json
import tomllib

import pytest

from studyforge.skills.onboarding import library, pin
from tests.studyforge.skills.onboarding import corpora
from tests.support import repository_root


def _declared():
    with (repository_root() / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def _dist_info(site, name="studyforge", version="3.2.1"):
    info = site / f"{name}-{version}.dist-info"
    info.mkdir(parents=True)
    (info / "METADATA").write_text(
        f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n\n# Readme\nName: not me\n",
        encoding="utf-8",
    )


def test_the_source_tree_this_test_imports_reads_as_its_declared_version():
    assert library.version() == _declared()
    assert library.PACKAGE == (repository_root() / "src" / "studyforge").resolve()


def test_an_installed_package_reads_its_distribution_metadata(tmp_path):
    package = tmp_path / "site-packages" / "studyforge"
    package.mkdir(parents=True)
    _dist_info(package.parent)

    assert library.version(package) == "3.2.1"


def test_another_distributions_metadata_beside_it_is_not_read(tmp_path):
    package = tmp_path / "site-packages" / "studyforge"
    package.mkdir(parents=True)
    _dist_info(package.parent, name="studyforge", version="3.2.1")
    _dist_info(package.parent, name="studyforge-extras", version="9.9.9")

    assert library.version(package) == "3.2.1"


def test_two_installed_versions_beside_one_package_are_refused_by_name(tmp_path):
    package = tmp_path / "site-packages" / "studyforge"
    package.mkdir(parents=True)
    _dist_info(package.parent, version="3.2.1")
    _dist_info(package.parent, version="3.2.2")

    with pytest.raises(library.LibraryRefused, match="2 studyforge distributions"):
        library.version(package)


def test_a_package_with_nothing_to_read_is_refused_and_names_no_path(tmp_path):
    package = tmp_path / "loose" / "studyforge"
    package.mkdir(parents=True)

    with pytest.raises(library.LibraryRefused, match="version cannot be read") as refused:
        library.version(package)
    assert str(tmp_path) not in str(refused.value)


def test_a_version_shaped_like_a_path_is_refused_and_not_quoted(tmp_path):
    package = tmp_path / "site-packages" / "studyforge"
    package.mkdir(parents=True)
    _dist_info(package.parent, version="0.1")
    (package.parent / "studyforge-0.1.dist-info" / "METADATA").write_text(
        "Name: studyforge\nVersion: ../../somewhere\n", encoding="utf-8"
    )

    with pytest.raises(library.LibraryRefused) as refused:
        library.version(package)
    assert "somewhere" not in str(refused.value)


def _pinned(tmp_path, **document):
    (tmp_path / pin.PIN_DIR).mkdir()
    (tmp_path / pin.PIN_FILE).write_text(json.dumps(document), encoding="utf-8")
    return tmp_path


def test_a_pin_is_read_back_with_its_version_and_commit(tmp_path):
    root = _pinned(tmp_path, **pin.pin_document(corpora.COMMIT, "3.2.1"))

    read = library.pinned(root)

    assert (read["version"], read["commit"]) == ("3.2.1", corpora.COMMIT)


def test_a_sibling_pin_is_refused_as_predating_the_installed_library(tmp_path):
    root = _pinned(tmp_path, pin_api=1, where="sibling", commit=corpora.COMMIT)

    with pytest.raises(library.LibraryRefused, match="predates the installed library"):
        library.pinned(root)


def test_an_absent_pin_is_refused_by_name(tmp_path):
    with pytest.raises(library.LibraryRefused, match="there is no pin"):
        library.pinned(tmp_path)


def test_a_pin_carrying_a_path_is_refused_and_not_quoted(tmp_path):
    root = _pinned(
        tmp_path, **{**pin.pin_document(corpora.COMMIT, "3.2.1"), "version": "../../elsewhere"}
    )

    with pytest.raises(library.LibraryRefused) as refused:
        library.pinned(root)
    assert "elsewhere" not in str(refused.value)
