"""Mirror of `src/studyforge/look/__init__.py` (R12): the command, and what it refuses."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.exitcodes import UNUSABLE
from studyforge.look import NOT_RENDERED, main
from studyforge.look.browser import CANDIDATES
from tests.studyforge.look.sites import built, stand_in


def tree(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


def test_every_chosen_page_is_captured_and_the_site_gains_nothing(tmp_path, capsys):
    site = built(tmp_path)
    capsys.readouterr()
    before = tree(site)
    out = tmp_path / "shots"
    out.mkdir()
    assert main([str(site), "--out", str(out), "--browser", stand_in(tmp_path)]) == 0
    said = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in said[:3]] == ["looked"] * 3
    assert said[-1].startswith("look: 3 of 3 page(s) rendered")
    assert len(list(out.iterdir())) == 6
    assert tree(site) == before


def test_a_page_that_did_not_render_fails_the_look(tmp_path, capsys):
    site = built(tmp_path)
    out = tmp_path / "shots"
    out.mkdir()
    argv = [str(site), "--out", str(out), "--browser", stand_in(tmp_path, exit=5), "--all"]
    assert main(argv) == NOT_RENDERED
    said = capsys.readouterr().out
    assert said.count("FAILED ") == 5 and "look: 0 of 5 page(s) rendered" in said


def test_an_output_directory_inside_the_site_is_refused(tmp_path, capsys):
    # ⛔ A site is often the corpus root, and a picture of a page is not a file
    # the corpus should gain (R3).
    site = built(tmp_path)
    inside = site / ".studyforge"
    before = tree(site)
    assert main([str(site), "--out", str(inside), "--browser", stand_in(tmp_path)]) == UNUSABLE
    assert "inside the site" in capsys.readouterr().err
    assert tree(site) == before


@pytest.mark.parametrize("missing", ["site", "out"])
def test_a_missing_site_or_output_directory_is_refused(tmp_path, capsys, missing):
    site = built(tmp_path) if missing == "out" else tmp_path / "nothing"
    out = tmp_path / "nothing-either" if missing == "out" else tmp_path
    assert main([str(site), "--out", str(out), "--browser", stand_in(tmp_path)]) == UNUSABLE
    assert "look: " in capsys.readouterr().err


def test_no_browser_names_what_was_searched_and_both_ways_forward(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    site = built(tmp_path)
    assert main([str(site), "--out", str(tmp_path)]) == UNUSABLE
    said = capsys.readouterr().err
    assert all(name in said for name in CANDIDATES)
    assert "--browser" in said and "studyforge serve" in said
