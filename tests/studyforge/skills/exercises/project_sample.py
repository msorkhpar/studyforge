"""The sample project (`tests/fixtures/project/`) as the project tests gate it: one shared setup.

⭐ A small fictional seed-crate planner grown over two snapshots, `steps/00` and `steps/01`, and one
manifest, `practices/01-must-ship/project.json`, that makes lesson 1's practice of it.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from studyforge.address import Address
from studyforge.exercise.bundle import Places
from studyforge.skills.exercises import Brief, Page, gate_code, take
from studyforge.skills.exercises.project import project_draft, read_manifest
from tests.studyforge.skills.exercises.authoring import Running
from tests.support import repository_root

#: The sample project, and the manifest of its one practice.
SAMPLE = repository_root() / "tests" / "fixtures" / "project"
MANIFEST = SAMPLE / "practices" / "01-must-ship" / "project.json"

#: The page the practice cites, as a corpus would carry it.
PAGE = "lessons/fixing.md"


def brief_and_ledger(root: Path):
    """A one-page corpus under `root`, its ledger, and the brief for its first practice."""
    (root / "lessons").mkdir(parents=True, exist_ok=True)
    (root / PAGE).write_text("# Fixing a variable\n\nA forced lot is fixed to one.\n", "utf-8")
    ledger = take(root, [PAGE], [], "the ledger")
    page = Page(PAGE, Address(["seeds"]), "prose", 1, "code", (), "core")
    places = Places(page.address, page.variant, 1, 1)
    return Brief(page, "neither", 1, places, 1, ()), ledger


def copy_sample(root: Path, change: dict | None = None) -> Path:
    """The sample copied under `root`, its manifest's keys replaced by `change`; the manifest."""
    target = root / "project"
    shutil.copytree(SAMPLE, target, ignore=shutil.ignore_patterns("__pycache__", "conftest.py"))
    manifest = target / MANIFEST.relative_to(SAMPLE)
    document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps({**document, **(change or {})}), encoding="utf-8")
    return manifest


def gated(root: Path, manifest: Path = MANIFEST, runner=None):
    """Gate the practice the manifest declares, every run a real `pytest` process; the result."""
    brief, ledger = brief_and_ledger(root / "corpus")
    draft = project_draft(manifest, brief.places.workspace)
    return gate_code(draft, brief, ledger, runner or Running(), source="demo", where="w"), draft


def manifest():
    """The sample's manifest, read."""
    return read_manifest(MANIFEST)
