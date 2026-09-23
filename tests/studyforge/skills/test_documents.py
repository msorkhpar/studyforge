"""`REL-04`: every `SKILL.md` ships in the wheel, and the installed package reads each one.

⭐ Three readings, from the cheapest to the one that IS the acceptance:

1. **The locator, in the tree.** `names()` is exactly the tree's `SKILL.md` population —
   walked here with `glob`, never typed — and each document reads back byte-identical.
2. **The declaration.** Every tree `SKILL.md` matches a `[tool.setuptools.package-data]`
   pattern and no `exclude-package-data` pattern. ⚠️ A proxy for the wheel, kept because it
   needs no build backend: the dev image uninstalls setuptools once it has installed the
   package (`docker/dev/Dockerfile`), so reading 3 cannot run there.
3. **The effect.** A wheel built from an export of the tree carries every `SKILL.md`,
   byte-identical; unpacked beside nothing, with the working directory outside the checkout,
   `python3 -m studyforge.skills.documents` lists every skill and writes each document's
   bytes unchanged. ⛔ Skipped, saying why, only where no build backend is importable.

⭐ Planted, each RED: a glob that drops one skill's `SKILL.md` from `package-data` (readings
2 and 3), and the release tip's `package-data`, which shipped none (`W438/5`).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

import pytest

from studyforge.exitcodes import UNUSABLE
from studyforge.skills import documents
from tests.support import repository_root

#: The package directory, relative to the repository root.
SOURCE = PurePosixPath("src/studyforge")

#: What an export needs to build a wheel: the build configuration, the file it names as
#: its readme, and the source tree.
EXPORT = ("pyproject.toml", "README.md")

#: Builds a wheel with the in-process backend and prints its file name. ⛔ No pip and no
#: isolation: nothing is fetched, and the backend is whatever the environment already has.
BUILD = "import sys; from setuptools import build_meta; print(build_meta.build_wheel(sys.argv[1]))"


def tree_documents() -> dict[str, bytes]:
    """Every `SKILL.md` under the package, keyed by its path inside the package."""
    package = repository_root() / SOURCE
    found = {
        path.relative_to(package).as_posix(): path.read_bytes()
        for path in sorted(package.glob("skills/**/SKILL.md"))
    }
    assert found, f"{SOURCE}/skills ships no SKILL.md at all"
    return found


def declared(table: str) -> list[str]:
    """The `studyforge` patterns one `[tool.setuptools.*]` table declares."""
    with (repository_root() / "pyproject.toml").open("rb") as handle:
        config = tomllib.load(handle)
    return config["tool"]["setuptools"].get(table, {}).get("studyforge", [])


# --- 1. the locator, in the tree -------------------------------------------------------


def test_names_are_the_trees_population() -> None:
    expected = {f"skills/{name}/SKILL.md" for name in documents.names()}
    assert set(tree_documents()) == expected
    assert list(documents.names()) == sorted(documents.names())


def test_every_document_reads_back_unchanged() -> None:
    tree = tree_documents()
    for name in documents.names():
        body = tree[f"skills/{name}/SKILL.md"]
        assert documents.document(name).read_bytes() == body
        assert documents.text(name) == body.decode("utf-8")


@pytest.mark.parametrize("name", ["nosuchskill", "../skills", "", "onboarding/SKILL.md"])
def test_a_name_that_ships_no_document_is_refused(name: str) -> None:
    with pytest.raises(documents.UnknownSkill) as refusal:
        documents.document(name)
    assert documents.names()[0] in str(refusal.value)


def test_main_lists_every_skill(capsys: pytest.CaptureFixture[str]) -> None:
    assert documents.main([]) == 0
    assert capsys.readouterr().out.splitlines() == list(documents.names())


@pytest.mark.parametrize("argv", [["nosuchskill"], ["a", "b"], ["--path"]])
def test_main_refuses_a_bad_invocation(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert documents.main(argv) == UNUSABLE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err


# --- 2. the declaration ----------------------------------------------------------------


def test_every_document_is_declared_package_data() -> None:
    include, exclude = declared("package-data"), declared("exclude-package-data")
    undeclared = [
        path
        for path in tree_documents()
        if not any(PurePosixPath(path).full_match(pattern) for pattern in include)
        or any(PurePosixPath(path).full_match(pattern) for pattern in exclude)
    ]
    assert not undeclared, f"not shipped by [tool.setuptools.package-data]: {undeclared}"


# --- 3. the effect ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A wheel built from an export of the tree — never from the checkout, which it dirties."""
    if importlib.util.find_spec("setuptools") is None:
        pytest.skip(
            "no build backend here (the dev image uninstalls setuptools after installing "
            "the package); the declaration test still ran — build on the host to read this"
        )
    root = repository_root()
    export = tmp_path_factory.mktemp("export")
    for name in EXPORT:
        shutil.copy2(root / name, export / name)
    shutil.copytree(
        root / "src", export / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info")
    )
    out = tmp_path_factory.mktemp("wheel")
    built = subprocess.run(
        [sys.executable, "-c", BUILD, str(out)],
        cwd=export,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert built.returncode == 0, built.stderr[-2000:]
    return out / built.stdout.strip().splitlines()[-1]


def test_the_wheel_carries_every_document_unchanged(wheel: Path) -> None:
    prefix = "studyforge/"
    with zipfile.ZipFile(wheel) as archive:
        shipped = {
            name.removeprefix(prefix): archive.read(name)
            for name in archive.namelist()
            if name.startswith(prefix + "skills/") and name.endswith("/SKILL.md")
        }
    tree = tree_documents()
    missing = sorted(set(tree) - set(shipped))
    assert not missing, f"missing from the wheel: {missing}"
    assert shipped == tree


def test_the_installed_package_reads_every_document(wheel: Path, tmp_path: Path) -> None:
    site, elsewhere = tmp_path / "site", tmp_path / "elsewhere"
    elsewhere.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(site)
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env["PYTHONPATH"] = str(site)

    def run(*argv: str) -> bytes:
        done = subprocess.run(
            [sys.executable, "-m", "studyforge.skills.documents", *argv],
            cwd=elsewhere,
            env=env,
            capture_output=True,
            timeout=60,
            check=False,
        )
        assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
        return done.stdout

    where = subprocess.run(
        [sys.executable, "-c", "import studyforge; print(studyforge.__file__)"],
        cwd=elsewhere,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    assert Path(where.stdout.strip()).is_relative_to(site), "the checkout was imported"

    tree = tree_documents()
    listed = run().decode("utf-8").splitlines()
    assert [f"skills/{name}/SKILL.md" for name in listed] == sorted(tree)
    for name in listed:
        assert run(name) == tree[f"skills/{name}/SKILL.md"], name
