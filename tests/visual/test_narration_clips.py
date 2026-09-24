"""A narrated page with its clips absent shows no narration control and logs nothing.

⛔ **The reading the row asks for, in the pinned browser.** A site whose clips are a
download nobody has taken is the normal case, so a page must hide its narration
controls when they are absent, and must learn that without requesting a clip: a
request for a file that is not there is an ERROR in the console, over `file://`
(`net::ERR_FILE_NOT_FOUND`) and served (`404`) alike — measured before this was
written, for a `<script>`, a preloading `<audio>` and a `fetch`.

⭐ **Four trees, each built by the real build from a fixture corpus with planted
clips, and each opened over `file://` AND served by the real `studyforge serve`:**

| tree | how it got there | the page must |
|---|---|---|
| `absent` | built with no clip on disk | hide every control, log nothing |
| `released` | built WITH clips, packed (`RELEASED`), clips then taken away | the same |
| `restored` | built with no clip, then restored (clips + `PRESENT`), no rebuild | play |
| `present` | built with clips on disk | play |

⭐ **The console is read at every level** through the protocol's `Log` domain (where
a failed load lands), `Runtime.consoleAPICalled` and `Runtime.exceptionThrown`, and
none may be an error or a warning. ⛔ `absent` and `released` are also DRIVEN: a
press of Space and a click on a narrated passage must load nothing.

⛔ **The console reading is shown to be able to fail** (`test_the_console_reading_
sees_a_probe_that_fails`): the same absent page, made to request one of its own
clips, reads RED.
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
from studyforge.render.pageassets import CLIPS_NAME, PRESENT, RELEASED, clips_script
from tests.studyforge.generate.corpora import a_corpus
from tests.studyforge.generate.test_narration import narrate
from tests.visual.page import OpenPage
from tests.visual.test_served_faces import serving

#: The fixture read. ⭐ `depth2`, the `sibling` profile, whose pages sit below the
#: corpus root and whose clips sit in `audio/<stem>/` beside them.
FIXTURE = "depth2"

#: Every tree, by what it stands for (the table in this module's docstring).
TREES = ("absent", "released", "restored", "present")

#: The trees whose clips are not on disk.
WITHOUT = ("absent", "released")

#: How the page is reached.
SCHEMES = ("file", "served")

#: One silent MPEG-1 Layer III frame (128 kbit/s, 44.1 kHz): a header and zeroed
#: side information, which decodes to silence. ⭐ A real clip rather than the
#: build tests' marker bytes, because a clip that will not decode is its own
#: message in the console and would be read here as the page's fault.
FRAME = bytes.fromhex("fffb9064") + bytes(417 - 4)

#: Frames per planted clip: about half a second.
FRAMES = 20

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
    signal = root / ".studyforge" / "assets" / CLIPS_NAME
    if tree == "released":
        signal.write_bytes(clips_script(RELEASED))
        for clip in clips:
            clip.unlink()
    if tree == "restored":
        # ⭐ What the restore does, after the site exists and with no build after it.
        for clip in clips:
            shutil.move(kept / clip.name, clip)
        signal.write_bytes(clips_script(PRESENT))
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
                found.append((entry["level"], str(entry.get("text", ""))[:160]))
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


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("tree", WITHOUT)
def test_with_its_clips_absent_a_page_shows_no_control_and_its_console_is_clean(
    open_page: OpenPage, trees: dict[str, Path], tree: str, scheme: str
) -> None:
    root = trees[tree]
    assert not list(root.rglob("*.mp3")), "⛔ born vacuous: this tree must hold no clip"
    with reached(root, scheme) as url:
        opened(open_page, url)
        assert open_page.evaluate("document.querySelectorAll('[data-audio]').length") > 0
        assert shown(open_page) == {"player": False, "src": ""}
        drive(open_page)
        after = shown(open_page)
        console = loud(open_page)
        asked = clip_requests(open_page)
    assert console == [], f"the console is not clean: {console}"
    assert after == {"player": False, "src": ""}, "a press or a click reached the narrator"
    assert asked == [], f"the page requested {len(asked)} clip(s) that are not there"


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("tree", ("restored", "present"))
def test_with_its_clips_present_a_page_plays_and_its_console_is_clean(
    open_page: OpenPage, trees: dict[str, Path], tree: str, scheme: str
) -> None:
    root = trees[tree]
    assert list(root.rglob("*.mp3")), "⛔ born vacuous: this tree must hold its clips"
    with reached(root, scheme) as url:
        opened(open_page, url)
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
def test_the_console_reading_sees_a_probe_that_fails(
    open_page: OpenPage, trees: dict[str, Path], scheme: str
) -> None:
    # ⛔ The negative control: the absent page, made to ask for one of its own
    # clips the way a probe would. If this reads clean, the readings above prove
    # nothing.
    with reached(trees["absent"], scheme) as url:
        opened(open_page, url)
        open_page.evaluate(
            "(() => { const a = new Audio();"
            " a.preload = 'auto';"
            " a.src = document.querySelector('[data-audio]').getAttribute('data-audio'); })()"
        )
        console = loud(open_page)
    assert any(level == "error" for level, _ in console), "a failed load was not read"
