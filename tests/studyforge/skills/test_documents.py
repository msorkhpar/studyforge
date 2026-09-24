"""Every `SKILL.md` ships in the wheel, and the installed package reads each one.

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
2 and 3), and the release tip's `package-data`, which shipped none.
"""

from __future__ import annotations

import os
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
    message = str(refusal.value)
    assert documents.names()[0] in message
    if name:
        assert name not in message, "a refusal reproduced the value it refused (R7)"


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
    return build_wheel(tmp_path_factory)


def build_wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the wheel `wheel` hands out; ⭐ shared, so every wheel reading builds it one way."""
    from tests.studyforge.skills.onboarding import wheels

    return wheels.build(tmp_path_factory.mktemp("build"))


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
