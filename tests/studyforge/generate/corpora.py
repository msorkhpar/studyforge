"""Fixture corpora and the committed plan goldens, for `studyforge.generate`'s tests.

⛔ **Every expected path is READ from `tests/fixtures/golden/*.plan.txt`**, never
retyped here. A list spelled in a test module would agree with the build for the
same reason the build agrees with itself, and Ruling 99 exists because a plan and
a build that drifted together would pass a diff between them.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.support import repository_root

FIXTURES = repository_root() / "tests" / "fixtures"
GOLDEN = FIXTURES / "golden"

#: Both `FND-04` fixtures. ⭐ Named once so a clause runs against the tree
#: profile and the sibling profile without either being the default.
BOTH = ("depth1", "depth2")


def planned(name: str, suffix: str = ".html") -> list[str]:
    """The paths `studyforge plan`'s committed golden says a build creates."""
    lines = (GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8").splitlines()
    created = [line.split()[1] for line in lines if line.startswith("create ")]
    return sorted(path for path in created if path.endswith(suffix))


def a_corpus(tmp_path: Path, name: str) -> Path:
    """A writable copy of one fixture corpus, so nothing under `tests/` is touched."""
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


def with_a_unit_missing(tmp_path: Path, name: str, where: str) -> Path:
    """A fixture copy whose material for one declared unit has been removed.

    ⭐ **The mechanism removed rather than mocked**, and it is the state §7 calls
    *declared but not present* — which neither fixture has as shipped, so every
    clause about an unbuilt unit would otherwise be untestable.
    """
    root = a_corpus(tmp_path, name)
    shutil.rmtree(root / where)
    return root


def an_output(tmp_path: Path, name: str = "out") -> Path:
    """An empty output root that already exists.

    ⛔ The build refuses to mint its own root — see `generate/writing.py` — so a
    test that wants one somewhere other than `tmp_path` creates it here.
    """
    root = tmp_path / name
    root.mkdir(parents=True)
    return root
