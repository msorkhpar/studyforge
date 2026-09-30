"""A narrated page asks its first clip once, and shows narration only when it loads.

⭐ **What works is found out in the UI.** A page
learns whether its clips are here by loading its FIRST clip's metadata, once
(`narration-probe.js`). When it loads, the transport shows and plays. When it
fails, the page asks for no other clip and shows no narration control, and the
one failed request is the only line in the console.

⭐ **Five trees, each built by the real build from a fixture corpus with planted
clips, and each opened over `file://` AND served by the real `studyforge serve`:**

| tree | how it got there | the page must |
|---|---|---|
| `absent` | built with no clip on disk | ask one clip, hide every control |
| `removed` | built WITH clips, then one unit's clips taken away | the same, on that unit |
| `restored` | built with no clip, then the clips put back, no rebuild | play |
| `present` | built with clips on disk | play |
| `stale` | built with clips, beside a retired clip signal that says `released` | play |

⭐ **The console is read at every level** through the protocol's `Log` domain (where
a failed load lands), `Runtime.consoleAPICalled` and `Runtime.exceptionThrown`:
where the clips are here none may be an error or a warning, and where they are
not the ONE error is the probe's, naming the first clip. ⛔ The trees without
clips are also DRIVEN: a press of Space and a click on a narrated passage must
ask for nothing more.
"""

from __future__ import annotations

import contextlib
import re
import shutil
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.generate import write_site
from tests.studyforge.generate.corpora import a_corpus
from tests.studyforge.generate.test_narration import narrate
from tests.visual.page import OpenPage
from tests.visual.site import FRAME, FRAMES
from tests.visual.test_served_faces import serving

#: The fixture read. ⭐ `depth2`, the `sibling` profile, whose pages sit below the
#: corpus root and whose clips sit in `audio/<stem>/` beside them.
FIXTURE = "depth2"

#: Every tree, by what it stands for (the table in this module's docstring).
TREES = ("absent", "removed", "restored", "present", "stale")

#: The trees whose read page has no clip on disk.
WITHOUT = ("absent", "removed")

#: The trees whose read page has its clips.
WITH = ("restored", "present", "stale")

#: The retired clip signal, and what the release pack once wrote into it.
RETIRED = ".studyforge/assets/narration-clips.js"
RELEASED_BODY = (
    'window.studyforge = window.studyforge || {}; window.studyforge.clips = "released";\n'
)

#: How the page is reached.
SCHEMES = ("file", "served")

#: Levels a console entry may not have.
LOUD = frozenset({"error", "warning"})

#: Seconds a driven page is given to issue whatever it would issue.
SETTLE = 1.0

#: A narrated passage's attribute, as the page carries it.
HREF = re.compile(r'data-audio="([^"]+)"')


def _built(where: Path, tree: str) -> Path:
    """One narrated corpus, built into its own root and left in state `tree`."""
    root = a_corpus(where, FIXTURE)
    clips = narrate(root)
    for clip in clips:
        clip.write_bytes(FRAME * FRAMES)
    kept = where / "kept"
    if tree in ("absent", "restored"):
        kept.mkdir()
        for clip in clips:
            shutil.move(clip, kept / clip.name)
    write_site(root, root)
    if tree == "removed":
        # ⭐ The read page's own clips go, after the build and with no build after
        # it: every other unit keeps its clips.
        page = root / narrated_page(root)
        for href in HREF.findall(page.read_text(encoding="utf-8")):
            (page.parent / href).unlink(missing_ok=True)
    if tree == "restored":
        # ⭐ What the restore does, after the site exists and with no build after it.
        for clip in clips:
            shutil.move(kept / clip.name, clip)
    if tree == "stale":
        # ⛔ What hid the Java site's narration on its author's disk: a signal the
        # release pack wrote, with every clip still there. Nothing reads it now.
        (root / RETIRED).write_text(RELEASED_BODY, encoding="utf-8")
    return root


@pytest.fixture(scope="module")
def trees(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Every tree, built once for the module."""
    return {tree: _built(tmp_path_factory.mktemp(tree), tree) for tree in TREES}


def narrated_page(root: Path) -> str:
    """The first unit page under `root` that carries a narrated passage, as a relative path."""
    for page in sorted(root.rglob("*.unit.html")):
        if HREF.search(page.read_text(encoding="utf-8")):
            return page.relative_to(root).as_posix()
    raise AssertionError("no unit page carries a narrated passage, so nothing here is read")


@contextlib.contextmanager
def reached(root: Path, scheme: str) -> Iterator[str]:
    """Yield the URL of `root`'s narrated page over `scheme`, serving it while needed."""
    page = narrated_page(root)
    if scheme == "file":
        yield (root / page).as_uri()
        return
    with serving(root, root) as origin:
        yield f"{origin}/{page}"


def loud(page: OpenPage) -> list[tuple[str, str]]:
    """Every console entry this tab logged at error or warning level, as `(level, text)`.

    ⭐ Three sources, because they are three different places a page complains:
    `Log.entryAdded` is where a failed resource load lands, `consoleAPICalled` a
    script's own `console.*`, and `exceptionThrown` an uncaught throw.
    """
    time.sleep(SETTLE)
    page.evaluate("1")  # ⭐ drains what the browser has sent since the last call
    found: list[tuple[str, str]] = []
    for event in page.browser.events:
        if event.get("sessionId") not in (None, page.session):
            continue
        method, params = event.get("method"), event.get("params", {})
        if method == "Log.entryAdded":
            entry = params["entry"]
            if entry.get("level") in LOUD:
                where = str(entry.get("url", "")).rsplit("/", 1)[-1]
                found.append((entry["level"], f"{str(entry.get('text', ''))[:120]} {where}"))
        elif method == "Runtime.consoleAPICalled":
            level = "warning" if params.get("type") == "warn" else params.get("type")
            if level in LOUD:
                found.append((str(level), "console." + str(params.get("type"))))
        elif method == "Runtime.exceptionThrown":
            found.append(("error", "uncaught exception"))
    return found


def opened(page: OpenPage, url: str) -> None:
    """Open `url` with the `Log` domain on, so a failed load is read."""
    page.browser.call("Log.enable", session=page.session)
    page.open(url)


def shown(page: OpenPage) -> dict:
    """Whether the transport shows, and what the narrator has been given to play."""
    return dict(
        page.evaluate(
            "({player: !document.getElementById('player').hidden,"
            " src: document.getElementById('narrator').getAttribute('src') || ''})"
        )  # type: ignore[arg-type]
    )


def drive(page: OpenPage) -> None:
    """Press Space on the page, then click its first narrated passage, as a reader would."""
    page.focus_body()
    page.press(" ")
    box = page.evaluate(
        "(() => { const r = document.querySelector('[data-audio]').getBoundingClientRect();"
        " return {x: r.left + 4, y: r.top + 4}; })()"
    )
    for kind in ("mousePressed", "mouseReleased"):
        page.browser.call(
            "Input.dispatchMouseEvent",
            {"type": kind, "x": box["x"], "y": box["y"], "button": "left", "clickCount": 1},
            session=page.session,
        )


def clip_requests(page: OpenPage) -> list[str]:
    """Every clip this tab asked for."""
    return [url for url in page.requests() if url.endswith(".mp3")]


def first_clip(root: Path) -> str:
    """The file name of the first clip the read page names: the one its probe asks."""
    page = root / narrated_page(root)
    found = HREF.search(page.read_text(encoding="utf-8"))
    assert found, "⛔ born vacuous: the read page names no clip"
    return found.group(1).rsplit("/", 1)[-1]


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("tree", WITHOUT)
def test_with_its_clips_absent_a_page_asks_one_clip_and_shows_no_control(
    open_page: OpenPage, trees: dict[str, Path], tree: str, scheme: str
) -> None:
    root = trees[tree]
    page = root / narrated_page(root)
    hrefs = HREF.findall(page.read_text(encoding="utf-8"))
    assert hrefs and not any((page.parent / href).is_file() for href in hrefs), (
        "⛔ born vacuous: the read page must hold none of its clips"
    )
    first = first_clip(root)
    with reached(root, scheme) as url:
        opened(open_page, url)
        assert shown(open_page) == {"player": False, "src": ""}
        drive(open_page)
        after = shown(open_page)
        console = loud(open_page)
        asked = clip_requests(open_page)
    assert after == {"player": False, "src": ""}, "a press or a click reached the narrator"
    assert [one.rsplit("/", 1)[-1] for one in asked] == [first], (
        f"the page asked {len(asked)} clip(s), and it must ask its first one only: {asked}"
    )
    others = [entry for entry in console if not entry[1].endswith(first)]
    assert others == [], f"the console holds more than the probe: {others}"
    assert len(console) <= 1, f"the probe was logged more than once: {console}"


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("tree", WITH)
def test_with_its_clips_present_a_page_plays_and_its_console_is_clean(
    open_page: OpenPage, trees: dict[str, Path], tree: str, scheme: str
) -> None:
    root = trees[tree]
    assert list(root.rglob("*.mp3")), "⛔ born vacuous: this tree must hold its clips"
    with reached(root, scheme) as url:
        opened(open_page, url)
        deadline = time.monotonic() + SETTLE * 5
        while not shown(open_page)["player"] and time.monotonic() < deadline:
            time.sleep(0.05)
        assert shown(open_page)["player"] is True, "the transport is hidden with its clips there"
        open_page.focus_body()
        open_page.press(" ")
        playing = shown(open_page)
        console = loud(open_page)
        asked = clip_requests(open_page)
    assert playing["src"].endswith(".mp3"), "Space did not load the first clip"
    assert asked, "the first clip was never requested"
    assert console == [], f"the console is not clean: {console}"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_the_console_reading_sees_the_probe_that_fails(
    open_page: OpenPage, trees: dict[str, Path], scheme: str
) -> None:
    # ⛔ The negative control of the clean readings above: the absent page's one
    # probe IS read, as one error naming its first clip. If this read clean, a
    # clean console would prove nothing.
    root = trees["absent"]
    with reached(root, scheme) as url:
        opened(open_page, url)
        console = loud(open_page)
    assert [level for level, _ in console] == ["error"], console
    assert console[0][1].endswith(first_clip(root)), console
