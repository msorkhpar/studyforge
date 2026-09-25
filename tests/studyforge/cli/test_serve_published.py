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


# --------------------------------------------------------------------------
# ⛔ The publisher's instance.env: a value that cannot work is refused by name
# --------------------------------------------------------------------------


def declared_with(root, **values):
    """Declare the corpus's runner and write the publisher's instance.env with `values`."""
    from studyforge.execute.instance import COMPOSE_FILE, INSTANCE_FILE

    (root / COMPOSE_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / COMPOSE_FILE).write_text("services: {}\n", encoding="utf-8")
    lines = "".join(f"{key}={value}\n" for key, value in values.items())
    (root / INSTANCE_FILE).write_text(lines, encoding="utf-8")
    return root


def test_the_root_form_refuses_a_bad_port_by_its_key_before_anything_binds(root):
    declared_with(root, STUDYFORGE_EDITOR_PORT="18505", STUDYFORGE_SITE_PORT="70000")
    code, out = said([str(root.parent), "--port", "0"])
    assert code == UNUSABLE
    assert "STUDYFORGE_SITE_PORT must be a whole port number" in out


def test_the_site_form_refuses_one_port_for_two_services_by_name(root):
    declared_with(root, STUDYFORGE_EDITOR_PORT="18505", STUDYFORGE_SITE_PORT="18505")
    code, out = said([str(root), "--site", str(root), "--port", "0"])
    assert code == UNUSABLE
    assert "STUDYFORGE_EDITOR_PORT and STUDYFORGE_SITE_PORT name one port" in out


def test_a_corpus_that_declares_no_runner_is_not_asked(root):
    from studyforge.execute.instance import INSTANCE_FILE
    from studyforge.serve import instance_refusal

    (root / INSTANCE_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / INSTANCE_FILE).write_text("STUDYFORGE_SITE_PORT=0\n", encoding="utf-8")
    assert instance_refusal(root) is None, "a corpus with no runner declared is served as before"
    declared_with(root, STUDYFORGE_SITE_PORT="0")
    assert "STUDYFORGE_SITE_PORT" in instance_refusal(root)
