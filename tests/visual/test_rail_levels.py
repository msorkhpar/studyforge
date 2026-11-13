"""The rail reads as levels, in a real browser: indented, hung, and never a level twice.

⭐ **Three things the bytes cannot show**, each read off the live layout of a built
depth-2 corpus whose `basics` section holds ONE module and whose `advanced`
section holds two:

- a module's summary starts further in than its section's, so the two never
  read as siblings;
- a summary that wraps starts its second line under its first word, not under
  the disclosure mark, so the mark stays the one thing in its column;
- the section holding one module is ONE disclosure, its module's own row.

⛔ **Every reading is a comparison between two boxes on the same page**, never a
pixel figure typed here, and each of the first two is asserted the other way on
the same page with the declaration that makes it true taken off: a check that
has only ever seen the correct stylesheet has not been shown to notice the
defect it exists for.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.generate import read_corpus, unit_location, write_site
from tests.support import repository_root
from tests.visual.page import NARROW, WIDE, OpenPage

#: The fixture corpus: `basics` holds one module, `advanced` holds two.
CORPUS = "depth2"

#: The section the reader is in on the page every clause opens, and the title of
#: the section that holds one module.
OPEN_SECTION = "advanced"
LONE_TITLE = "Basics"

#: The region under test, as `chrome.css` and `test_rail.py` spell it.
RAIL = 'nav[aria-label="Containers"]'

#: A title long enough to wrap in the rail at both widths. ⛔ Words, not one
#: unbroken run: the clause is about where a wrapped LINE starts.
LONG = (
    "Engineering the optimization service, with other modeling frameworks and solvers, "
    "and a title long enough to wrap even where the rail is the column's whole width"
)

#: Two edges closer than this are the same edge — `test_rail.TOUCHING`.
TOUCHING = 0.5

#: Where the text of one summary starts, line by line, and where its box starts.
#: ⭐ A range over the summary's own text, so the reading is the glyphs and not
#: a box the mark sits inside.
TEXT_LINES = """
(summary => {
  const range = document.createRange();
  range.selectNodeContents(summary);
  const lines = [];
  for (const rect of range.getClientRects()) {
    if (rect.width < 1) continue;
    const last = lines[lines.length - 1];
    if (!last || rect.top > last.top + 2) lines.push({left: rect.left, top: rect.top});
    else last.left = Math.min(last.left, rect.left);
  }
  return {lines: lines, box: summary.getBoundingClientRect().left};
})"""

#: The section row and one of its module rows, both open, on the open page.
NESTED = (
    f"(() => {{ const read = {TEXT_LINES};"
    f" const group = Array.from(document.querySelectorAll('{RAIL} li:not([data-readable])'))"
    "  .find(li => li.querySelector('li[data-readable]'));"
    " if (!group) return null;"
    " group.querySelector('details').open = true;"
    " return {group: read(group.querySelector('summary')),"
    "  module: read(group.querySelector('li[data-readable] > details > summary'))}; })()"
)

#: One module summary, given the long title, read line by line.
WRAPPED = (
    f"(() => {{ const read = {TEXT_LINES};"
    f" const summary = document.querySelector('{RAIL} li li[data-readable] > details > summary');"
    " if (!summary) return null;"
    " const words = summary.querySelector('a') || summary;"
    f" words.textContent = {LONG!r};"
    " return read(summary); })()"
)


@dataclass(frozen=True)
class Built:
    """The corpus built onto disk, and the unit page every clause opens."""

    page: Path

    @property
    def url(self) -> str:
        """The page's `file://` URL: R8's floor is a double-clicked file."""
        return "file://" + str(self.page)


@pytest.fixture(scope="session")
def built(tmp_path_factory: pytest.TempPathFactory) -> Built:
    """The fixture corpus, built once, opened on a unit inside the two-module section."""
    root = tmp_path_factory.mktemp("visual-rail-levels")
    source = repository_root() / "tests" / "fixtures" / CORPUS
    write_site(source, root)
    corpus = read_corpus(source)
    inside = [unit for unit in corpus.units if unit.key.startswith(OPEN_SECTION + "/")]
    assert inside, f"{CORPUS} declares no unit under {OPEN_SECTION}"
    return Built(page=root / str(unit_location(corpus, inside[0]).page))


def _open(page: OpenPage, built: Built, width: tuple[int, int], scheme: str = "light") -> None:
    page.resize(*width)
    page.open(built.url, scheme=scheme, scripts=False)
    # ⚠️ The narrow fold is closed by the page script only; with none it is open.
    page.evaluate(f"document.querySelector('{RAIL} > details').open = true")


def _nested(page: OpenPage) -> dict:
    found = page.evaluate(NESTED)
    assert found is not None, "the rail holds no section with modules, so this reads nothing"
    return dict(found)  # type: ignore[arg-type]


@pytest.mark.parametrize("width", [WIDE, NARROW], ids=["wide", "narrow"])
@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_a_module_summary_starts_further_in_than_its_sections(
    open_page: OpenPage, built: Built, width: tuple[int, int], scheme: str
) -> None:
    _open(open_page, built, width, scheme)
    read = _nested(open_page)
    group, module = read["group"], read["module"]

    assert module["box"] > group["box"] + TOUCHING, (
        f"a module's summary box starts at {module['box']:.2f}px and its section's at "
        f"{group['box']:.2f}px, so the two read as siblings"
    )
    assert module["lines"][0]["left"] > group["lines"][0]["left"] + TOUCHING, read


def test_the_indent_check_fails_with_the_indent_taken_off(
    open_page: OpenPage, built: Built
) -> None:
    # ⛔ The control: the same page with the group's list flush again.
    _open(open_page, built, WIDE)
    open_page.evaluate(
        f"document.querySelectorAll('{RAIL} ol').forEach(ol => ol.style.paddingLeft = '0')"
    )
    read = _nested(open_page)
    assert abs(read["module"]["box"] - read["group"]["box"]) <= TOUCHING, read


@pytest.mark.parametrize("width", [WIDE, NARROW], ids=["wide", "narrow"])
@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_a_wrapped_summary_starts_its_second_line_under_its_first_word(
    open_page: OpenPage, built: Built, width: tuple[int, int], scheme: str
) -> None:
    _open(open_page, built, width, scheme)
    read = open_page.evaluate(WRAPPED)
    assert read is not None, "the rail has no module summary, so this reads nothing"
    lines = dict(read)["lines"]  # type: ignore[index]

    assert len(lines) >= 2, f"the long title did not wrap at {width[0]}px: {lines}"
    first, second = lines[0]["left"], lines[1]["left"]
    assert second == pytest.approx(first, abs=TOUCHING), (
        f"the second line starts at {second:.2f}px and the first line's text at {first:.2f}px, "
        "so the wrap runs back under the disclosure mark"
    )
    box = dict(read)["box"]  # type: ignore[index]
    assert second > box + TOUCHING, "the text starts at the summary's edge, where the mark is"


def test_the_hanging_check_fails_without_the_hanging_indent(
    open_page: OpenPage, built: Built
) -> None:
    # ⛔ The control: no hanging indent, so the mark pushes the first line only.
    _open(open_page, built, WIDE)
    open_page.evaluate(
        f"document.querySelectorAll('{RAIL} summary')"
        ".forEach(s => { s.style.paddingLeft = '0'; s.style.textIndent = '0'; })"
    )
    lines = dict(open_page.evaluate(WRAPPED))["lines"]  # type: ignore[arg-type]
    assert len(lines) >= 2, lines
    assert abs(lines[1]["left"] - lines[0]["left"]) > TOUCHING, lines


@pytest.mark.parametrize("width", [WIDE, NARROW], ids=["wide", "narrow"])
def test_a_section_holding_one_module_is_one_disclosure(
    open_page: OpenPage, built: Built, width: tuple[int, int]
) -> None:
    _open(open_page, built, width)
    counts = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{RAIL} > details > ol > li'))"
        ".map(li => [li.querySelector('summary').textContent.trim(),"
        " li.querySelectorAll('details').length,"
        " li.querySelector('summary small') ? li.querySelector('summary small').textContent : ''])"
    )
    rows = list(counts)  # type: ignore[arg-type]
    assert len(rows) == 2, rows
    lones = [row for row in rows if row[2]]
    assert len(lones) == 1, f"not one row names a lone module: {rows}"
    (lone, lone_count, lone_module), (_, two_count, _) = lones[0], next(
        row for row in rows if not row[2]
    )

    assert LONE_TITLE in lone, rows
    assert lone_count == 1, f"the one-module section {lone!r} is {lone_count} disclosures"
    assert lone_module, f"the one-module section {lone!r} does not name its module"
    # ⭐ The other way: a section holding two modules is still a level of its own.
    assert two_count == 3, rows
