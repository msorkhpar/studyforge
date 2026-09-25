"""Mirror of `src/studyforge/look/browser.py` (R12): finding a browser and asking it."""

from __future__ import annotations

import pytest

from studyforge.look import browser
from studyforge.look.browser import CANDIDATES, Profile, capture, find
from tests.studyforge.look.sites import a_browser, built, stand_in


def test_no_candidate_on_path_is_no_browser(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    assert find(None) is None


def test_a_candidate_on_path_is_found_by_its_name(tmp_path, monkeypatch):
    shim = tmp_path / CANDIDATES[-1]
    shim.write_text("#!/bin/sh\n", encoding="utf-8")
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert find(None) == str(shim)


def test_a_named_browser_is_used_when_it_runs_and_refused_when_it_does_not(tmp_path):
    runs = stand_in(tmp_path)
    assert find(runs) == runs
    assert find(str(tmp_path / "no-such-browser")) is None


@pytest.mark.parametrize(("uid", "sandboxed"), [(0, False), (1000, True)])
def test_the_sandbox_is_off_as_root_and_only_as_root(tmp_path, monkeypatch, uid, sandboxed):
    monkeypatch.setattr(browser.os, "geteuid", lambda: uid)
    assert ("--no-sandbox" not in browser._flags(tmp_path)) is sandboxed


def test_the_profile_is_gone_when_the_look_ends(tmp_path):
    with Profile() as profile:
        (profile / "cache").write_text("x", encoding="utf-8")
        assert profile.is_dir()
    assert not profile.exists()


def test_a_page_the_stand_in_renders_is_captured_as_a_png_and_a_dom(tmp_path):
    site = built(tmp_path)
    png, dom = tmp_path / "a.png", tmp_path / "a.dom.html"
    with Profile() as profile:
        seen = capture(stand_in(tmp_path), profile, site / "index.html", png, dom)
    assert seen.ok, seen.detail
    assert png.read_bytes().startswith(browser.PNG_SIGNATURE)
    assert "<body>" in dom.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("kwargs", "said"),
    [({"exit": 3}, "the screenshot launch exited 3"), ({"png": b"GIF89a"}, "wrote no PNG")],
)
def test_a_launch_that_fails_is_reported_and_never_quoted(tmp_path, kwargs, said):
    site = built(tmp_path)
    with Profile() as profile:
        seen = capture(
            stand_in(tmp_path, **kwargs),
            profile,
            site / "index.html",
            tmp_path / "a.png",
            tmp_path / "a.dom.html",
        )
    assert not seen.ok and said in seen.detail
    assert str(tmp_path) not in seen.detail


def test_a_real_browser_renders_a_built_page(tmp_path):
    # ⭐ The whole command's premise, read in whatever browser the visual harness
    # found: the page's title reaches the DOM its scripts left.
    binary = a_browser()
    site = built(tmp_path)
    png, dom = tmp_path / "a.png", tmp_path / "a.dom.html"
    with Profile() as profile:
        seen = capture(binary, profile, site / "index.html", png, dom)
    assert seen.ok, seen.detail
    assert "<title>Depth One Demo</title>" in dom.read_text(encoding="utf-8")
    assert png.stat().st_size > 1000
