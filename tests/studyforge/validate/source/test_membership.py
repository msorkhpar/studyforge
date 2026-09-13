"""Mirror of `src/studyforge/validate/source/membership.py` (R12, `W248`).

⛔ **A stray beneath the archive root is refused by name, never skipped.** Both
ways: a planted file turns `validate` RED and names itself, and an archive
laid out by SK-02's own `Layout` reads clean.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.archive.document import build
from studyforge.archive.document import render as render_document
from studyforge.corpus.container import Container, Unit
from studyforge.corpus.container import render as render_map
from studyforge.corpus.placement import ARCHIVE_DIRNAME
from studyforge.skills.adapter import Layout
from studyforge.validate import validate
from studyforge.validate.corpus import read
from studyforge.validate.source import RULE_ARCHIVE_STRAY, archive_members
from tests.studyforge.validate import corpora
from tests.support import repository_root

STRAY = RULE_ARCHIVE_STRAY


def strays(root: Path) -> list[str]:
    """The paths `validate` refuses as strays, as it names them."""
    return [f.where for f in validate(root).findings if f.rule == STRAY]


def plant(root: Path, where: str, text: str = "planted\n") -> str:
    """Write one file at `where` beneath the corpus root and return `where`."""
    path = root / where
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return where


# --------------------------------------------------------------------------
# ⛔ refused by name
# --------------------------------------------------------------------------


def test_a_planted_note_beneath_the_archive_root_turns_validate_red_and_names_it(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    where = plant(root, f"{ARCHIVE_DIRNAME}/notes.md")
    report = validate(root)
    assert not report.ok
    assert strays(root) == [where]
    assert [f.rule for f in report.findings] == [STRAY], [f.line() for f in report.findings]


def test_a_stray_is_named_even_when_the_archive_holds_no_map(tmp_path):
    # ⭐ Not waiting on a container: `no-archive` says there is no map, and the
    # stray is still named beside it.
    root = corpora.write(tmp_path / "c")
    where = plant(root, f"{ARCHIVE_DIRNAME}/notes.md")
    assert set(validate(root).rules) == {"no-archive", STRAY}
    assert strays(root) == [where]


@pytest.mark.parametrize(
    "shape",
    [
        "demo/notes.md",  # beside a map, not a member
        "demo/raw/notes.md",  # member-shaped directory, outside any variant
        "demo/raw/prose/notes.md",  # beneath the variant, outside any unit, never read
        "demo/raw/prose/unit-01/notes.md",  # inside a unit, not a document
        "demo/raw/other/unit-01/lesson-1.json",  # a second variant the map does not read
        "demo/units/unit-02/media/x.svg",  # an undeclared unit's own files
        "raw/unit-01/lesson-1.md",  # member-shaped, outside every container
        ".keep",  # hidden, and still a file nobody reads
    ],
)
def test_every_file_no_reader_reads_is_a_stray(tmp_path, shape):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    where = plant(root, f"{ARCHIVE_DIRNAME}/{shape}")
    assert strays(root) == [where]


def test_a_json_file_beneath_the_variant_at_the_wrong_depth_reads_as_identity_once(tmp_path):
    # ⚠️ The walk reads every `.json` beneath a map's variant, so this file is
    # read as a document and `identity` refuses it. One defect, one rule.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    good = root / ARCHIVE_DIRNAME / "demo/raw/prose/unit-01/lesson-1.json"
    plant(root, f"{ARCHIVE_DIRNAME}/demo/raw/prose/lesson-2.json", good.read_text("utf-8"))
    report = validate(root)
    assert "identity" in report.rules
    assert STRAY not in report.rules


def test_nothing_beneath_a_map_that_did_not_parse_is_judged_twice(tmp_path):
    # ⛔ `run` already says no document there was read. A stray finding per
    # file would be N findings for one broken map.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / ARCHIVE_DIRNAME / "demo/container.json").write_text("{", encoding="utf-8")
    plant(root, f"{ARCHIVE_DIRNAME}/demo/notes.md")
    report = validate(root)
    assert "container" in report.rules
    assert STRAY not in report.rules


def test_a_stray_is_never_read_as_material_even_when_the_manifest_includes_it(tmp_path):
    # ⛔ Refused, never resolved: no precedence lets `include` claim it.
    manifest = {**corpora.MANIFEST, "content": {"include": ["src/*.md", f"{ARCHIVE_DIRNAME}/*"]}}
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "corpus.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    where = plant(root, f"{ARCHIVE_DIRNAME}/notes.md")
    assert strays(root) == [where]


# --------------------------------------------------------------------------
# ⭐ an adapter-written archive reads clean
# --------------------------------------------------------------------------

ADDRESS = Address(["demo"])


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_an_archive_laid_out_by_the_adapter_layout_reads_clean(tmp_path):
    # ⭐ Every shape `Layout` mints: a map, a lesson, a practice, and a unit's
    # own files (media and the overlay), with `validate`'s verdict unchanged.
    root = corpora.write(tmp_path / "c", sources={"src/one.md": corpora.SOURCE})
    layout = Layout(root)
    container = Container(
        address=ADDRESS,
        titles=("Demo",),
        variant="prose",
        ingested="2026-01-05",
        units=(Unit(n=1, title="Unit 1", practices=1, origin="src/one.md"),),
    )
    _write(layout.container_map(ADDRESS), render_map(container))
    for kind in ("lesson", "practice"):
        document = build(
            source="demo",
            address=ADDRESS,
            variant="prose",
            unit=1,
            kind=kind,
            ordinal=1,
            ingested="2026-01-05",
            title="Unit 1",
            blocks=corpora.BLOCKS,
        )
        _write(layout.document(ADDRESS, "prose", 1, kind, 1), render_document(document))
    _write(layout.unit_files(ADDRESS, 1) / "media" / "diagram.svg", "<svg/>\n")
    _write(layout.unit_files(ADDRESS, 1) / "content.json", "{}\n")
    report = validate(root)
    assert STRAY not in report.rules, [f.line() for f in report.findings]
    assert len(archive_members(read(root))) == 3


@pytest.mark.parametrize("name", ["depth1", "depth2", "shared-origin"])
def test_the_shipped_archives_hold_no_stray(name):
    # ⭐ Files somebody else wrote, including `units/` media and an overlay.
    assert strays(repository_root() / "tests/fixtures" / name) == []
