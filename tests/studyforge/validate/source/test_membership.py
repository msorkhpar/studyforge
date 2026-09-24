"""Mirror of `src/studyforge/validate/source/membership.py` (R12, `W248`, `W214`).

⛔ **A stray beneath the archive root is refused by name, never skipped.** Both
ways: a planted file turns `validate` RED and names itself, and an archive
laid out by the adapter scaffold's own `Layout` reads clean.

⛔ **And the other direction (`W214`): a file the archive DECLARES and does not
hold is refused by name too.** Both ways again — declared media written where
`Layout.unit_files` puts it passes, and media that is absent, written inside a
variant, or named by no path at all is refused.
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
from studyforge.validate.source import (
    RULE_ARCHIVE_STRAY,
    RULE_MEDIA_MISSING,
    archive_members,
)
from tests.studyforge.validate import corpora
from tests.support import repository_root

STRAY = RULE_ARCHIVE_STRAY

#: The one container every corpus in this module holds, and the variant it
#: declares. ⛔ **Declared once, here, because every path below is asked of
#: `Layout` at this address rather than spelled** (`W322`): the address and the
#: variant are the corpus's own data, and the geography around them —
#: `archive/`, `raw/`, `units/`, `unit-NN`, and each filename — is the layout's.
ADDRESS = Address(["demo"])
VARIANT = "prose"


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
    # ⭐ The document is asked of `Layout`; the place it is COPIED to is not a
    # place any layout produces — that is the whole defect — so it stays spelled.
    good = Layout(root).document(ADDRESS, VARIANT, 1, "lesson", 1)
    plant(root, f"{ARCHIVE_DIRNAME}/demo/raw/prose/lesson-2.json", good.read_text("utf-8"))
    report = validate(root)
    assert "identity" in report.rules
    assert STRAY not in report.rules


def test_nothing_beneath_a_map_that_did_not_parse_is_judged_twice(tmp_path):
    # ⛔ `run` already says no document there was read. A stray finding per
    # file would be N findings for one broken map.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    Layout(root).container_map(ADDRESS).write_text("{", encoding="utf-8")
    plant(root, f"{ARCHIVE_DIRNAME}/demo/notes.md")
    report = validate(root)
    assert "container" in report.rules
    assert STRAY not in report.rules


def test_a_stray_is_never_read_as_material_even_when_the_manifest_includes_it(tmp_path):
    # ⛔ Refused, never resolved: no precedence lets `include` claim it.
    manifest = {**corpora.MANIFEST, "content": {"include": ["src/*.md", f"{ARCHIVE_DIRNAME}/*"]}}
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    Layout(root).manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    where = plant(root, f"{ARCHIVE_DIRNAME}/notes.md")
    report = validate(root)
    assert strays(root) == [where]
    # ⛔ And the scan never reads beneath the root: without its skip, the plan's
    # `archive/` line makes every file there generated output the manifest
    # includes, which reads as `contested` (plant P7 survived without this).
    assert [f.rule for f in report.findings] == [STRAY], [f.line() for f in report.findings]


# --------------------------------------------------------------------------
# ⭐ an adapter-written archive reads clean
# --------------------------------------------------------------------------


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
        variant=VARIANT,
        ingested="2026-01-05",
        units=(Unit(n=1, title="Unit 1", practices=1, origin="src/one.md"),),
    )
    _write(layout.container_map(ADDRESS), render_map(container))
    for kind in ("lesson", "practice"):
        document = build(
            source="demo",
            address=ADDRESS,
            variant=VARIANT,
            unit=1,
            kind=kind,
            ordinal=1,
            ingested="2026-01-05",
            title="Unit 1",
            blocks=corpora.BLOCKS,
        )
        _write(layout.document(ADDRESS, VARIANT, 1, kind, 1), render_document(document))
    _write(layout.unit_files(ADDRESS, 1) / "media" / "diagram.svg", "<svg/>\n")
    # ⛔ `layout.content`, not the directory plus a typed filename (`W322`): the
    # overlay's name is the contract's, and a test that spells it is a second
    # producer of an address `src/` computes in one place.
    _write(layout.content(ADDRESS, 1), "{}\n")
    report = validate(root)
    assert STRAY not in report.rules, [f.line() for f in report.findings]
    assert len(archive_members(read(root))) == 3


@pytest.mark.parametrize("name", ["depth1", "depth2", "shared-origin"])
def test_the_shipped_archives_hold_no_stray(name):
    # ⭐ Files somebody else wrote, including `units/` media and an overlay.
    assert strays(repository_root() / "tests/fixtures" / name) == []


# --------------------------------------------------------------------------
# ⛔ W214 — a declared file the archive does not hold is refused by name
# --------------------------------------------------------------------------


#: One entry of `assets` or `attachments`, whose `local` is the only half a
#: page addresses. ⚠️ The digest and the byte count are not this check's
#: question and are fabricated here.
def entry(local, kind="image"):
    """One media entry naming `local`."""
    return {
        "remote": None,
        "local": local,
        "sha256": "0" * 64,
        "bytes": 7,
        "content_type": "image/svg+xml",
        "kind": kind,
    }


def declaring(root: Path, **overrides) -> Path:
    """The smallest corpus whose one document declares a media entry."""
    return corpora.one_unit(root, source=corpora.SOURCE, **overrides)


def missing(root: Path) -> list[str]:
    """Every `media-missing` message `validate` reports, as it words them."""
    return [f.message for f in validate(root).findings if f.rule == RULE_MEDIA_MISSING]


def test_declared_media_written_where_the_layout_says_reads_clean(tmp_path):
    # ⭐ The passing half, and it uses `Layout` rather than a typed path: the
    # check and the writer agree because both asked the same module.
    root = declaring(
        tmp_path / "c",
        assets=[entry("media/diagram.svg")],
        attachments=[entry("media/small-graph.ttl", kind="dataset")],
    )
    home = Layout(root).unit_files(ADDRESS, 1)
    _write(home / "media" / "diagram.svg", "<svg/>\n")
    _write(home / "media" / "small-graph.ttl", "@prefix x: <x:> .\n")
    report = validate(root)
    assert report.ok, [f.line() for f in report.findings]


def test_a_declared_asset_that_was_never_written_is_named_and_refused(tmp_path):
    root = declaring(tmp_path / "c", assets=[entry("media/diagram.svg")])
    report = validate(root)
    assert not report.ok
    assert [f.rule for f in report.findings] == [RULE_MEDIA_MISSING]
    assert "media/diagram.svg" in missing(root)[0]
    assert "units/unit-01/media/diagram.svg" in missing(root)[0]


def test_a_declared_attachment_that_was_never_written_is_refused_too(tmp_path):
    # ⛔ One entry vocabulary, not two: the lists differ in what a page DOES
    # with them, never in what they hold, so one check covers both.
    root = declaring(tmp_path / "c", attachments=[entry("data/set.csv", kind="dataset")])
    assert [f.rule for f in validate(root).findings] == [RULE_MEDIA_MISSING]
    assert "data/set.csv" in missing(root)[0]


def test_media_written_inside_the_variant_is_refused_where_it_is_and_where_it_is_not(tmp_path):
    """⛔ The `W214` defect exactly: an adapter that wrote media under `raw/`.

    ⭐ Two findings, and they are two different true statements: the file that
    is there is read by nothing, and the file that was declared is not there.
    ⚠️ Before this check the first was the only one, and a stray beside a
    document is easy to read as untidiness rather than as a broken page.
    """
    root = declaring(tmp_path / "c", assets=[entry("media/diagram.svg")])
    _write(
        Layout(root).unit_dir(ADDRESS, VARIANT, 1) / "media" / "diagram.svg",
        "<svg/>\n",
    )
    assert set(validate(root).rules) == {RULE_MEDIA_MISSING, STRAY}


def test_an_entry_naming_no_file_is_refused_rather_than_skipped(tmp_path):
    # ⛔ The build refuses this one outright — `a media block names the file it
    # shows, and this one names nothing` — so `validate` may not pass it.
    root = declaring(tmp_path / "c", assets=[{**entry("media/x.svg"), "local": "  "}])
    assert [f.rule for f in validate(root).findings] == [RULE_MEDIA_MISSING]
    assert "names no file" in missing(root)[0]


def test_a_local_that_is_not_a_location_inside_the_unit_is_refused_without_quoting_it(tmp_path):
    # ⛔ R7: every shape refused here is a candidate home directory, so the
    # refusal names the fault and never the value. ⚠️ Fabricated, and it leaves
    # the source root, which is what `sourcepath` refuses it for.
    escaping = "../../elsewhere/diagram.svg"
    root = declaring(tmp_path / "c", assets=[entry(escaping)])
    said = missing(root)
    assert [f.rule for f in validate(root).findings] == [RULE_MEDIA_MISSING]
    assert escaping not in said[0], "a refusal quoted the value it refused (R7)"
    assert "leaving the source root" in said[0]


def test_media_skipped_is_a_state_and_not_a_shortfall(tmp_path):
    # ⭐ `archive.document`: an ingest that named its media and deliberately did
    # not fetch it. The marker is IN the document, so nothing is inferred.
    root = declaring(
        tmp_path / "c",
        assets=[entry("media/diagram.svg")],
        media_skipped=True,
    )
    assert validate(root).ok


def test_a_document_that_disagrees_with_its_directory_is_not_judged_twice(tmp_path):
    # ⛔ `identity` already refuses the disagreement. Resolving a file against a
    # directory derived from it would report one defect under two rules.
    root = declaring(tmp_path / "c", assets=[entry("media/diagram.svg")], unit=2)
    assert set(validate(root).rules) == {"identity", "unit-missing"}


@pytest.mark.parametrize("name", ["depth1", "depth2", "shared-origin"])
def test_the_shipped_archives_hold_every_file_they_declare(name):
    # ⭐ Files somebody else wrote: `depth1` declares an asset and an
    # attachment, and `depth2`'s third unit declares `media_skipped`.
    report = validate(repository_root() / "tests/fixtures" / name)
    assert RULE_MEDIA_MISSING not in report.rules, [f.line() for f in report.findings]
