"""Shared by SF-19b's tests: fixture corpora built IN PLACE under one harness-minted root.

⭐ `a_workspace` is the discovery clauses' input: a root holding the `tree`-profile
depth-1 fixture and the `sibling`-profile depth-2 fixture, each built into itself
the way a consumer repository is, with no path configured anywhere.

⛔ Every practice key is spelled by `progress.practice_key` and every unit key is
read from the corpus's own declarations — never typed here (`SF-21/4`).
"""

from __future__ import annotations

from pathlib import Path

from studyforge.address import parse_unit_key
from studyforge.corpus.discovery import scan
from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.generate import write_site
from studyforge.generate.declarations import read_corpus
from studyforge.progress import Progress, practice_key
from tests.studyforge.generate.corpora import BOTH, a_corpus

WHEN = "2026-09-12T10:00:00+00:00"
LATER = "2026-09-12T11:00:00+00:00"
SECTION = "practice-one"


def a_workspace(tmp_path: Path, names: tuple[str, ...] = BOTH) -> Path:
    """A root under `tmp_path` holding each named fixture, built into itself."""
    workspace = tmp_path / "workspace"
    for name in names:
        root = a_corpus(workspace, name)
        write_site(root, root)
    return workspace


def source_of(root: Path) -> str:
    return load(root / MANIFEST_FILENAME).source


def depth_of(root: Path) -> int:
    return load(root / MANIFEST_FILENAME).depth


def unit_keys(root: Path) -> list[str]:
    """Every declared unit with material, in declared order, as the corpus spells it."""
    return [unit.key for unit in read_corpus(root).units]


def practice(root: Path, unit_key: str, section: str = SECTION) -> str:
    address, ordinal = parse_unit_key(unit_key, depth_of(root))
    return practice_key(address, ordinal, section)


def record(
    root: Path,
    unit_key: str,
    *,
    mode: str = "test",
    exit_code: int = 0,
    when: str = WHEN,
    section: str = SECTION,
) -> dict:
    """Record one run through the store, the only writer (`SF-21`)."""
    depth = depth_of(root)
    address, ordinal = parse_unit_key(unit_key, depth)
    store = Progress(root, depth)
    return store.record_run(
        address, ordinal, section, mode=mode, exit_code=exit_code, commands=["make test"], when=when
    )


def pages_of(root: Path, unit_key: str) -> list[Path]:
    """Every page under `root` that identifies itself as `unit_key`, by a scan."""
    site = scan(root, {source_of(root): depth_of(root)})
    return [
        root / found.path
        for found in site.units
        if found.identity.address.unit_key(found.identity.unit) == unit_key
    ]
