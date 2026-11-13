"""Mirror of `generate/diagrampages.py` (R12): which corpus carries a diagram at all."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from studyforge.generate import diagrampages


def corpus_with(root: Path, lesson: dict) -> SimpleNamespace:
    unit = root / "unit-01"
    unit.mkdir(parents=True)
    (unit / "lesson-1.json").write_text(json.dumps(lesson), encoding="utf-8")
    return SimpleNamespace(units=(SimpleNamespace(directory=unit),))


def test_a_mermaid_block_marks_the_corpus(tmp_path):
    block = {"blocks": [{"type": "code", "lang": "mermaid", "text": "graph LR; A-->B"}]}
    assert diagrampages.wanted(corpus_with(tmp_path, block))


def test_a_diagram_inside_a_list_item_marks_it_too(tmp_path):
    item = [{"type": "code", "lang": "mermaid", "text": "graph LR; A-->B"}]
    nested = {"blocks": [{"type": "list", "ordered": False, "items": [["Step", *item]]}]}
    assert diagrampages.wanted(corpus_with(tmp_path, nested))


def test_the_word_alone_does_not(tmp_path):
    plain = {"blocks": [{"type": "code", "lang": "java", "text": "class Mermaid {}"},
                        {"type": "para", "text": "A `mermaid` fence draws a diagram."}]}
    assert not diagrampages.wanted(corpus_with(tmp_path, plain))


# --- a whole build ---------------------------------------------------------------------------

LESSON = Path("archive/depth-one/raw/prose/unit-01/lesson-1.json")
DIAGRAM_FILES = [
    ".studyforge/assets/diagram.css",
    ".studyforge/assets/diagram.js",
    ".studyforge/assets/mermaid.min.js",
]


def built(where: Path, *, with_diagram: bool) -> dict[str, bytes]:
    """Copy `depth1`, give its first lesson a diagram when asked, build it; every file written."""
    import shutil

    from studyforge.archive.blocks import counts_of
    from studyforge.archive.document import content_sha256, render
    from studyforge.generate import write_site
    from tests.studyforge.exercise.quiz.depth1 import fixture_root
    from tests.studyforge.exercise.quiz.mock_corpus import built_files

    root = where / "depth1"
    shutil.copytree(fixture_root(), root)
    if with_diagram:
        document = json.loads((root / LESSON).read_text(encoding="utf-8"))
        document["blocks"].append({"type": "code", "lang": "mermaid", "text": "graph LR\n  A-->B"})
        document["counts"] = counts_of(document["blocks"])
        document["content_sha256"] = content_sha256(document["blocks"])
        (root / LESSON).write_text(render(document), encoding="utf-8")
    write_site(root, root)
    return built_files(root)


def test_a_corpus_with_a_diagram_writes_mermaid_and_only_its_page_links_it(tmp_path):
    plain = built(tmp_path / "plain", with_diagram=False)
    drawn = built(tmp_path / "drawn", with_diagram=True)
    assert not [path for path in plain if path in DIAGRAM_FILES or "mermaid" in path]
    assert sorted(set(drawn) - set(plain)) == DIAGRAM_FILES
    pages = {path: body.decode("utf-8") for path, body in drawn.items() if path.endswith(".html")}
    linking = sorted(path for path, page in pages.items() if "mermaid.min.js" in page)
    assert len(linking) == 1 and linking[0].endswith(".unit.html")
    # ⭐ The page the build framed as a diagram is the one whose lesson `wanted` read: the two
    # modules agree on the language by behaviour, not by importing each other.
    assert 'data-frame="diagram"' in pages[linking[0]]
    for path, page in pages.items():
        if path not in linking:
            assert "diagram.js" not in page and "diagram.css" not in page, path
