"""Mirror of `src/studyforge/skills/adapter/figures.py` (R12): a lesson's figures reach its unit.

⛔ **Every expectation is a literal**, written before the run.
"""

from __future__ import annotations

import hashlib

import pytest

from studyforge.skills.adapter.figures import (
    FIGURE_TYPES,
    MAX_FIGURE_BYTES,
    FigureRefused,
    lift,
)

#: A picture's first bytes. ⭐ Nothing here reads a picture, so a header is enough.
PNG = b"\x89PNG\r\n\x1a\n" + bytes(24)

LESSON = "lessons/two/README.md"


def image(src, alt="The feasible region, shaded"):
    return {"type": "image", "src": src, "alt": alt, "width": None}


@pytest.fixture
def root(tmp_path):
    (tmp_path / "lessons" / "two" / "figures").mkdir(parents=True)
    (tmp_path / "lessons" / "two" / "figures" / "region.png").write_bytes(PNG)
    (tmp_path / "lessons" / "shared").mkdir()
    (tmp_path / "lessons" / "shared" / "axes.svg").write_text("<svg/>\n", encoding="utf-8")
    return tmp_path


def test_a_figure_is_read_beside_its_lesson_and_declared_as_an_asset(root):
    lifted = lift(root, LESSON, [{"type": "para", "text": "x"}, image("figures/region.png")])
    assert lifted.blocks == [{"type": "para", "text": "x"}, image("media/region.png")]
    assert lifted.assets == [
        {
            "remote": None,
            "local": "media/region.png",
            "sha256": hashlib.sha256(PNG).hexdigest(),
            "bytes": len(PNG),
            "content_type": "image/png",
            "kind": "image",
        }
    ]
    assert [local for local, _ in lifted.files] == ["media/region.png"]


def test_a_figure_in_a_sibling_folder_and_inside_a_quote_is_carried(root):
    lifted = lift(root, LESSON, [{"type": "quote", "blocks": [image("../shared/axes.svg")]}])
    assert lifted.blocks == [{"type": "quote", "blocks": [image("media/axes.svg")]}]
    assert lifted.assets[0]["content_type"] == "image/svg+xml"


def test_one_file_named_twice_is_one_asset(root):
    lifted = lift(root, LESSON, [image("figures/region.png"), image("./figures/region.png")])
    assert len(lifted.assets) == 1
    assert len(lifted.files) == 1


def test_a_remote_figure_and_one_the_reader_already_carried_are_left_as_written(root):
    declared = [{"local": "media/kept.png"}]
    blocks = [image("https://example.invalid/plot.png"), image("media/kept.png")]
    lifted = lift(root, LESSON, blocks, declared)
    assert lifted.blocks == blocks
    assert lifted.assets == []


def test_placing_copies_each_figure_into_the_units_own_directory(root, tmp_path):
    lifted = lift(root, LESSON, [image("figures/region.png")])
    unit = tmp_path / "archive" / "units" / "unit-02"
    placed = lifted.place(unit)
    assert placed == [unit / "media" / "region.png"]
    assert (unit / "media" / "region.png").read_bytes() == PNG


@pytest.mark.parametrize("alt", ["", "   ", None])
def test_a_figure_with_no_alternative_text_is_refused(root, alt):
    with pytest.raises(FigureRefused, match="no alternative text"):
        lift(root, LESSON, [image("figures/region.png", alt=alt)])


@pytest.mark.parametrize(
    "src",
    ["figures/missing.png", "../../../outside.png", "/etc/region.png", "C:/region.png"],
)
def test_a_figure_that_names_no_file_inside_the_corpus_is_refused_quoting_no_path(root, src):
    with pytest.raises(FigureRefused, match="names no file inside the corpus") as refused:
        lift(root, LESSON, [image(src)])
    assert src not in str(refused.value)
    assert str(root) not in str(refused.value)


def test_a_file_that_is_not_a_picture_is_refused(root):
    (root / "lessons" / "two" / "figures" / "region.pdf").write_bytes(b"%PDF")
    with pytest.raises(FigureRefused, match="not a picture"):
        lift(root, LESSON, [image("figures/region.pdf")])
    assert ".pdf" not in FIGURE_TYPES


def test_a_figure_over_the_size_limit_is_refused(root):
    (root / "lessons" / "two" / "figures" / "huge.png").write_bytes(bytes(MAX_FIGURE_BYTES + 1))
    with pytest.raises(FigureRefused, match="over the"):
        lift(root, LESSON, [image("figures/huge.png")])


def test_two_different_files_with_one_name_are_refused(root):
    (root / "lessons" / "shared" / "region.png").write_bytes(PNG + b"other")
    with pytest.raises(FigureRefused, match="same file name"):
        lift(root, LESSON, [image("figures/region.png"), image("../shared/region.png")])
