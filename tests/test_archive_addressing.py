"""No test spells an archive address — the three sites `W322` received, and the instrument.

⛔ **`W198` removed the composition from `src/`; three test sites kept it**
(`W198/4`, `W198/5`, `W298/2`), so the one contract had a single producer in
`src/` and three in `tests/`. ⚠️ A test that invents an address is a build that
invents it, one register over: it passes for exactly as long as the constant is
what the test happens to say, and goes silently wrong the day the constant
moves — without anything going RED to say so.

**What this module asserts**, both ways, for each of the three sites named in
`SITES`:

* ⛔ none of them **joins** a segment or a filename `src/` owns — asserted by
  reading their own syntax, and the instrument is watched catching a planted
  one (Ruling 11);
* ⭐ each of them **follows** the owner: the overlay pattern and the unit's home
  are re-derived when `CONTENT_FILENAME` or the `units/` segment moves;
* ⛔ and the walk that uses them is asserted to **find** the overlay the
  fixtures ship, because an empty walk is the failure that hides — a moved
  filename would otherwise leave every overlay check green against nothing.

⚠️ **What a literal is allowed to be, and it is not a loophole.** A path that
no layout produces — a stray planted where nothing reads it, a document copied
to the wrong depth — has no producer to ask, and spelling it is the whole point
of the test that plants it. The instrument therefore reads *joins*, which is
how a path is built, and not every string in the file.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from studyforge.address import FIRST_ORDINAL, Address, unit_name
from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.corpus.placement import ARCHIVE_DIRNAME, RAW_DIRNAME, UNITS_DIRNAME
from studyforge.skills.adapter import Layout
from studyforge.skills.adapter import layout as layout_module
from studyforge.unit.content import CONTENT_FILENAME
from tests.fixture_checks import FIXTURES, VALID, archive_files, containers_in, read_json
from tests.fixture_checks.addresses import (
    ORDINAL_DIGITS,
    check_overlays,
    overlay_glob,
    overlays_in,
    unit_files_in,
)
from tests.fixture_checks.media import check_media
from tests.support import repository_root

#: ⛔ **The three sites `W322` received, by path.** Named rather than globbed:
#: the row measured these three, and a scan that widened itself would be
#: asserting something nobody agreed to.
SITES = (
    "tests/studyforge/validate/source/test_membership.py",
    "tests/fixture_checks/addresses.py",
    "tests/fixture_checks/media.py",
)

#: Every spelling of the corpus's geography that a module in `src/` owns. ⛔
#: Imported, never retyped — this list going stale would make the instrument
#: agree with a literal it was written to refuse.
OWNED = (
    ARCHIVE_DIRNAME,
    RAW_DIRNAME,
    UNITS_DIRNAME,
    CONTAINER_FILENAME,
    CONTENT_FILENAME,
    MANIFEST_FILENAME,
)

#: A unit directory, whatever padding `unit_name` gives it. ⭐ Derived the same
#: way `overlay_glob` derives its wildcard — from `unit_name`'s own output, with
#: the digits it filled in replaced — so a widened ordinal is still recognised.
UNIT_SEGMENT = re.compile(ORDINAL_DIGITS.sub(r"[0-9]+", unit_name(FIRST_ORDINAL)) + r"\Z")

#: The overlay the shipped fixtures carry, and where it sits. ⚠️ `depth2` is the
#: corpus that has one; the address and the unit are its data, and every segment
#: between them is the layout's.
OVERLAY_FIXTURE = "depth2"
OVERLAY_ADDRESS = Address(["basics", "01-getting-started"])
OVERLAY_UNIT = 1


def joined_literals(source: str):
    """Every string literal `source` joins into a path or hands to a glob.

    ⭐ **A join, not a spelling.** `container.get("units")` reads a JSON key and
    mints no directory; `x / "units"` makes one. The discriminator is the same
    one `W298` needed for the `src/` scan, for the same reason: the word is a
    key as well as a segment, and a census that cannot tell them apart teaches
    the next office to edit the census.

    ⚠️ **Its limit, stated rather than discovered later:** it reads `pathlib`
    joins and glob patterns, which is what these files use. A path assembled
    with `os.path.join`, `"/".join` or an f-string is not seen — and an f-string
    is how the sites below deliberately spell the places that have no producer.
    """
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            operands = (node.left, node.right)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            operands = tuple(node.args) if node.func.attr in ("glob", "rglob", "joinpath") else ()
        else:
            continue
        for operand in operands:
            if isinstance(operand, ast.Constant) and isinstance(operand.value, str):
                yield operand.value


def spelled_segments(source: str) -> list[str]:
    """Every joined literal in `source` carrying a segment the framework owns."""
    found = []
    for literal in joined_literals(source):
        for part in literal.split("/"):
            if part in OWNED or UNIT_SEGMENT.match(part):
                found.append(literal)
                break
    return found


# --------------------------------------------------------------------------
# ⛔ clause 1 — no named site composes an archive path from a literal
# --------------------------------------------------------------------------


@pytest.mark.parametrize("where", SITES)
def test_a_named_site_joins_no_segment_the_framework_owns(where):
    path = repository_root() / where
    assert path.is_file(), where
    found = spelled_segments(path.read_text(encoding="utf-8"))
    assert found == [], (
        f"{where} composes an archive address from a literal; ask the type that "
        f"owns the geography — `Layout` — instead: {found}"
    )


def test_the_instrument_catches_a_spelling_put_back():
    # ⭐ Ruling 11 on the guard itself: an assertion that a mechanism refuses
    # something is worth nothing until it has been watched passing without it.
    # ⚠️ Each of these is one of the three shapes the sites actually held.
    put_back = (
        f'_write(layout.unit_files(ADDRESS, 1) / "{CONTENT_FILENAME}", "{{}}")',
        f'(root / "{ARCHIVE_DIRNAME}").rglob("{UNITS_DIRNAME}/unit-*/{CONTENT_FILENAME}")',
        f'unit_root = container_dir / "{UNITS_DIRNAME}" / "{unit_name(FIRST_ORDINAL)}"',
    )
    for source in put_back:
        assert spelled_segments(source) != [], source


def test_the_instrument_passes_what_has_no_producer_to_ask():
    # ⛔ The other direction, and it is what keeps the guard usable: a stray is
    # planted where NO layout puts anything, so there is nothing to ask and the
    # literal is the test's own subject. ⚠️ Read as a key, `units` is not a
    # segment either.
    permitted = (
        'plant(root, f"{ARCHIVE_DIRNAME}/demo/raw/prose/lesson-2.json")',
        'declared = [unit.get("n") for unit in container.get("units") or []]',
        '_write(layout.unit_files(ADDRESS, 1) / "media" / "diagram.svg", "<svg/>")',
    )
    for source in permitted:
        assert spelled_segments(source) == [], source


# --------------------------------------------------------------------------
# ⭐ clause 2 — the sites follow the owner, and the walk finds something
# --------------------------------------------------------------------------


def test_the_overlay_walk_finds_the_overlay_the_fixtures_ship():
    # ⛔ The assertion that makes a moved filename RED rather than silent. The
    # expected path is `Layout`'s own, so this compares the walk against the
    # producer and not against a second spelling.
    root = FIXTURES / OVERLAY_FIXTURE
    expected = Layout(root).content(OVERLAY_ADDRESS, OVERLAY_UNIT)
    assert expected.is_file(), "the fixture that carries an overlay no longer carries one"
    assert overlays_in(root) == [expected]
    assert list(check_overlays(root)) == []


def test_a_content_filename_that_moved_leaves_the_walk_finding_nothing(monkeypatch):
    # ⛔ The RED half, in process: the pattern follows `CONTENT_FILENAME`, so the
    # fixture's `content.json` stops matching — which is exactly what makes the
    # test above fail by name instead of walking an empty tree in silence.
    moved = "moved-overlay.json"
    monkeypatch.setattr(layout_module, "CONTENT_FILENAME", moved)
    assert overlay_glob().endswith(moved)
    assert overlays_in(FIXTURES / OVERLAY_FIXTURE) == []


def test_a_units_directory_that_moved_reaches_the_pattern_and_the_unit_home(monkeypatch):
    moved = "moved-units"
    monkeypatch.setattr(layout_module, "UNITS_DIR", moved)
    assert overlay_glob().startswith(f"{moved}/")
    assert overlays_in(FIXTURES / OVERLAY_FIXTURE) == []
    home = unit_files_in(Path("any") / "container", OVERLAY_UNIT)
    assert home.parent.name == moved


def test_a_units_directory_that_moved_turns_the_media_check_red_by_name(monkeypatch):
    # ⭐ The third site, asserted through the check that uses it: every declared
    # file is looked for where the layout NOW says, so the fixture's media reads
    # as missing rather than as found in the old place.
    container_dir, document = declaring_document()
    assert list(check_media(container_dir, document, "where")) == []
    monkeypatch.setattr(layout_module, "UNITS_DIR", "moved-units")
    rules = [rule for rule, _message in check_media(container_dir, document, "where")]
    assert rules and set(rules) == {"media-present"}


def declaring_document():
    """The first shipped `(container_dir, document)` whose document declares a local file."""
    for name in VALID:
        for container_dir, container in containers_in(FIXTURES / name):
            for _unit, _kind, _ordinal, path in archive_files(container_dir, container["variant"]):
                document = read_json(path)
                if document.get("assets") and not document.get("media_skipped"):
                    return container_dir, document
    raise AssertionError("no shipped fixture declares a local file, so this asserts nothing")
