"""A lesson's practices as a list of cards, and the one workspace a card opens in.

⭐ **The workspace, read in a browser at desktop and at phone width.** A
lesson's practices are one *Practice (n)* list of titled cards; opening a card
gives a full-screen workspace — the statement on the left, the editor on the
right, stacked at phone width — with Previous, Next and Close; and no editor
loads until a practice is opened, and one at most.

⛔ **Opened by the keyboard**, never by `click()`: a card a keyboard reader
cannot open is a practice they cannot work.

⭐ **The page is this module's own**, written beside the depth-2 unit page so
every relative asset link resolves: three practices — two code practices and a
quiz — so Next has somewhere to go and a quiz is a card too.
"""

from __future__ import annotations

import copy
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.render.page import render
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.studyforge.render.page.test_practice import QUIZ
from tests.visual import served, site
from tests.visual.page import OpenPage

#: The corpus this module borrows a document and a placement from.
CORPUS = "depth2"

#: The page this module writes beside that corpus's own unit page.
PAGE = "a-workspace.unit.html"

#: The two widths the ruling is read at: a desktop, and a phone.
DESKTOP = (1280, 800)
PHONE = (390, 844)
WIDTHS = {"desktop": DESKTOP, "phone": PHONE}

#: Seconds a reading waits for a state the page's script produces.
SETTLE = 15.0

#: How many presses a walk to a card takes before giving up.
PRESSES = 80

#: The whole workspace, as the browser holds it now.
STATE = """
(() => {
  const box = (el) => {
    if (!el || !el.checkVisibility()) return null;
    const b = el.getBoundingClientRect();
    return {top: b.top, bottom: b.bottom, left: b.left, right: b.right, width: b.width};
  };
  const shell = document.querySelector('div[data-workspace]');
  const open = Array.from(document.querySelectorAll('main > section[data-workspace-open]'));
  const statement = open.find((el) => el.hasAttribute('data-kind')) || null;
  const panel = open.find((el) => !el.hasAttribute('data-kind')) || null;
  const act = (name) => shell.querySelector('[data-workspace-act="' + name + '"]');
  return {
    cards: Array.from(document.querySelectorAll('li[data-practice-card]')).map((card) => ({
      title: card.querySelector('h3').textContent.trim(),
      concepts: Array.from(card.querySelectorAll('[data-practices-part="concepts"] li'))
        .map((li) => li.textContent.trim())
    })),
    listTitle: document.querySelector('#practices-title').textContent.trim(),
    shown: Array.from(document.querySelectorAll('main > section[data-kind="practice"]'))
      .filter((el) => el.checkVisibility()).map((el) => el.id),
    shell: box(shell),
    bar: box(shell.querySelector('[data-workspace-part="bar"]')),
    title: shell.querySelector('[data-workspace-part="title"]').textContent.trim(),
    statement: statement ? statement.id : null,
    statementBox: box(statement),
    panel: panel
      ? (panel.getAttribute('data-practice') || panel.getAttribute('data-practice-quiz'))
      : null,
    panelBox: box(panel),
    previous: !!act('previous').checkVisibility(),
    next: !!act('next').checkVisibility(),
    frames: document.querySelectorAll('iframe').length,
    y: window.scrollY,
    viewport: {w: window.innerWidth, h: window.innerHeight}
  };
})()
"""

#: The fixture's two code practices and its quiz, each with what it practises.
PRACTICES = (
    ("practice-java", "Practice: Greeter", ["A greeting is built from a name."]),
    ("practice-shout", "Practice: Shouter", ["Upper case is one call."]),
    ("practice-quiz", "Practice: Check yourself", ["What a class declaration opens."]),
)


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """A real built tree, with one extra page carrying three practices."""
    root = tmp_path_factory.mktemp("workspace-site")
    built = site.build(root)
    case = UNIT_CASE_OF[CORPUS]()
    document = copy.deepcopy(case.document)
    practice = next(part for part in document["sections"] if part.get("kind") == "practice")
    others = [part for part in document["sections"] if part.get("kind") != "practice"]
    made = []
    for key, heading, concepts in PRACTICES:
        one = copy.deepcopy(practice)
        record = QUIZ if key == "practice-quiz" else one["workspace"]
        one.update(key=key, heading=heading, workspace={**record, "concepts": concepts})
        made.append(one)
    document["sections"] = [*others, *made]
    where = Path(root / CORPUS / str(case.placement.unit.page))
    (where.parent / PAGE).write_bytes(render(document, case.placement))
    return built


@pytest.fixture
def origin(tree: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the tree, whose editor route answers two windows."""
    with served.serving(tree, CORPUS, windows=True) as running:
        yield running


def _url(origin: served.Served) -> str:
    case = UNIT_CASE_OF[CORPUS]()
    return f"{origin.origin}/{Path(str(case.placement.unit.page)).parent / PAGE}"


def _state(page: OpenPage) -> dict:
    return dict(page.evaluate(STATE))  # type: ignore[call-overload]


def _until(page: OpenPage, ready, what: str) -> dict:
    deadline = time.monotonic() + SETTLE
    reading = _state(page)
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = _state(page)
    raise AssertionError(f"the workspace never {what}; it reads {reading}")


def _open_card(page: OpenPage, key: str) -> None:
    """Tab from the top to the card for `key`, and press Enter on it."""
    page.focus_body()
    for _press in range(PRESSES):
        page.tab()
        if page.focused()["label"] == f"#s-{key}":
            page.press("Enter")
            return
    raise AssertionError(f"{PRESSES} Tab presses never reached the card for {key}")


def _act(page: OpenPage, name: str) -> None:
    """Press one of the workspace's own buttons with the keyboard."""
    page.evaluate(f"document.querySelector('[data-workspace-act=\"{name}\"]').focus()")
    page.press("Enter")


def _laid_out(reading: dict, shape: str, *, quiz: bool = False) -> None:
    """The statement and the panel, side by side at a desktop and stacked on a phone.

    ⭐ A quiz is one column at every width: its intro above its questions, the
    same width, so no pane is left holding one line.
    """
    statement, panel, bar = reading["statementBox"], reading["panelBox"], reading["bar"]
    width, height = reading["viewport"]["w"], reading["viewport"]["h"]
    assert statement and panel and bar, f"the workspace shows no statement or no panel: {reading}"
    if quiz:
        # ⭐ A quiz is a page that scrolls as one, so it starts under the bar and may run past
        # the window's foot.
        assert statement["top"] >= bar["bottom"] - 1, f"the statement is under the bar: {reading}"
    else:
        assert abs(statement["top"] - bar["bottom"]) <= 1, (
            f"the statement is not under the bar: {reading}"
        )
        assert panel["bottom"] <= height + 1 and statement["bottom"] <= height + 1
    if quiz:
        assert statement["bottom"] <= panel["top"] + 1, f"not one column: {reading}"
        assert abs(statement["left"] - panel["left"]) <= 1, f"not one column: {reading}"
        assert abs(statement["width"] - panel["width"]) <= 1, f"not one column: {reading}"
    elif shape == "desktop":
        assert statement["right"] <= panel["left"] + 1, f"not side by side: {reading}"
        assert abs(panel["top"] - bar["bottom"]) <= 1 and panel["right"] >= width - 1
    else:
        assert statement["bottom"] <= panel["top"] + 1, f"not stacked: {reading}"
        assert statement["width"] >= width - 1 and panel["width"] >= width - 1


@pytest.mark.parametrize("shape", WIDTHS)
def test_the_list_titles_every_practice_and_no_editor_loads_until_one_is_opened(
    open_page: OpenPage, origin: served.Served, shape: str
) -> None:
    open_page.resize(*WIDTHS[shape])
    open_page.open(_url(origin))
    reading = _state(open_page)
    assert reading["listTitle"] == "Practice (3)"
    assert [card["title"] for card in reading["cards"]] == [title for _k, title, _c in PRACTICES]
    assert [card["concepts"] for card in reading["cards"]] == [c for _k, _t, c in PRACTICES]
    assert reading["shown"] == [], f"a practice shows under the list: {reading['shown']}"
    assert reading["shell"] is None, "the workspace is up before any card was opened"
    assert reading["frames"] == 0, "an editor loaded before a practice was opened"
    # ⛔ And none was ASKED for: the frame is built from an answer, so a count
    # read before the answer came would see none either way.
    asked = [one for one in origin.runs.asked if "/editor/" in one]
    assert asked == [], f"the page asked for an editor before a practice was opened: {asked}"


@pytest.mark.parametrize("shape", WIDTHS)
def test_a_card_opens_its_statement_beside_one_editor(
    open_page: OpenPage, origin: served.Served, shape: str
) -> None:
    open_page.resize(*WIDTHS[shape])
    open_page.open(_url(origin))
    _open_card(open_page, "practice-java")
    reading = _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    assert reading["shell"] and reading["title"] == "Practice: Greeter"
    assert reading["statement"] == "s-practice-java"
    assert reading["panel"].endswith("/practice-java")
    assert not reading["previous"] and reading["next"], (
        "the ends are not where Previous and Next say"
    )
    _laid_out(reading, shape)
    # ⛔ Clicking the Tests tab points the ONE frame at the test's window.
    open_page.evaluate("document.querySelector('[data-practice-tab=\"test\"]').click()")
    assert _state(open_page)["frames"] == 1, "the Tests tab built a second editor"


@pytest.mark.parametrize("shape", WIDTHS)
def test_next_opens_the_next_practice_and_the_quiz_is_one_of_them(
    open_page: OpenPage, origin: served.Served, shape: str
) -> None:
    open_page.resize(*WIDTHS[shape])
    open_page.open(_url(origin))
    _open_card(open_page, "practice-java")
    _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    _act(open_page, "next")
    second = _until(open_page, lambda r: r["statement"] == "s-practice-shout", "opened card 2")
    assert second["frames"] <= 1, "two editors at once"
    assert second["previous"] and second["next"]
    second = _until(open_page, lambda r: r["frames"] == 1, "built card 2's editor")
    _laid_out(second, shape)
    _act(open_page, "next")
    quiz = _until(open_page, lambda r: r["statement"] == "s-practice-quiz", "opened the quiz")
    assert quiz["frames"] == 0, "the quiz kept an editor frame it has no use for"
    assert quiz["previous"] and not quiz["next"]
    _laid_out(quiz, shape, quiz=True)


@pytest.mark.parametrize("shape", WIDTHS)
def test_close_returns_the_reader_to_the_card_with_no_editor_left(
    open_page: OpenPage, origin: served.Served, shape: str
) -> None:
    open_page.resize(*WIDTHS[shape])
    open_page.open(_url(origin))
    open_page.evaluate(
        "window.scrollTo({top: document.querySelector('#practices').offsetTop - 20,"
        " behavior: 'instant'})"
    )
    before = _state(open_page)["y"]
    assert before > 0, "the page is at its top, so a return to the top would pass unseen"
    # ⭐ The card is reached by Tab from where the reader is, which moves nothing
    # once it is in view.
    open_page.evaluate("document.querySelector('#card-practice-java a').focus()")
    open_page.tab()
    assert open_page.focused()["label"] == "#s-practice-shout"
    open_page.press("Enter")
    _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    _act(open_page, "close")
    after = _until(open_page, lambda r: r["shell"] is None, "closed")
    assert after["frames"] == 0 and after["shown"] == []
    assert after["y"] == before, f"Close left the page at {after['y']}, not {before}"
    assert open_page.focused()["label"] == "#s-practice-shout", "focus did not return to the card"


# --- narration's stand-in for a passage the page is not showing -----

#: Where `window.studyforge.standIn` puts a passage, by what it is: its own id,
#: its tag, and the card it names. ⭐ The real part, asked in the real page.
STAND_IN = """
((selector) => {
  const passage = document.querySelector(selector);
  const at = window.studyforge.standIn(passage);
  return at ? {tag: at.tagName, card: at.getAttribute('data-practice-card')} : null;
})
"""


def _stand_in(page: OpenPage, selector: str) -> dict | None:
    return page.evaluate(f"({STAND_IN})({selector!r})")  # type: ignore[return-value]


def test_a_passage_in_a_practice_under_the_list_stands_in_as_its_card(
    open_page: OpenPage, tree: site.Site
) -> None:
    open_page.open(tree.url("depth2-unit-01").rsplit("/", 1)[0] + "/" + PAGE)
    statement = "#s-practice-shout p"
    assert _stand_in(open_page, statement) == {"tag": "LI", "card": "s-practice-shout"}
    # ⭐ Opened, the practice is its own place.
    open_page.open_practice(1)
    assert _stand_in(open_page, statement) is None


def test_a_passage_in_a_closed_entry_stands_in_as_its_summary_and_nothing_opens(
    open_page: OpenPage, tree: site.Site
) -> None:
    open_page.open(tree.url("depth2-unit-01").rsplit("/", 1)[0] + "/" + PAGE)
    open_page.open_practice(0)
    # ⭐ The practice's own hint: a closed disclosure with a passage inside it.
    open_page.evaluate(
        "document.querySelector('#s-practice-java details p').setAttribute('id', 'inside')"
    )
    assert _stand_in(open_page, "#inside") == {"tag": "SUMMARY", "card": None}
    assert open_page.evaluate("document.querySelector('#s-practice-java details').open") is False


def test_opening_a_practice_closes_an_expanded_code_example(
    open_page: OpenPage, tree: site.Site
) -> None:
    # ⛔ One editor on the page at most: an expanded example is closed by an
    # attribute, and `code-links.js` drops its frames on the toggle.
    open_page.open(tree.url("depth2-unit-01").rsplit("/", 1)[0] + "/" + PAGE)
    open_page.evaluate(
        "(() => { const d = document.createElement('details');"
        " d.setAttribute('data-code-example', ''); d.open = true;"
        " document.querySelector('main').prepend(d); })()"
    )
    open_page.open_practice(0)
    assert open_page.evaluate("document.querySelector('details[data-code-example]').open") is False


def test_with_no_editor_a_practice_says_why_and_asks_nothing_that_fails(
    open_page: OpenPage, tree: site.Site
) -> None:
    # ⭐ The page learns what works from the server's API.
    # ⛔ With no editor named in the index, opening a practice asks for no
    # editor window — a `404` for one would be an error in the reader's console
    # — and the panel shows the sentence it ships.
    with served.serving(tree, CORPUS) as running:
        open_page.browser.call("Log.enable", session=open_page.session)
        open_page.open(_url(running))
        _open_card(open_page, "practice-java")
        time.sleep(1.0)
        says = open_page.evaluate(
            "(() => { const p = document.querySelector("
            "'section[data-practice][data-workspace-open] [data-practice-part=\"no-editor\"]');"
            " return !!p && p.checkVisibility(); })()"
        )
        frames = _state(open_page)["frames"]
        asked = [one for one in running.runs.asked if "/editor/" in one]
        failed = [
            str(event["params"]["entry"].get("text", ""))
            + " "
            + str(event["params"]["entry"].get("url", ""))
            for event in open_page.browser.events
            if event.get("method") == "Log.entryAdded"
            and event["params"]["entry"].get("level") in ("error", "warning")
            # ⚠️ This harness registers no `state` namespace, so the card's
            # record answers `404` here; a real instance answers it.
            and "/api/v1/state/" not in str(event["params"]["entry"].get("url", ""))
        ]
    assert running.runs.asked, "⛔ born vacuous: the page asked the run namespace nothing"
    assert says is True, "the panel does not say why there is no editor"
    assert frames == 0
    assert asked == [], f"the page asked an editor the index does not name: {asked}"
    assert failed == [], f"the console is not clean: {failed}"


def test_a_link_beside_the_tabs_opens_the_shown_window_in_a_tab_of_its_own(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    open_page.resize(*WIDTHS["desktop"])
    open_page.open(_url(origin))
    _open_card(open_page, "practice-java")
    _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    link = (
        "(() => { const a = document.querySelector('a[data-practice-popout]');"
        " return a && {href: a.getAttribute('href'), target: a.target, rel: a.rel,"
        " frame: document.querySelector('iframe').getAttribute('src'),"
        " shown: a.checkVisibility()}; })()"
    )
    first = dict(open_page.evaluate(link))  # type: ignore[call-overload]
    assert first["shown"] and first["target"] == "_blank" and "noopener" in first["rel"]
    assert first["href"] == first["frame"], "the link does not open the window the frame shows"
    open_page.capture(capture_dir / "editor-popout-link.png", whole=False)
    open_page.evaluate("document.querySelector('[data-practice-tab=\"test\"]').click()")
    second = dict(open_page.evaluate(link))  # type: ignore[call-overload]
    assert second["href"] == second["frame"] and second["href"] != first["href"]


def test_a_practice_of_several_files_has_a_tab_for_each_and_each_tab_its_own_window(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    origin.runs.windows["files"] = [
        {"path": "practice/config/settings.json", "url": "about:blank#settings"},
        {"path": "practice/config/NOTES.md", "url": "about:blank#notes"},
    ]
    open_page.resize(*WIDTHS["desktop"])
    open_page.open(_url(origin))
    _open_card(open_page, "practice-java")
    _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    tabs = (
        "Array.from(document.querySelectorAll('[data-practice-tab]'))"
        ".filter((t) => t.checkVisibility()).map((t) => t.textContent.trim())"
    )
    assert open_page.evaluate(tabs) == ["Your code", "settings.json", "NOTES.md", "Tests"]
    open_page.capture(capture_dir / "multi-file-tabs.png", whole=False)
    open_page.evaluate("document.querySelectorAll('[data-practice-tab]')[2].click()")
    where = (
        "[document.querySelector('iframe').getAttribute('src'),"
        " document.querySelector('a[data-practice-popout]').getAttribute('href')]"
    )
    assert open_page.evaluate(where) == ["about:blank#notes", "about:blank#notes"]
    assert _state(open_page)["frames"] == 1, "a file tab built a second editor"


FILES = [
    {"path": "practice/config/settings.json", "url": "about:blank#settings"},
    {"path": "practice/config/NOTES.md", "url": "about:blank#notes"},
]


@pytest.mark.parametrize("width", ["desktop", "phone"])
@pytest.mark.parametrize(
    "windows",
    [
        {"main": {"url": "about:blank#a"}, "files": FILES},
        {"main": {"url": "about:blank#a"}, "test": {"url": "about:blank#t"}, "files": FILES},
        {"main": {"url": "about:blank#a"}},
    ],
    ids=["files-no-test", "files-and-test", "one-file"],
)
def test_the_editor_link_shows_whenever_the_workspace_shows_the_editor(
    open_page: OpenPage, origin: served.Served, windows: dict, width: str
) -> None:
    # ⭐ A configuration practice has several files and may have no test window, so the tablist
    # may be hidden; the link to the editor in its own tab is shown all the same, in view.
    origin.runs.windows = windows
    open_page.resize(*WIDTHS[width])
    open_page.open(_url(origin))
    _open_card(open_page, "practice-java")
    _until(open_page, lambda r: r["frames"] == 1, "built its one editor frame")
    seen = open_page.evaluate(
        "(() => { const a = document.querySelector('a[data-practice-popout]');"
        " if (!a) return null; const b = a.getBoundingClientRect();"
        " const f = document.querySelector('iframe').getBoundingClientRect();"
        " return {shown: a.checkVisibility(), inside: b.width > 0 && b.height > 0 &&"
        " b.bottom <= innerHeight && b.right <= innerWidth && b.top >= 0,"
        " above: b.bottom <= f.top + 1}; })()"
    )
    assert seen == {"shown": True, "inside": True, "above": True}
