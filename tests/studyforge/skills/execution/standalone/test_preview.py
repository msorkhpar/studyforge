"""Mirror of `src/studyforge/skills/execution/standalone/preview.py` and `preview.py` (R12).

⭐ Two trees are written here in the shapes a learner tree really has (pages under the hidden
directory, and pages beside their source under `src/study`), with every server-only part a
built page carries: narration, a practice panel, a code example. Each clause is read off the
files the preview writes, and every link of every page is resolved against them.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from studyforge.skills.execution.standalone import preview

#: The narration player exactly as a built page carries it, and its audio element.
PLAYER = (
    '<footer id="player" hidden>\n'
    '<div id="track" role="progressbar" aria-label="Progress through this '
    'unit" aria-valuemin="0"><div id="fill"></div></div>\n'
    "<div>\n"
    '<button id="previous" type="button" aria-label="Previous '
    'passage"><span aria-hidden="true">&#8249;</span></button>\n'
    '<button id="play" type="button"><span data-state="paused">Play '
    'narration</span><span data-state="playing" hidden>Pause '
    "narration</span></button>\n"
    '<button id="next" type="button" aria-label="Next passage"><span '
    'aria-hidden="true">&#8250;</span></button>\n'
    '<select id="speed" aria-label="Playback speed">\n'
    '<option value="0.75">0.75&#215;</option>\n'
    '<option value="1" selected>1&#215;</option>\n'
    '<option value="1.25">1.25&#215;</option>\n'
    '<option value="1.5">1.5&#215;</option>\n'
    '<option value="1.75">1.75&#215;</option>\n'
    '<option value="2">2&#215;</option>\n'
    "</select>\n"
    '<span><span id="where"></span><span id="counter"></span></span>\n'
    '<span id="status" role="status" aria-live="polite"><span '
    'data-state="missing" hidden>This passage has no audio on disk, so '
    "narration stops here rather than pretending to play it. Move on with "
    'Next.</span><span data-state="blocked" hidden>Your browser would not '
    "start audio on its own. Press play once and it will keep going from "
    'there.</span><span data-state="none" hidden>None of this unit\'s clips '
    "are on disk, so there is nothing to play. They were recorded once "
    "&#8212; re-run the narration pass and the audio comes back with "
    "them.</span></span>\n"
    "<p>Space plays and pauses. Left and right arrows move to the next "
    "passage and scroll it into view. Click any paragraph to start reading "
    "from there.</p>\n"
    "</div>\n"
    "</footer>\n"
    '<audio id="narrator" preload="none"></audio>\n'
)
PRACTICE = (
    '<section data-practice="m/unit-01/practice-prose" data-corpus="c" aria-label="Practice" '
    'tabindex="-1">\n<p data-practice-part="offline">Running needs the local study server.</p>\n'
    '<div data-practice-part="editor" hidden><div data-practice-frame="main"></div></div>\n'
    '<p data-practice-part="controls" hidden><button type="button" data-practice-act="run">Run'
    '</button><button type="button" data-practice-act="test">Submit</button></p>\n</section>\n'
)
QUIZ = (
    '<section data-practice-quiz="m/unit-01/quiz" data-corpus="c" aria-label="Questions">\n'
    '<p data-practice-part="offline">Checking answers needs this page\'s script.</p>\n</section>\n'
)


def example(source: str) -> str:
    return (
        '<div data-code-examples data-corpus="c">\n'
        f'<details data-code-example data-code-open="{source}">\n'
        f"<summary>A.java</summary>\n"
        f'<ul class="items"><li>Source: <a href="{{up}}{source}" rel="noopener noreferrer" '
        f'data-code-path="{source}">A.java</a></li></ul>\n'
        '<div data-code-part="editor" hidden><div data-code-frame="main"></div></div>\n'
        '<p data-code-part="controls" hidden><button type="button" data-code-act="test">Run tests'
        "</button></p>\n"
        '<p data-code-part="plain">Each file opens as plain text.</p>\n</details>\n</div>\n'
    )


def page(
    *, up: str, assets: str, index: str, other: str, body: str = "", audio: bool = True
) -> str:
    tag = ' data-audio="audio/x.mp3"' if audio else ""
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>T</title>\n'
        f'<link rel="stylesheet" href="{assets}/page.css">\n</head>\n<body>\n'
        '<a href="#content">Skip to the content</a>\n'
        f'<header><nav><a href="{index}">Course</a></nav><h1{tag}>Unit</h1></header>\n'
        f'<main id="content">\n<p{tag}>Text with <a href="{other}">a link</a>.</p>\n'
        f"{body.replace('{up}', up)}</main>\n{PLAYER if audio else ''}"
        f'<script src="{assets}/page.js" defer></script>\n</body>\n</html>\n'
    )


def hidden_tree(root: Path) -> Path:
    """Pages under `.studyforge/`, the root index beside it, and the source the example names."""
    write(root / ".studyforge/assets/page.css", "body{}")
    write(root / ".studyforge/assets/page.js", "window.studyforge={};")
    write(root / "src/A.java", "class A {}")
    body = PRACTICE + QUIZ + example("src/A.java")
    write(
        root / ".studyforge/g/units/u1.unit.html",
        page(
            up="../../../",
            assets="../../assets",
            index="../../../index.html",
            other="u2.unit.html",
            body=body,
        ),
    )
    write(
        root / ".studyforge/g/units/u2.unit.html",
        page(
            up="../../../",
            assets="../../assets",
            index="../../../index.html",
            other="u1.unit.html",
            audio=False,
        ),
    )
    write(
        root / "index.html",
        page(
            up="",
            assets=".studyforge/assets",
            index="index.html",
            other=".studyforge/g/units/u1.unit.html",
            audio=False,
        ),
    )
    return root


def sibling_tree(root: Path) -> Path:
    """Pages beside their source, in `src/study/`, with the assets two levels up."""
    write(root / ".studyforge/assets/page.css", "body{}")
    write(root / ".studyforge/assets/page.js", "window.studyforge={};")
    write(
        root / "src/study/a.unit.html",
        page(
            up="../../",
            assets="../../.studyforge/assets",
            index="../../index.html",
            other="a.unit.html",
        ),
    )
    write(
        root / "index.html",
        page(
            up="",
            assets=".studyforge/assets",
            index="index.html",
            other="src/study/a.unit.html",
            audio=False,
        ),
    )
    return root


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def made(tmp_path: Path, build=hidden_tree) -> Path:
    out = tmp_path / "preview"
    preview.preview(build(tmp_path / "tree"), out)
    return out


def files(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def html_of(root: Path) -> dict[str, str]:
    return {
        one: (root / one).read_text(encoding="utf-8")
        for one in files(root)
        if one.endswith(".html")
    }


def dangling(root: Path) -> list[str]:
    """Every relative href or src of every page that names no file under `root`."""
    broken = []
    for name, text in html_of(root).items():
        for url in re.findall(r'\b(?:href|src)="([^"]*)"', text):
            split = urlsplit(url)
            if split.scheme or not split.path:
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), unquote(split.path))
            )
            if not (root / target).is_file():
                broken.append(f"{name}: {url}")
    return broken


@pytest.mark.parametrize("build", [hidden_tree, sibling_tree])
def test_no_path_of_the_preview_starts_with_a_dot_so_the_pages_action_packs_all_of_it(
    tmp_path, build
):
    out = made(tmp_path, build)
    dots = [one for one in files(out) if any(part.startswith(".") for part in one.split("/"))]
    assert dots == []
    assert (out / "course/assets/page.js").is_file() and not (out / ".studyforge").exists()


@pytest.mark.parametrize("build", [hidden_tree, sibling_tree])
def test_every_link_of_every_page_is_recomputed_and_reaches_a_file(tmp_path, build):
    out = made(tmp_path, build)
    assert dangling(out) == []
    assert all(".studyforge" not in text for text in html_of(out).values())


def test_a_link_left_as_the_hidden_directory_would_be_seen_as_broken(tmp_path):
    out = made(tmp_path)
    (out / "index.html").write_text(
        (out / "index.html")
        .read_text(encoding="utf-8")
        .replace("course/assets", ".studyforge/assets"),
        encoding="utf-8",
    )
    assert dangling(out)


def test_only_what_the_index_reaches_is_written(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    write(tree / "practice/x/notes.html", "<html><body>x</body></html>")
    write(tree / "compose.yaml", "services: {}")
    out = tmp_path / "preview"
    made_ = preview.preview(tree, out)
    assert "src/A.java" not in files(out) and "compose.yaml" not in files(out)
    assert not any(one.startswith("practice/") for one in files(out))
    assert made_.pages == (
        "course/g/units/u1.unit.html",
        "course/g/units/u2.unit.html",
        "index.html",
    )
    assert tuple(files(out)) == tuple(sorted([*made_.pages, *made_.files]))


def test_narration_is_removed_and_a_note_says_where_it_lives(tmp_path):
    out = made(tmp_path)
    text = html_of(out)["course/g/units/u1.unit.html"]
    for gone in ("data-audio", 'id="player"', 'id="narrator"', "Play narration"):
        assert gone not in text, gone
    assert text.count('data-preview-note="narration"') == 1
    assert 'data-preview-note="narration"' not in html_of(out)["course/g/units/u2.unit.html"]


def test_a_practice_panel_is_replaced_by_a_note_with_no_run_submit_or_editor(tmp_path):
    text = html_of(made(tmp_path))["course/g/units/u1.unit.html"]
    assert '<section data-practice="m/unit-01/practice-prose"' in text
    for gone in (
        "data-practice-act",
        'data-practice-part="editor"',
        "data-practice-frame",
        "study server",
    ):
        assert gone not in text, gone
    assert text.count('data-preview-note="practice"') == 1
    assert "locally with Docker" in text


def test_a_quiz_is_left_exactly_as_it_was_because_the_page_grades_it(tmp_path):
    text = html_of(made(tmp_path))["course/g/units/u1.unit.html"]
    assert QUIZ in text


def test_a_code_example_keeps_its_files_without_links_to_files_that_are_not_there(tmp_path):
    out = made(tmp_path)
    text = html_of(out)["course/g/units/u1.unit.html"]
    assert "<summary>A.java</summary>" in text and 'data-code-path="src/A.java"' in text
    assert 'href="../../../src/A.java"' not in text and 'A.java" rel' not in text
    for gone in ("data-code-act", "data-code-frame", "data-code-part", "Each file opens"):
        assert gone not in text, gone
    assert text.count('data-preview-note="example"') == 1
    assert not any(one.endswith(".java") for one in files(out))


def test_every_page_carries_the_banner_once_with_the_style_and_the_script(tmp_path):
    for name, text in html_of(made(tmp_path)).items():
        assert text.count("data-preview-banner") == 1, name
        assert text.count("Read-only preview") == 1, name
        assert "preview.css" in text and "preview.js" in text, name
        assert text.index("data-preview-banner") < text.index("<header>"), name
        assert text.index("Skip to the content") < text.index("data-preview-banner"), name


def test_no_page_and_no_script_names_an_account_or_a_repository(tmp_path):
    out = made(tmp_path)
    for one in files(out):
        text = (out / one).read_text(encoding="utf-8")
        assert not re.search(r"github\.com/[A-Za-z0-9]", text), one
        assert not re.search(r"github\.io/[A-Za-z0-9]", text), one
    assert "location" in preview.PREVIEW_JS or "window.location" in preview.PREVIEW_JS


def test_the_preview_is_the_same_bytes_every_time(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    preview.preview(tree, tmp_path / "one")
    preview.preview(tree, tmp_path / "two")
    assert files(tmp_path / "one") == files(tmp_path / "two")
    for one in files(tmp_path / "one"):
        assert (tmp_path / "one" / one).read_bytes() == (tmp_path / "two" / one).read_bytes()


def test_a_page_with_no_server_part_changes_only_by_what_the_preview_adds(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    before = (tree / ".studyforge/g/units/u2.unit.html").read_text(encoding="utf-8")
    out = tmp_path / "out"
    preview.preview(tree, out)
    after = (out / "course/g/units/u2.unit.html").read_text(encoding="utf-8")
    trimmed = re.sub(r"<div data-preview-banner.*?</div>\n", "", after, flags=re.DOTALL)
    trimmed = re.sub(
        r'<link rel="icon"[^>]*>\n|<link rel="stylesheet" href="[^"]*preview.css">\n', "", trimmed
    )
    trimmed = re.sub(r'<script src="[^"]*preview.js" defer></script>\n', "", trimmed)
    assert trimmed == before


def test_a_target_that_is_not_empty_is_refused(tmp_path):
    tree, out = hidden_tree(tmp_path / "tree"), tmp_path / "out"
    write(out / "left.txt", "x")
    with pytest.raises(preview.PreviewRefused, match="not empty"):
        preview.preview(tree, out)


def test_a_tree_with_no_index_is_refused(tmp_path):
    with pytest.raises(preview.PreviewRefused, match="no index.html"):
        preview.preview(tmp_path, tmp_path / "out")


def test_a_link_to_a_file_that_is_not_in_the_tree_is_refused_by_name(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    (tree / ".studyforge/g/units/u2.unit.html").unlink()
    with pytest.raises(preview.PreviewRefused, match="u2.unit.html"):
        preview.preview(tree, tmp_path / "out")


def test_a_link_that_leaves_the_tree_is_refused(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    index = tree / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace("Course</a>", 'Out</a><a href="../x.html">x</a>'),
        encoding="utf-8",
    )
    with pytest.raises(preview.PreviewRefused, match="leaves the tree"):
        preview.preview(tree, tmp_path / "out")


def test_a_dot_directory_other_than_the_hidden_one_is_refused(tmp_path):
    tree = hidden_tree(tmp_path / "tree")
    write(tree / ".other/page.html", "<html><head></head><body></body></html>")
    index = tree / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            "Course</a>", 'Course</a><a href=".other/page.html">o</a>'
        ),
        encoding="utf-8",
    )
    with pytest.raises(preview.PreviewRefused, match="dot"):
        preview.preview(tree, tmp_path / "out")


def test_a_practice_panel_that_holds_a_section_is_refused_rather_than_cut(tmp_path):
    with pytest.raises(preview.PageRefused, match="section"):
        preview.remove_server_parts('<section data-practice="k"><section>inner</section></section>')


def test_the_command_writes_the_preview_and_says_what_it_holds(tmp_path, capsys):
    tree = hidden_tree(tmp_path / "tree")
    assert preview.main([str(tree), str(tmp_path / "out")]) == 0
    assert "3 pages" in capsys.readouterr().out
    assert preview.main([str(tree), str(tmp_path / "out")]) == 1
    assert "refused" in capsys.readouterr().out
    assert preview.main([]) == 2


# The page edits, read off the text each returns for a page shaped like a built one.

PAGE = (
    "<!doctype html><html><head><title>T</title></head><body>"
    '<a href="#content">Skip to the content</a><header><h1 data-audio="a.mp3">T</h1></header>'
    '<main id="content"><p data-audio="b.mp3">Text</p></main>'
    '<footer id="player" hidden><button id="play">Play narration</button></footer>'
    '<audio id="narrator" preload="none"></audio>'
    '<script src="page.js" defer></script></body></html>'
)


def test_every_reference_to_narration_is_removed_and_one_note_stands_in_its_place():
    text, narrated = preview.remove_server_parts(PAGE)
    assert narrated is True
    for gone in ("data-audio", 'id="player"', 'id="narrator"', "Play narration"):
        assert gone not in text
    assert text.count('data-preview-note="narration"') == 1
    assert text.index("</header>") < text.index("data-preview-note")


def test_a_page_with_no_narration_is_not_given_the_note():
    text, narrated = preview.remove_server_parts("<html><body><p>x</p></body></html>")
    assert narrated is False and "data-preview-note" not in text


def test_a_code_example_without_its_summary_or_files_is_refused():
    with pytest.raises(preview.PageRefused, match="summary"):
        preview.remove_server_parts("<details data-code-example><p>x</p></details>")


def test_a_source_link_loses_its_href_and_keeps_its_path_for_the_script():
    example = (
        "<details data-code-example><summary>A</summary>"
        '<ul class="items"><li><a href="../../A.java" rel="noopener" data-code-path="a/A.java">A'
        "</a></li></ul></details>"
    )
    text, _ = preview.remove_server_parts(example)
    assert 'data-code-path="a/A.java"' in text and 'A.java"' in text
    assert "href=" not in text


def test_the_banner_the_style_and_the_script_are_added_once_and_in_their_places():
    done = preview.finish(PAGE, assets="../course")
    assert done.count("data-preview-banner") == 1
    assert done.index("Skip to the content") < done.index("data-preview-banner")
    assert done.index("data-preview-banner") < done.index("<header>")
    assert '<link rel="stylesheet" href="../course/preview.css">' in done
    assert done.index("preview.js") > done.index("page.js")
    assert 'rel="icon" href="data:,"' in done


def test_a_page_that_already_has_an_icon_keeps_it_and_gains_none():
    page = PAGE.replace("<title>", '<link rel="icon" href="x.ico"><title>')
    assert preview.finish(page, assets=".").count('rel="icon"') == 1


def test_a_page_without_a_head_or_a_body_is_refused():
    with pytest.raises(preview.PageRefused, match="head and a body"):
        preview.finish("<p>x</p>", assets=".")


def test_the_script_holds_no_owner_repository_or_host_and_builds_from_location():
    js = preview.PREVIEW_JS
    assert "window.location.hostname" in js and "window.location.pathname" in js
    assert not re.search(r"github\.(com|io)/[A-Za-z0-9]", js)
    assert preview.RUN_ANCHOR in js and "@ANCHOR@" not in js
    for note in (preview.PRACTICE_NOTE, preview.EXAMPLE_NOTE, preview.NARRATION_NOTE):
        assert "locally with Docker" in note
        assert preview.RUN_LINK in note
