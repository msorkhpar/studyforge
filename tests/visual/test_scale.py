"""The page at scale, in a real browser: the progress strip fits, and code draws no ligature.

⛔ **A course of sixty top-level groups is the reading, and no committed fixture
has one.** The strip gives each top-level group one segment with a floor under it,
so the failure it can have — segments whose floors add up to more than the
column — is invisible at the two or three groups a fixture declares. ⭐ So
this module plants a corpus of exactly that shape through the index fixtures'
own `planted`, writes its root index beside the shipped assets, and reads it.

⛔ **Every clause has a control, and the control must fail.** The strip is read
again with the one-size floor every segment would have without the shared
`--segments` count; the ligature is read again with ligatures forced on. A
control that passes is a reading that cannot see its failure.

## ⚠️ Why the ligature is read as two pictures and never as a width

JetBrains Mono draws a ligature in the same two cells as the characters it
replaces, so a width cannot tell `!=` from a not-equal sign. ⭐ The operator is
captured as shipped and again with ligatures turned off on that one span:
identical pictures mean no ligature was drawn.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from studyforge.render import pageassets
from tests.studyforge.render.index.indexes import planted
from tests.visual import site
from tests.visual.page import NARROW, WIDE, OpenPage

#: The groups the strip must fit: a course of sixty modules filed flat. ⚠️ Past
#: the forty-five a real course has, so the one-size floor overflows the column at
#: both widths and the control below fails at both.
GROUPS = 60

#: How many units each group holds. ⚠️ Any count: the segments are equal here.
UNITS = 4

#: The strip, as `lists.css` targets it.
STRIP = 'section[aria-label="Progress"] ol'

#: Where the strip's segments end, against the column it sits in.
STRIP_READING = f"""(() => {{
  const strip = document.querySelector('{STRIP}');
  if (!strip) return null;
  const column = strip.parentElement.getBoundingClientRect();
  const right = Math.max(...[...strip.children].map(li => li.getBoundingClientRect().right));
  return {{segments: strip.children.length, right: right, column: column.right,
          page: document.documentElement.scrollWidth, window: window.innerWidth}};
}})()"""

#: The control: every segment given the one-size floor, with no share of the row.
ONE_SIZE_FLOOR = (
    f"document.querySelectorAll('{STRIP} > li')"
    ".forEach(li => li.style.minWidth = '.9rem');"
)

#: How far a laid-out edge may sit past another and still be touching.
TOUCHING = 1.0

#: An operator written into the page's first code listing, in its own span.
OPERATOR = """(() => {
  const code = document.querySelector('figure.code pre code');
  if (!code) return null;
  const span = document.createElement('span');
  span.id = 'probe-operator';
  span.textContent = '!=';
  code.appendChild(span);
  document.documentElement.style.scrollBehavior = 'auto';
  span.scrollIntoView({block: 'center', behavior: 'instant'});
  const r = span.getBoundingClientRect();
  return {x: r.x + window.scrollX, y: r.y + window.scrollY, width: r.width, height: r.height,
          scale: 4};
})()"""

#: What the probe span is set to for each picture: its ligatures, then its features.
SETTINGS = {
    "off": ("none", '"liga" 0, "calt" 0'),
    "on": ("normal", "normal"),
}


@pytest.fixture(scope="module")
def many_groups(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A root index of `GROUPS` top-level groups, written beside the shipped assets."""
    built = planted((GROUPS, UNITS))
    root = tmp_path_factory.mktemp("scale")
    page = root / str(built.placement.shared.root_index)
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_bytes(built.render())
    assets = root / str(built.placement.shared.assets)
    assets.mkdir(parents=True, exist_ok=True)
    for name, body in pageassets.written_files().items():
        (assets / name).write_text(body, encoding="utf-8")
    return page


def _strip(open_page: OpenPage, page: Path, size: tuple[int, int], control: str = "") -> dict:
    open_page.resize(*size)
    open_page.open(page.as_uri())
    if control:
        open_page.evaluate(control)
    reading = open_page.evaluate(STRIP_READING)
    assert reading is not None, "the index drew no progress strip, so this reads nothing"
    assert reading["segments"] == GROUPS, reading
    return reading


@pytest.mark.parametrize("size", [WIDE, NARROW], ids=["wide", "narrow"])
def test_the_strip_of_sixty_groups_ends_inside_its_column(open_page, many_groups, size):
    reading = _strip(open_page, many_groups, size)
    assert reading["right"] <= reading["column"] + TOUCHING, reading
    assert reading["page"] <= reading["window"], reading


@pytest.mark.parametrize("size", [WIDE, NARROW], ids=["wide", "narrow"])
def test_the_control_a_one_size_floor_overflows_the_column(open_page, many_groups, size):
    reading = _strip(open_page, many_groups, size, ONE_SIZE_FLOOR)
    assert reading["right"] > reading["column"] + TOUCHING, (
        f"the one-size floor still fits, so the clause above cannot see an overflow: {reading}"
    )


def _operator(open_page: OpenPage, url: str) -> dict[str, str]:
    """The operator's picture as shipped, and with ligatures turned off and on."""
    open_page.open(url)
    box = open_page.evaluate(OPERATOR)
    assert box is not None, "the page carries no code listing, so this reads nothing"
    pictures = {"shipped": _picture(open_page, box)}
    for name, (ligatures, features) in SETTINGS.items():
        open_page.evaluate(
            "(() => { const s = document.getElementById('probe-operator');"
            f" s.style.fontVariantLigatures = '{ligatures}';"
            f" s.style.fontFeatureSettings = '{features}'; }})()"
        )
        pictures[name] = _picture(open_page, box)
    return pictures


def _picture(open_page: OpenPage, box: dict) -> str:
    open_page.evaluate(
        "new Promise(done => requestAnimationFrame(() => requestAnimationFrame(() => done(true))))"
    )
    shot = open_page.browser.call(
        "Page.captureScreenshot", {"format": "png", "clip": box}, session=open_page.session
    )
    return base64.b64decode(shot["data"]).hex()


def test_code_draws_its_operator_as_the_characters_and_the_control_draws_a_ligature(
    open_page, built_site
):
    url = built_site.url(
        next(
            built.name
            for built in site.pages_built()
            if built.kind == site.UNIT and b'<figure class="code"' in built.body
        )
    )
    pictures = _operator(open_page, url)
    assert pictures["on"] != pictures["off"], "no ligature drawn even when forced on: blind"
    assert pictures["shipped"] == pictures["off"], "the shipped page draws `!=` joined"
