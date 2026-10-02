"""A corpus that declares reading modes asks for one on a first visit, in a real browser.

⭐ **Every clause drives the real question and the real switch.** A corpus with
two languages and three modes is built the way a build does, and its pages are
opened in the headless browser: served from a loopback origin where the choice
is kept, and over `file://` where it is not.

⛔ **Each clause is asserted both ways (R12).** The question lists exactly the
declared modes; a choice survives a reload and a second page of another kind;
a mode change shows the sections of the mode's language and hides the others and
the outline's lines that point at them; scripts off read the default mode with
no question and no switch; a page whose storage is refused shows the default
mode and asks nothing; and a corpus that declares no modes shows no question and
no switch at all.

⚠️ **The browser profile outlives the tab**, so each reading clears the stores
before it and after it.

## What this module does NOT read

The locked and greyed entries of the index and the rail, the tabbed examples and
the practice list of a mode are other rows' clauses.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate.test_section_language import build
from tests.studyforge.validate.test_languages import READING, document
from tests.visual import served, site
from tests.visual.page import NARROW, WIDE, OpenPage

MODES = [
    *READING["modes"],
    {
        "id": "both",
        "label": "Aa with Bb",
        "summary": "Aa first, then Bb",
        "prose": "aa",
        "tabs": ["aa", "bb"],
        "practices": ["aa", "bb"],
    },
]
DECLARED = {**READING, "modes": MODES}

COMMON = [{"type": "para", "text": "Common words."}]
BLOCKS = {
    "aa": [{"type": "para", "text": "AA WORDS"}, {"type": "code", "lang": "aa", "text": "a != b"}],
    "bb": [{"type": "para", "text": "BB WORDS"}],
}
DOCUMENTS = [
    document(ordinal=1, blocks=COMMON),
    document(ordinal=2, lang="aa", blocks=BLOCKS["aa"]),
    document(ordinal=3, lang="bb", blocks=BLOCKS["bb"]),
]

UNIT = ".studyforge/demo/units/unit-01/unit-01-unit-1.unit.html"
CONTAINER = ".studyforge/demo/demo.section.html"
INDEX = "index.html"

SWITCH = '[data-section="mode"]'
QUESTION = '[data-section="mode-question"]'

#: The sections a reader can see, by their `data-section`, and the outline's lines.
VISIBLE = """
Array.from(document.querySelectorAll('main section[data-section]'))
  .filter(s => getComputedStyle(s).display !== 'none')
  .map(s => s.getAttribute('data-section'))
"""
OUTLINE = """
Array.from(document.querySelectorAll('nav[aria-label="Outline"] li'))
  .filter(li => getComputedStyle(li).display !== 'none')
  .map(li => li.getAttribute('data-lang') || 'common')
"""
ASKING = """
(() => {
  const q = document.querySelector('<q>');
  if (!q) return null;
  const box = q.getBoundingClientRect();
  return {
    shown: !q.hidden && getComputedStyle(q).display !== 'none',
    options: Array.from(q.querySelectorAll('button')).map(b => [
      b.getAttribute('data-mode-choice'),
      b.querySelector('strong').textContent,
      b.querySelector('span').textContent]),
    left: box.left, right: box.right, width: window.innerWidth,
    focused: q.contains(document.activeElement)
  };
})()
""".replace("<q>", QUESTION)
SWITCHED = """
(() => {
  const g = document.querySelector('<s>');
  if (!g) return null;
  return {
    shown: !g.hidden && getComputedStyle(g).display !== 'none',
    pressed: Array.from(g.querySelectorAll('button'))
      .filter(b => b.getAttribute('aria-pressed') === 'true')
      .map(b => b.getAttribute('data-mode-choice')),
    choices: Array.from(g.querySelectorAll('button')).map(b => b.getAttribute('data-mode-choice')),
    mode: document.documentElement.getAttribute('data-mode')
  };
})()
""".replace("<s>", SWITCH)
CLEAR = "(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()"
REFUSED = """
Object.defineProperty(window, 'localStorage', { get() { throw new Error('refused'); } });
Object.defineProperty(window, 'sessionStorage', { get() { throw new Error('refused'); } });
"""


@pytest.fixture(scope="module")
def modal(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A corpus that declares three modes, built into a tree."""
    return build(tmp_path_factory.mktemp("modes-site"), "m", DOCUMENTS, DECLARED)


@pytest.fixture(scope="module")
def plain(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The same corpus declaring no modes."""
    return build(tmp_path_factory.mktemp("plain-site"), "p", DOCUMENTS, {})


@pytest.fixture(scope="module")
def origin(modal: Path) -> Iterator[served.Served]:
    with served.serving(site.Site(modal.parent), corpus=modal.name) as running:
        yield running


@pytest.fixture
def fresh(open_page: OpenPage, origin: served.Served) -> Iterator[OpenPage]:
    """A tab on the served unit page whose stores are empty, cleared again afterwards."""
    open_page.resize(*WIDE)
    open_page.open(f"{origin.origin}/{UNIT}")
    open_page.evaluate(CLEAR)
    yield open_page
    open_page.evaluate(CLEAR)


def reopen(page: OpenPage, origin: served.Served, where: str = UNIT, **kwargs: object) -> None:
    page.open(f"{origin.origin}/{where}", **kwargs)


def test_the_first_visit_asks_and_lists_exactly_the_declared_modes(
    fresh: OpenPage, origin: served.Served
) -> None:
    reopen(fresh, origin)
    asking = fresh.evaluate(ASKING)
    assert asking["shown"] is True
    assert asking["options"] == [
        ["only-aa", "Aa", "Aa only"],
        ["only-bb", "Bb", "Bb only"],
        ["both", "Aa with Bb", "Aa first, then Bb"],
    ]
    assert asking["focused"] is True
    switched = fresh.evaluate(SWITCHED)
    assert switched["shown"] is True and switched["choices"] == [m["id"] for m in MODES]
    assert switched["pressed"] == ["only-aa"], "until it is answered the page is the default mode"
    assert fresh.evaluate(VISIBLE) == ["prose", "prose-2"]


def test_a_choice_shows_its_language_and_survives_a_reload_and_a_page_of_another_kind(
    fresh: OpenPage, origin: served.Served
) -> None:
    reopen(fresh, origin)
    fresh.evaluate(f"document.querySelector('{QUESTION} [data-mode-choice=\"only-bb\"]').click()")
    assert fresh.evaluate(ASKING)["shown"] is False
    assert fresh.evaluate(VISIBLE) == ["prose", "prose-3"]
    assert fresh.evaluate(OUTLINE) == ["common", "bb"], "the other language's line stays"
    for where in (UNIT, CONTAINER, INDEX, UNIT):
        reopen(fresh, origin, where)
        assert fresh.evaluate(ASKING)["shown"] is False, f"{where} asked again"
        assert fresh.evaluate(SWITCHED)["pressed"] == ["only-bb"], where
    assert fresh.evaluate(VISIBLE) == ["prose", "prose-3"]


def test_the_switch_changes_the_mode_in_place_and_both_ways(
    fresh: OpenPage, origin: served.Served
) -> None:
    reopen(fresh, origin)
    for mode, shown in (("only-bb", "prose-3"), ("only-aa", "prose-2"), ("both", "prose-2")):
        fresh.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"{mode}\"]').click()")
        assert fresh.evaluate(VISIBLE) == ["prose", shown], mode
        assert fresh.evaluate(SWITCHED)["pressed"] == [mode]
    reopen(fresh, origin)
    assert fresh.evaluate(SWITCHED)["pressed"] == ["both"]


def test_a_stored_word_that_is_not_a_declared_mode_is_asked_again(
    fresh: OpenPage, origin: served.Served
) -> None:
    fresh.evaluate(
        "localStorage.setItem('studyforge.display.v1', JSON.stringify("
        "{version: 1, display: {mode: 'nonsense'}}))"
    )
    reopen(fresh, origin)
    assert fresh.evaluate(ASKING)["shown"] is True
    assert fresh.evaluate(SWITCHED)["pressed"] == ["only-aa"]


def test_the_question_can_be_put_away_with_escape_and_returns_next_visit(
    fresh: OpenPage, origin: served.Served
) -> None:
    reopen(fresh, origin)
    fresh.press("Escape")
    assert fresh.evaluate(ASKING)["shown"] is False
    reopen(fresh, origin)
    assert fresh.evaluate(ASKING)["shown"] is True


def test_the_question_fits_a_phone(open_page: OpenPage, origin: served.Served) -> None:
    open_page.resize(360, 640)
    reopen(open_page, origin)
    open_page.evaluate(CLEAR)
    reopen(open_page, origin)
    asking = open_page.evaluate(ASKING)
    assert asking["shown"] and asking["left"] >= 0 and asking["right"] <= asking["width"]
    open_page.evaluate(CLEAR)


def test_scripts_off_reads_the_default_mode_and_shows_no_question_and_no_switch(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{origin.origin}/{UNIT}", scripts=False)
    assert open_page.evaluate(VISIBLE) == ["prose", "prose-2"]
    assert open_page.evaluate(ASKING)["shown"] is False
    assert open_page.evaluate(SWITCHED)["shown"] is False
    assert open_page.evaluate(SWITCHED)["mode"] == "only-aa"


def test_a_page_whose_storage_is_refused_reads_the_default_and_asks_nothing(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument", {"source": REFUSED}, session=open_page.session
    )
    reopen(open_page, origin)
    probe = "(() => { try { localStorage; return 'open'; } catch (e) { return 'refused'; } })()"
    assert open_page.evaluate(probe) == "refused"
    assert open_page.evaluate(ASKING)["shown"] is False
    assert open_page.evaluate(VISIBLE) == ["prose", "prose-2"]
    assert open_page.evaluate(SWITCHED)["shown"] is True
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-bb\"]').click()")
    assert open_page.evaluate(VISIBLE) == ["prose", "prose-3"], "the switch still changes the page"


def test_opened_from_a_file_the_question_is_asked_on_every_load(
    open_page: OpenPage, modal: Path
) -> None:
    url = f"file://{modal / UNIT}"
    open_page.open(url)
    open_page.evaluate(CLEAR)
    for _ in range(2):
        open_page.open(url)
        assert open_page.evaluate(ASKING)["shown"] is True
        open_page.evaluate(
            f"document.querySelector('{QUESTION} [data-mode-choice=\"only-bb\"]').click()"
        )
        assert open_page.evaluate(VISIBLE) == ["prose", "prose-3"]
    open_page.evaluate(CLEAR)


def test_a_corpus_declaring_no_modes_has_no_question_no_switch_and_no_attribute(
    open_page: OpenPage, plain: Path
) -> None:
    open_page.open(f"file://{plain / UNIT}")
    assert open_page.evaluate(ASKING) is None
    assert open_page.evaluate(SWITCHED) is None
    assert open_page.evaluate("document.documentElement.hasAttribute('data-mode')") is False
    assert open_page.evaluate("document.querySelectorAll('script[src]').length") == 1


def test_code_still_draws_no_ligature_on_a_modes_page(
    fresh: OpenPage, origin: served.Served
) -> None:
    reopen(fresh, origin)
    reading = fresh.evaluate(
        "(() => { const c = document.querySelector('pre'); const s = getComputedStyle(c);"
        " return [s.fontVariantLigatures, s.fontFeatureSettings]; })()"
    )
    assert reading[0] == "none" and '"liga" 0' in reading[1]
