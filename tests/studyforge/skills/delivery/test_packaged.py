"""Mirror of `src/studyforge/skills/delivery/packaged.py` (R12) — `REL-06`.

⭐ Four readings, from the cheapest to the one that IS the acceptance:

1. **The reader, in the tree.** `packaged_index()` and the module's command hand back the
   file beside the module, byte for byte.
2. **One copy.** While `docs/capability-index.md` is still on the main line it is the same
   bytes. ⭐ That the shipped file is the generator's output — the instrument that fails a
   hand-edit — is `test_walkthrough.py`'s, beside the procedure it serves.
3. **The declaration.** The file matches a `[tool.setuptools.package-data]` pattern and no
   `exclude-package-data` one — ⚠️ the proxy for where no build backend is importable.
4. **The effect.** A wheel built from an export carries the file unchanged, and unpacked
   beside nothing, run from an empty directory with no plan documents anywhere,
   `python3 -m studyforge.skills.delivery` prints it byte for byte.

⭐ Planted, RED: the index's pattern dropped from `package-data` (readings 3 and 4); one byte
of the shipped file changed (`test_walkthrough.py`'s regeneration).
"""

from __future__ import annotations

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

#: ⚠️ The copy `REL-11` takes off the main line. While it exists it is the same bytes.
DOCS_COPY = "docs/capability-index.md"


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


# --- 2. one copy ---------------------------------------------------


def test_the_documents_copy_is_the_shipped_one_while_it_exists() -> None:
    # ⚠️ `REL-11` takes `docs/capability-index.md` off the main line. Until then a reader of
    # either reads the same bytes, and this test is what keeps the two from diverging.
    copy = repository_root() / DOCS_COPY
    if copy.exists():
        assert copy.read_bytes() == tree_bytes(), f"{DOCS_COPY} differs from the shipped index"


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
    """`REL-04`'s wheel, built from an export of the tree the one way that module builds it."""
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
