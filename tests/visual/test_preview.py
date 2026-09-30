"""The read-only preview, opened in a real browser from a static server, never the study server.

⭐ **A course's `main` explains itself and a static, read-only
preview of its lessons can be published.** So the preview a real build produces is served by
Python's own `http.server` (no study server, no run client, no API) and every page is opened:
the console holds nothing, no request fails, none asks an `/api/` path or a clip, the banner and
the notes are there, a quiz grades inside the page, a reading mark survives a reload, and no
Run or Submit exists to press.

⛔ **The negative control is the same page unstripped**, served the same way: its narration
probes a clip the static server does not have, and the console says so. ⭐ The links that need
the repository are built at run time from `location`, so `studyforge_preview.repository` is asked
with each shape of address and must build the project page's link only from a project page's.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import shutil
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import preview, tour
from tests.studyforge.serve.routes.quizzing import page_of, quiz_corpus
from tests.studyforge.skills.execution.standalone.test_preview import (
    PLAYER,
    PRACTICE,
    example,
)
from tests.visual.page import OpenPage

#: Seconds a reading waits for the page's own script to settle.
SETTLE = 1.0

#: What the page logs at these levels is a failure, and the first status that is one.
LOUD = frozenset({"error", "warning"})
HTTP_ERROR = 400

#: The markup a built page carries and the fixture lacks, added before the quiz section.
SERVER_ONLY = PRACTICE + example("archive/x/Source.java")

#: The five shapes of address the runtime link is judged over: `(host, path, link or None)`.
ADDRESSES = (
    ("a.github.io", "/r/x.html", "https://github.com/a/r"),
    ("A.GitHub.io", "/Repo/x", "https://github.com/a/Repo"),
    ("a.github.io", "/", None),
    ("a.github.io", "/index.html", None),
    ("example.org", "/r/", None),
    ("a.b.github.io", "/r/", None),
)


class Quiet(http.server.SimpleHTTPRequestHandler):
    """A plain static file server that keeps the paths it was asked for."""

    asked: list[str] = []

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        type(self).asked.append(str(args[0]))


@contextlib.contextmanager
def static(root: Path) -> Iterator[tuple[str, list[str]]]:
    """Serve `root` with `http.server` on a free loopback port; yield its origin and its log."""
    handler = type("Handler", (Quiet,), {"asked": []})
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(handler, directory=str(root))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", handler.asked
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


@pytest.fixture(scope="module")
def trees(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, str]:
    """A built course with the server-only parts added, and the preview made from it."""
    where = tmp_path_factory.mktemp("preview")
    tree = quiz_corpus(where)
    unit = page_of(tree)
    text = unit.read_text(encoding="utf-8")
    marker = "<section data-practice-quiz"
    assert marker in text, "born vacuous: the built page has no quiz"
    text = text.replace(marker, SERVER_ONLY.replace("{up}", "") + marker, 1)
    text = text.replace("<script src=", PLAYER + "<script src=", 1)
    text = text.replace("<h1", '<h1 data-audio="audio/x.mp3"', 1)
    unit.write_text(text, encoding="utf-8")
    (tree / "archive/x").mkdir(parents=True)
    (tree / "archive/x/Source.java").write_text("class Source {}", encoding="utf-8")
    out = where / "site"
    preview.preview(tree, out)
    return tree, out, unit.relative_to(tree).as_posix()


def watching(page: OpenPage) -> OpenPage:
    """Ask the browser for the `Log` domain too: where a failed resource load is reported."""
    page.browser.call("Log.enable", session=page.session)
    return page


def entries(page: OpenPage) -> list[tuple[str, str]]:
    """Every console entry at error or warning level, from the places a page complains."""
    time.sleep(SETTLE)
    page.evaluate("1")
    found: list[tuple[str, str]] = []
    for event in page.browser.events:
        if event.get("sessionId") not in (None, page.session):
            continue
        method, params = event.get("method"), event.get("params", {})
        if method == "Log.entryAdded" and params["entry"].get("level") in LOUD:
            found.append((params["entry"]["level"], str(params["entry"].get("text", ""))[:100]))
        elif method == "Runtime.consoleAPICalled" and params.get("type") in ("error", "warn"):
            found.append(("console", str(params.get("type"))))
        elif method == "Runtime.exceptionThrown":
            found.append(("exception", "thrown"))
        elif method == "Network.loadingFailed":
            found.append(("failed", str(params.get("errorText"))))
        elif method == "Network.responseReceived" and params["response"]["status"] >= HTTP_ERROR:
            found.append(("status", str(params["response"]["status"])))
    return found


def pages_of(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*.html"))


def test_every_page_opens_with_a_silent_console_and_asks_no_api_no_clip_and_no_missing_file(
    open_page: OpenPage, trees
) -> None:
    _tree, out, _unit = trees
    pages = pages_of(out)
    assert len(pages) >= 3, "born vacuous: the preview holds too few pages to be a crawl"
    watching(open_page)
    with static(out) as (origin, asked):
        for name in pages:
            open_page.open(f"{origin}/{name}")
            assert entries(open_page) == [], name
            urls = open_page.requests()
            assert not [u for u in urls if "/api/" in u or u.endswith(".mp3")], (name, urls)
    assert [line for line in asked if " 404 " in line or 'HTTP/1.1" 404' in line] == []
    assert not any("/api/" in line for line in asked)
    assert not any("/." in line.split(" ")[1] for line in asked)


def test_the_banner_and_the_notes_are_visible_and_nothing_can_run(
    open_page: OpenPage, trees
) -> None:
    _tree, out, unit = trees
    with static(out) as (origin, _asked):
        open_page.open(f"{origin}/course/{unit.split('.studyforge/')[-1]}")
        state = open_page.evaluate(
            """(() => {
              const shown = (el) => !!el && el.checkVisibility();
              const banner = document.querySelector('[data-preview-banner]');
              const example = document.querySelector('details[data-code-example]');
              example.open = true;
              const open = document.querySelector('a[data-practices-part=open]');
              return {
                banner: shown(banner), bannerText: banner.textContent,
                example: shown(example.querySelector('[data-preview-note=example]')),
                practice: document.querySelectorAll(
                  'section[data-practice] [data-preview-note=practice]').length,
                narration: document.querySelectorAll('[data-preview-note=narration]').length,
                acts: document.querySelectorAll('[data-practice-act],[data-code-act]').length,
                frames: document.querySelectorAll('iframe').length,
                audio: document.querySelectorAll('[data-audio]').length,
                player: document.querySelectorAll('#player,#narrator').length,
                links: document.querySelectorAll('a[data-preview-run], a[data-code-path]').length,
              };
            })()"""
        )
    assert state["banner"] and "Read-only preview" in state["bannerText"]
    assert state["example"] and state["practice"] == 1 and state["narration"] == 1
    assert (state["acts"], state["frames"], state["audio"], state["player"]) == (0, 0, 0, 0)
    assert state["links"] == 0, "off github.io no link may be built"


def test_a_quiz_grades_inside_the_preview_and_its_pass_survives_a_reload(
    open_page: OpenPage, trees
) -> None:
    _tree, out, unit = trees
    with static(out) as (origin, asked):
        url = f"{origin}/course/{unit.split('.studyforge/')[-1]}"
        open_page.open(url)
        before = len(asked)
        graded = open_page.evaluate(
            """(() => {
              const quiz = document.querySelector('section[data-practice-quiz]');
              const key = quiz.querySelector('script[data-practice-part=key]');
              const keys = JSON.parse(key.textContent);
              const questions = [...quiz.querySelectorAll('[data-practice-question]')];
              const say = () => quiz.querySelector('p[data-practice-part=status]').textContent;
              const choose = (right) => questions.forEach((li) => {
                const id = li.getAttribute('data-practice-question');
                const inputs = [...li.querySelectorAll('input')];
                inputs.find((i) => (i.value === keys[id].key) === right).click();
              });
              choose(false); quiz.querySelector('[data-practice-part=check]').click();
              const wrong = say();
              choose(true); quiz.querySelector('[data-practice-part=check]').click();
              return { wrong, right: say() };
            })()"""
        )
        assert "Every question answered correctly" not in graded["wrong"], graded
        assert "Every question answered correctly" in graded["right"], graded
        assert len(asked) == before, "answering a quiz asked the server for something"
        open_page.open(url)
        passed = open_page.evaluate(
            "document.querySelector('li[data-practice-kind=quiz]')"
            ".getAttribute('data-practice-state')"
        )
    assert passed == "passed"


def test_a_reading_mark_is_kept_in_the_browser_store_and_survives_a_reload(
    open_page: OpenPage, trees
) -> None:
    _tree, out, unit = trees
    with static(out) as (origin, _asked):
        url = f"{origin}/course/{unit.split('.studyforge/')[-1]}"
        open_page.open(url)
        button = "document.querySelector('[data-section=read-mark] button')"
        open_page.evaluate(f"{button}.click()")
        assert open_page.evaluate(f"{button}.getAttribute('aria-pressed')") == "true"
        open_page.open(url)
        assert open_page.evaluate(f"{button}.getAttribute('aria-pressed')") == "true"
        open_page.evaluate("localStorage.clear()")


def test_the_repository_link_is_built_from_the_address_and_from_no_other_source(
    open_page: OpenPage, trees
) -> None:
    _tree, out, unit = trees
    with static(out) as (origin, _asked):
        open_page.open(f"{origin}/course/{unit.split('.studyforge/')[-1]}")
        built = [
            open_page.evaluate(f"window.studyforgePreview.repository({host!r}, {path!r})")
            for host, path, _ in ADDRESSES
        ]
    assert built == [link for _, _, link in ADDRESSES]


def test_on_a_project_page_the_notes_link_the_readme_section_and_the_source_viewer(
    open_page: OpenPage, trees, tmp_path: Path
) -> None:
    _tree, out, unit = trees
    # ⭐ A loopback server cannot make a page's own `location` a github.io one, so the page is
    # opened with an EMPTY preview script and the real one is run over it with the address a
    # project page has.
    inert = tmp_path / "inert"
    shutil.copytree(out, inert)
    (inert / "course" / "preview.js").write_text("", encoding="utf-8")
    script = json.dumps(preview.PREVIEW_JS)
    with static(inert) as (origin, _asked):
        open_page.open(f"{origin}/course/{unit.split('.studyforge/')[-1]}")
        links = open_page.evaluate(
            f"""(() => {{
              const at = {{location: {{hostname: 'example-owner.github.io',
                                      pathname: '/example-course/index.html'}}}};
              new Function('window', {script})(at);
              const href = (selector) => [...document.querySelectorAll(selector)]
                .map((a) => a.getAttribute('href'));
              const notes = '[data-preview-note] a, [data-preview-banner] a';
              return {{run: href(notes), source: href('a[data-code-path]')}};
            }})()"""
        )
    base = "https://github.com/example-owner/example-course/blob/main/"
    assert links["run"] and set(links["run"]) == {f"{base}README.md#{tour.RUN_ANCHOR}"}, links
    assert links["source"] == [f"{base}archive/x/Source.java"], links


def test_the_same_page_unstripped_logs_the_missing_clip(
    open_page: OpenPage, trees, tmp_path: Path
) -> None:
    # ⛔ The negative control: without the preview's strip this exact page is the one that logs.
    tree, _out, unit = trees
    kept = tmp_path / "unstripped"
    shutil.copytree(tree, kept, ignore=shutil.ignore_patterns(".git"))
    watching(open_page)
    with static(kept) as (origin, _asked):
        open_page.open(f"{origin}/{unit}")
        console = entries(open_page)
    assert console, (
        "born vacuous: the unstripped page logs nothing, so a silent preview proves nothing"
    )
