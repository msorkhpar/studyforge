"""The read-only preview of a corpus of four languages reads in its default mode, in a browser.

⭐ **The preview a real build produces is read, not the build.** A corpus of four languages with
code practices is built, made into a preview with the shipped preview tool, and opened from a
static server and from `file://`: it builds with no refusal, each practice panel is replaced by
its note, the banner is the one a corpus with no modes has, the default mode's first tab of each
example is open, and the question is asked on every load of a file page while the page reads the
default mode until it is answered.

⛔ **Each clause is asserted both ways (R12).** A page opened from a server keeps the answer and a
file page asks again; a practice outside the default mode is greyed in the preview and one inside
is not; the corpus that declares no modes has the same banner and no mode question.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import preview
from tests.studyforge.generate import four_corpus as four
from tests.visual.four import ASKING, CLEAR, STATE, SWITCHED, VISIBLE, greyed
from tests.visual.page import WIDE, OpenPage
from tests.visual.test_preview import static

BANNER = "document.querySelector('[data-preview-banner]').textContent.replace(/\\s+/g, ' ').trim()"
NOTES = "document.querySelectorAll('[data-preview-note=practice]').length"
UNIT = "course/demo/units/unit-05/unit-05-practices-5.unit.html"
EXAMPLES = "course/demo/units/unit-01/unit-01-shared-ideas-1.unit.html"


@pytest.fixture(scope="module")
def previews(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """The preview of the corpus with its modes, and of the same corpus with none."""
    where = tmp_path_factory.mktemp("language-preview")
    made = {}
    for name, manifest in (
        ("modes", four.declared(absent="grey", mixed=True)),
        ("plain", {"corpus_api": 8, "languages": four.declared()["languages"]}),
    ):
        tree = four.build(where, name, manifest, code=True)
        made[name] = where / f"{name}-preview"
        preview.preview(tree, made[name])
    return made


def test_the_preview_of_a_corpus_of_four_languages_builds_and_replaces_every_panel(
    previews: dict[str, Path],
) -> None:
    page = (previews["modes"] / UNIT).read_text(encoding="utf-8")
    assert page.count('data-preview-note="practice"') == 4
    assert 'data-practice-part="editor"' not in page, "no editor, run or submit is left"
    panels = re.findall(r'<section data-practice="[^"]*"[^>]*>', page)
    assert [re.search(r'data-lang="([^"]+)"', one).group(1) for one in panels] == [
        "aa bb",
        "cc",
        "aa bb cc dd",
        "dd",
    ]
    assert (previews["modes"] / "course/assets/modes.js").is_file()
    assert not (previews["plain"] / "course/assets/modes.js").exists()


def test_the_banner_is_the_one_a_corpus_with_no_modes_has_and_adds_no_mode_of_its_own(
    open_page: OpenPage, previews: dict[str, Path]
) -> None:
    said = {}
    for name in ("modes", "plain"):
        with static(previews[name]) as (origin, _):
            open_page.resize(*WIDE)
            open_page.open(f"{origin}/{UNIT}")
            said[name] = open_page.evaluate(BANNER)
            assert open_page.evaluate(NOTES) == 4
    assert said["modes"] == said["plain"]
    assert "mode" not in said["modes"].lower()


def test_served_statically_the_default_mode_is_read_and_the_answer_is_kept(
    open_page: OpenPage, previews: dict[str, Path], capture_dir: Path
) -> None:
    with static(previews["modes"]) as (origin, _):
        open_page.resize(*WIDE)
        open_page.open(f"{origin}/{UNIT}")
        open_page.evaluate(CLEAR)
        open_page.open(f"{origin}/{UNIT}")
        assert open_page.evaluate(ASKING)["shown"] is True
        assert open_page.evaluate(SWITCHED)["pressed"] == ["only-aa"]
        assert greyed(open_page) == [False, True, False, True]
        open_page.capture(capture_dir / "preview-static-first-visit.png")
        open_page.evaluate("document.querySelector('[data-section=mode-question] button').click()")
        open_page.open(f"{origin}/{UNIT}")
        assert open_page.evaluate(ASKING)["shown"] is False
        open_page.evaluate(CLEAR)


def test_a_file_page_asks_on_every_load_and_reads_the_default_mode_until_answered(
    open_page: OpenPage, previews: dict[str, Path], capture_dir: Path
) -> None:
    where = f"file://{previews['modes'] / UNIT}"
    open_page.resize(*WIDE)
    for _ in range(2):
        open_page.open(where)
        assert open_page.evaluate(ASKING)["shown"] is True
        assert open_page.evaluate(SWITCHED)["mode"] == "only-aa"
        assert open_page.evaluate(VISIBLE) == ["prose"]
    open_page.capture(capture_dir / "preview-file-asks.png")
    open_page.evaluate(
        "document.querySelector('[data-section=mode-question] [data-mode-choice=only-cc]').click()"
    )
    assert open_page.evaluate(ASKING)["shown"] is False
    assert open_page.evaluate(SWITCHED)["mode"] == "only-cc"
    assert greyed(open_page) == [True, False, False, True]


def test_each_example_of_the_preview_opens_the_default_modes_first_tab(
    open_page: OpenPage, previews: dict[str, Path]
) -> None:
    with static(previews["modes"]) as (origin, _):
        open_page.resize(*WIDE)
        open_page.open(f"{origin}/{EXAMPLES}")
        state = {one["id"]: one for one in open_page.evaluate(STATE)}  # type: ignore[union-attr]
    assert state["quad"]["selected"] == ["aa"] and state["quad"]["panels"] == ["aa"]
    assert state["duo"]["selected"] == ["aa"] and state["duo"]["note"] is None
    assert state["solo"]["tabs"] == ["aa"] and state["solo"]["disabled"] == ["aa"]
    assert state["solo"]["note"] == "Available in: Cc."


def test_the_preview_of_a_corpus_with_no_modes_asks_nothing(
    open_page: OpenPage, previews: dict[str, Path]
) -> None:
    with static(previews["plain"]) as (origin, _):
        open_page.resize(*WIDE)
        open_page.open(f"{origin}/{UNIT}")
        assert open_page.evaluate(ASKING) is None
        assert open_page.evaluate("document.querySelector('[data-section=mode]')") is None
