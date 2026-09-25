"""`studyforge serve --published`: the form a course's compose runs, refused anywhere else.

⭐ Refused before anything binds: outside a container (no marker a container
runtime leaves), with no run service declared, or beside `--site`. ⛔ The form
that does bind (`0.0.0.0`, inside its container) is read live, in the compose,
and never started here on a host's every interface.
"""

from __future__ import annotations

import io

import pytest

from studyforge.cli.serve import build_parser, main
from studyforge.serve import published
from studyforge.validate.cli import UNUSABLE
from tests.studyforge.serve.routes.running import served_copy


@pytest.fixture
def root(tmp_path):
    return served_copy(tmp_path)


def said(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    code = main(argv, out, started=lambda server: pytest.fail("a refused form bound a server"))
    return code, out.getvalue()


def test_the_flag_is_offered_and_off_by_default():
    assert build_parser().parse_args(["r"]).published is False
    assert build_parser().parse_args(["r", "--published"]).published is True


def test_outside_a_container_it_is_refused_and_nothing_binds(root, monkeypatch, tmp_path):
    monkeypatch.setattr(published, "CONTAINER_MARKERS", (str(tmp_path / "absent"),))
    monkeypatch.setenv("STUDYFORGE_RUN_SERVICE", "runner")
    code, out = said([str(root.parent), "--published", "--port", "0"])
    assert code == UNUSABLE
    assert published.NOT_A_CONTAINER in out


def test_inside_a_container_with_no_run_service_it_is_refused(root, monkeypatch, tmp_path):
    marker = tmp_path / "dockerenv"
    marker.write_text("", encoding="utf-8")
    monkeypatch.setattr(published, "CONTAINER_MARKERS", (str(marker),))
    for name in ("STUDYFORGE_RUN_SERVICE", "STUDYFORGE_EDITOR_ORIGIN"):
        monkeypatch.delenv(name, raising=False)
    code, out = said([str(root.parent), "--published", "--port", "0"])
    assert code == UNUSABLE and "run service" in out


def test_beside_site_it_is_refused(root):
    code, out = said([str(root), "--site", str(root), "--published"])
    assert code == UNUSABLE and "--published serves a root" in out
