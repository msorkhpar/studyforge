"""Mirror of `src/studyforge/skills/delivery/packaged.py` (R12).

⭐ Four readings, from the cheapest to the one that IS the acceptance:

1. **The reader, in the tree.** `packaged_index()` and the module's command hand back the
   file beside the module, byte for byte.
2. **Frozen, so a hand-edit fails.** The shipped file is the generator's output over the
   epics as they stood with their task text, and that text now lives on the archive branch,
   not beside the package. So no test here can regenerate it; instead its digest is pinned,
   and any change to its bytes turns this reading RED. A deliberate regeneration — run over
   the archive's epics, task index and pin document, as the delivery skill's `SKILL.md`
   describes — updates the digest in the same commit.
3. **The declaration.** The file matches a `[tool.setuptools.package-data]` pattern and no
   `exclude-package-data` one — ⚠️ the proxy for where no build backend is importable.
4. **The effect.** A wheel built from an export carries the file unchanged, and unpacked
   beside nothing, run from an empty directory with no plan documents anywhere,
   `python3 -m studyforge.skills.delivery` prints it byte for byte.

⭐ Planted, RED: the index's pattern dropped from `package-data` (readings 3 and 4); one byte
of the shipped file changed (reading 2).
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

import pytest

from studyforge.exitcodes import UNUSABLE
from studyforge.skills import delivery
from studyforge.skills.delivery import packaged
from tests.studyforge.skills.test_documents import build_wheel, declared
from tests.support import repository_root

#: The shipped index, as a path inside the `studyforge` package.
SHIPPED = PurePosixPath("skills/delivery") / packaged.NAME

#: The SHA-256 of the shipped index: the generator's output over the epics as they stand on the
#: `archive/process` branch, byte-identical to a regeneration there.
FROZEN = "4bdf1cf988fca989f0d222d655052595004b3d796455cab508200ce935b7d009"


def tree_bytes() -> bytes:
    """The shipped index as the tree carries it."""
    return (repository_root() / "src/studyforge" / SHIPPED).read_bytes()


def packaged_text() -> str:
    """The shipped index through the reader under test."""
    return packaged.packaged_index()


# --- 1. the reader, in the tree ---------------------------------------------------------


def test_the_index_is_the_file_beside_the_module() -> None:
    assert packaged.INDEX == Path(packaged.__file__).resolve().parent / packaged.NAME
    assert packaged.INDEX.read_bytes() == tree_bytes()


def test_the_reader_hands_back_the_shipped_text() -> None:
    assert packaged_text() == tree_bytes().decode("utf-8")
    assert delivery.packaged_index is packaged.packaged_index


def test_the_command_writes_the_bytes_unchanged(capfd: pytest.CaptureFixture[bytes]) -> None:
    assert packaged.main([]) == 0
    assert capfd.readouterr().out == tree_bytes().decode("utf-8")


def test_the_command_takes_no_argument(capsys: pytest.CaptureFixture[str]) -> None:
    assert packaged.main(["docs/tasks"]) == UNUSABLE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert packaged.USAGE in captured.err


def test_the_shipped_index_says_it_is_generated() -> None:
    assert delivery.BANNER in packaged_text()


# --- 2. frozen, so a hand-edit fails ---------------------------------------------------


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_shipped_index_is_the_frozen_generation() -> None:
    # ⛔ A hand-edit is a finding against the delivery skill (R19), never a fix. The epics it
    # was generated from no longer carry their task text on this line, so the digest is the
    # instrument that reports one.
    assert digest(tree_bytes()) == FROZEN, (
        "the shipped capability index changed: a hand-edit is a finding, not a fix. "
        "Regenerate it from the archive branch's epics and update FROZEN in the same commit"
    )


def test_one_changed_byte_is_refused() -> None:
    planted = bytearray(tree_bytes())
    planted[-2] ^= 0x01
    assert digest(bytes(planted)) != FROZEN


# --- 3. the declaration -------------------------------------------------------------------


def test_the_index_is_declared_package_data() -> None:
    include, exclude = declared("package-data"), declared("exclude-package-data")
    assert any(SHIPPED.full_match(pattern) for pattern in include), (
        f"{SHIPPED} is not shipped by [tool.setuptools.package-data]"
    )
    assert not any(SHIPPED.full_match(pattern) for pattern in exclude)


# --- 4. the effect ------------------------------------------------------------------------


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The package's wheel, built from an export of the tree the one way that module builds it."""
    return build_wheel(tmp_path_factory)


def test_the_wheel_carries_the_index_unchanged(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        member = f"studyforge/{SHIPPED}"
        assert member in names, f"missing from the wheel: {member}"
        assert archive.read(member) == tree_bytes()


def test_the_installed_package_prints_the_index_with_no_plan_anywhere(
    wheel: Path, tmp_path: Path
) -> None:
    site, elsewhere = tmp_path / "site", tmp_path / "elsewhere"
    elsewhere.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(site)
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env["PYTHONPATH"] = str(site)

    def run(*argv: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, *argv],
            cwd=elsewhere,
            env=env,
            capture_output=True,
            timeout=60,
            check=False,
        )

    where = run("-c", "import studyforge; print(studyforge.__file__)")
    assert Path(where.stdout.decode().strip()).is_relative_to(site), "the checkout was imported"
    assert not any(site.rglob("docs")) and not any(elsewhere.iterdir())

    done = run("-m", "studyforge.skills.delivery")
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert done.stdout == tree_bytes()
