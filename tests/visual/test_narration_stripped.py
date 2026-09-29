"""A site built with no narration names no clip, so its pages ask for nothing.

⭐ **Register requirement (2026-09-28): a learner's site is served and navigated with
no error.** A page whose clips are absent asks its first clip and the browser logs one
`404` per page, so a build that KNOWS it holds no clip removes the references instead
(`standalone.images.STRIP_CLIPS`, run by the site image's without-narration stage).
This reads the effect in a real browser, over the real server: no page names a clip,
none is requested, the console holds nothing, and the transport stays hidden.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import images
from tests.visual.page import OpenPage
from tests.visual.test_narration_clips import (
    HREF,
    _built,
    clip_requests,
    loud,
    narrated_page,
    opened,
    shown,
)
from tests.visual.test_served_faces import serving


def strip(root: Path) -> None:
    """Run the site image's own strip step over `root`, as its build runs it."""
    subprocess.run(["sh", "-c", images.STRIP_CLIPS.replace(images.CORPUS, str(root))], check=True)


@pytest.fixture(scope="module")
def trees(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, str]:
    made = tmp_path_factory.mktemp("silent")
    root = _built(made, "absent")
    page = narrated_page(root)
    kept = tmp_path_factory.mktemp("kept") / "plain"
    shutil.copytree(root, kept)
    strip(root)
    return root, kept, page


def test_a_stripped_site_names_no_clip_in_any_page(trees) -> None:
    root, kept, page = trees
    assert HREF.search((kept / page).read_text(encoding="utf-8")), "born vacuous: nothing to strip"
    assert not any("data-audio" in one.read_text(encoding="utf-8") for one in root.rglob("*.html"))


def test_a_stripped_page_asks_for_no_clip_and_its_console_is_clean(
    open_page: OpenPage, trees
) -> None:
    root, _kept, page = trees
    with serving(root, root) as origin:
        opened(open_page, f"{origin}/{page}")
        state = shown(open_page)
        console = loud(open_page)
        asked = clip_requests(open_page)
    assert state["player"] is False and state["src"] == ""
    assert asked == [], asked
    assert console == [], console


def test_the_same_page_unstripped_logs_the_probes_error(open_page: OpenPage, trees) -> None:
    # ⛔ The negative control: without the strip this exact page is the one that logs.
    _root, kept, page = trees
    with serving(kept, kept) as origin:
        opened(open_page, f"{origin}/{page}")
        console = loud(open_page)
    assert [level for level, _ in console] == ["error"], console
