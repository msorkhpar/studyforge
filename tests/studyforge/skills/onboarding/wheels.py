"""A wheel of this tree, installed into a fresh virtual environment outside the checkout.

⭐ The installed-library reading needs what a stranger has: the library INSTALLED, and no
framework checkout anywhere a corpus could reach. ⛔ Built from an export, never
the checkout (a build writes `build/` and `*.egg-info` into its source tree), with
the in-process backend and no pip: nothing is fetched. The venv is made
`--without-pip`, and the wheel is unpacked into its `site-packages` — which is
what an install of a pure wheel puts there.

⚠️ The pinned dev image uninstalls setuptools once it has installed the package
so there the build is skipped, saying why.

⭐ **The export is committed to a git repository of its own** (`W467`): a wheel
records the commit it was built from, and `setup.py` refuses to build one from a
tree that is not the top of a checkout. Placeholder identities at a fixed date,
and no user or system config, so no identity of this machine's is read (R7).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tests.studyforge.skills.onboarding.corpora import SYNTHETIC_GIT
from tests.support import repository_root

#: What an export needs to build a wheel: the build configuration, the build step
#: that stamps the commit, and the readme.
EXPORT = ("pyproject.toml", "setup.py", "README.md")

#: Where a wheel carries its commit (`library.STAMP`, written by `setup.py`).
STAMPED = "studyforge/COMMIT"

#: Builds a wheel with the in-process backend and prints its file name.
BUILD = "import sys; from setuptools import build_meta; print(build_meta.build_wheel(sys.argv[1]))"


def build(scratch: Path) -> Path:
    """Build a wheel of this tree from an export under `scratch`; return the wheel."""
    if importlib.util.find_spec("setuptools") is None:
        pytest.skip(
            "no build backend here (the dev image uninstalls setuptools after installing "
            "the package, REL-04/1); build on the host to read the installed library"
        )
    root = repository_root()
    export = scratch / "export"
    export.mkdir()
    for name in EXPORT:
        shutil.copy2(root / name, export / name)
    shutil.copytree(
        root / "src", export / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info")
    )
    commit_tree(export)
    out = scratch / "wheel"
    out.mkdir()
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


def commit_tree(tree: Path) -> str:
    """Make `tree` a git repository holding one commit of everything in it; return the commit."""
    env = {**environment(Path(sys.executable).parent), **SYNTHETIC_GIT}
    for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "export"]):
        subprocess.run(["git", *argv], cwd=tree, env=env, check=True, capture_output=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tree, env=env, check=True, capture_output=True, text=True
    ).stdout.strip()


def stamp_of(wheel: Path) -> str:
    """Return the commit a wheel carries."""
    with zipfile.ZipFile(wheel) as archive:
        return archive.read(STAMPED).decode("utf-8").strip()


def environment(bin_dir: Path) -> dict[str, str]:
    """This process's environment with no Python override, and `bin_dir` first on PATH."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env["PATH"] = os.pathsep.join([str(bin_dir), env.get("PATH", "")])
    return env


def venv(where: Path, wheel: Path) -> Path:
    """A fresh venv at `where` with `wheel` installed; return its `bin` directory."""
    subprocess.run(
        [sys.executable, "-m", "venv", "--without-pip", str(where)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    bin_dir = where / "bin"
    purelib = subprocess.run(
        [str(bin_dir / "python3"), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        env=environment(bin_dir),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout.strip()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(purelib)
    return bin_dir
