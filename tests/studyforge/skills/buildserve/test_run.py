"""Mirror of `src/studyforge/skills/buildserve/run.py` (R12): the skill end to end.

⛔ Every pass condition is a REAL REQUEST answered by the running site, over a loopback
socket, and every site is written by `studyforge build` under `tmp_path`.
"""

from __future__ import annotations

from urllib.parse import quote

import pytest

import studyforge.cli.serve as serve_verb
from studyforge.serve.routes.run import RUN, TEST
from studyforge.skills.buildserve.states import EXECUTION_NAMESPACE
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES, VALID
from tests.studyforge.cli.narrate.service import VOICE
from tests.studyforge.cli.serving import floor, missing_media, pages_of
from tests.studyforge.execute.runnable import fixture_copy
from tests.studyforge.serve.routes.running import post, start_path
from tests.studyforge.serve.serving import fetch
from tests.studyforge.skills.buildserve.running import (
    EXERCISED,
    UNEXERCISED,
    audio_references,
    copied,
    dead_service,
    directory,
    files_under,
    narration_service,
    partials,
    reported_by_build,
    run_once,
    skill_running,
    steps,
)

SERVED = ["step validate exit 0", "step build exit 0", "step serve exit 0"]


def test_the_fixtures_inhabit_both_sides_of_the_exercise_flag():
    # ⛔ A parametrisation over an empty side would pass by collecting nothing.
    assert EXERCISED and UNEXERCISED


@pytest.mark.parametrize("name", VALID)
def test_each_fixture_is_validated_built_and_served_and_real_requests_are_answered(name, tmp_path):
    root, out = FIXTURES / name, directory(tmp_path)
    with skill_running(root, out) as running:
        index = fetch(running.server, "/index.html")
        toc = fetch(running.server, "/api/v1/content/toc")
        pages = {page: fetch(running.server, "/" + quote(page))[0] for page in pages_of(root)}
    said = running.said()
    assert running.code == [OK], said
    assert steps(said) == SERVED
    assert (index[0], index[2]) == (200, (out / "index.html").read_bytes())
    assert toc[0] == 200
    assert pages and set(pages.values()) == {200}, pages
    # ⛔ Contract 4's runtime arm: the site is exactly what the build said it wrote.
    assert files_under(out) and files_under(out) == reported_by_build(said)


@pytest.mark.parametrize("name", UNEXERCISED)
def test_no_exercises_and_no_narration_is_a_valid_site_and_both_states_are_reported(name, tmp_path):
    root, out = FIXTURES / name, directory(tmp_path)
    with skill_running(root, out) as running:
        status = fetch(running.server, "/index.html")[0]
    said = running.said()
    assert (running.code, status) == ([OK], 200), said
    assert partials(said) == ["narration", "exercises"]
    for state in partials(said):
        assert f"works {state}  " in said and f"remedy {state}  " in said
    reading = floor(out, missing_media(root, tmp_path))
    assert reading.pages and reading.defects == [], reading.defects


@pytest.mark.parametrize("name", EXERCISED)
def test_an_exercised_corpus_is_served_with_execution_and_no_toolchain_state(name, tmp_path):
    # ⭐ `W371`, closing `SF-22/2`: the skill serves `--site`, which now registers `run`.
    with skill_running(FIXTURES / name, directory(tmp_path)) as running:
        status = fetch(running.server, "/index.html")[0]
        index = fetch(running.server, "/api/v1/run/")[0]
    assert (running.code, status, index) == ([OK], 200, 200), running.said()
    assert EXECUTION_NAMESPACE in running.server.namespaces
    assert partials(running.said()) == ["narration"]


@pytest.mark.parametrize("name", EXERCISED)
def test_exercises_served_with_no_execution_are_still_reported_as_no_toolchain(
    name, tmp_path, monkeypatch
):
    # ⛔ The other way: the state follows what the serving process OFFERS, so a serve
    # that registers no `run` is still reported — and still serves the reading floor.
    # ⭐ `W386`: planted through the verb's named seam, and the plant must be REACHED.
    offered = []
    monkeypatch.setattr(serve_verb, "site_namespaces", lambda *given: offered.append(given) or {})
    with skill_running(FIXTURES / name, directory(tmp_path)) as running:
        status = fetch(running.server, "/index.html")[0]
    assert (running.code, status) == ([OK], 200), running.said()
    assert len(offered) == 1, "the serve never asked the seam what to register"
    assert EXECUTION_NAMESPACE not in running.server.namespaces
    assert not running.server.writers
    assert partials(running.said()) == ["narration", "toolchain"]


def test_the_seam_is_named_for_what_it_returns_and_the_private_name_is_gone():
    # ⭐ `W386`, closing `W380/1`: the seam returns `state` as well as `run`, so it is
    # named for the namespaces, and a plant at the old private name binds nothing.
    assert callable(serve_verb.site_namespaces)
    assert not hasattr(serve_verb, "_execution")


def test_a_site_the_skill_serves_answers_run_and_submit(tmp_path):
    # ⭐ The row's clause end to end: the runnable corpus, through the skill, in host mode.
    root = fixture_copy(tmp_path)
    with skill_running(root, directory(tmp_path)) as running:
        ran = post(running.server, start_path(1, RUN))
        submitted = post(running.server, start_path(1, TEST))
    said = running.said()
    assert running.code == [OK], said
    assert "toolchain" not in partials(said)
    assert (ran[0], ran[2].splitlines()) == (200, ["Hello, reader", "--- exit 0 ---"])
    assert submitted[0] == 200 and any("1 passed" in line for line in submitted[2].splitlines())


def test_an_absent_narration_service_is_reported_and_the_site_is_still_served(tmp_path):
    root, out = copied("depth1", tmp_path), directory(tmp_path)
    with skill_running(root, out, voice=VOICE, service=dead_service()) as running:
        status = fetch(running.server, "/index.html")[0]
    said = running.said()
    assert (running.code, status) == ([OK], 200), said
    assert "step narrate exit 2" in steps(said)
    assert partials(said) == ["narration-service", "exercises"]
    assert "Traceback" not in said


def test_a_narrated_corpus_is_served_with_every_clip_its_pages_name(tmp_path):
    root, out = copied("depth1", tmp_path), directory(tmp_path)
    with narration_service() as (url, fake):
        with skill_running(root, out, voice=VOICE, service=url) as running:
            clips = audio_references(out)
            answers = [fetch(running.server, "/" + quote(clip)) for clip in clips]
    said = running.said()
    assert running.code == [OK], said
    assert fake.submitted, "the narration service was never asked for anything"
    assert "step narrate exit 0" in steps(said)
    assert partials(said) == ["exercises"]
    assert clips, "no built page names a clip"
    assert all(status == 200 and body[:3] == b"ID3" for status, _, body in answers)


def test_a_corpus_that_does_not_validate_stops_before_anything_is_built(tmp_path):
    out = directory(tmp_path)
    code, said = run_once(FIXTURES / "invalid" / "ordinal-gap", out)
    assert code == INVALID
    assert steps(said) == [f"step validate exit {INVALID}"]
    assert files_under(out) == set()
    assert "partial " not in said


def test_an_output_directory_that_does_not_exist_stops_at_build_and_serves_nothing(tmp_path):
    absent = tmp_path / "absent"
    code, said = run_once(FIXTURES / "depth1", absent)
    assert code == UNUSABLE
    assert steps(said) == ["step validate exit 0", f"step build exit {UNUSABLE}"]
    assert not absent.exists()
    assert "serve http" not in said


def test_running_it_again_over_its_own_site_serves_again(tmp_path):
    out = directory(tmp_path)
    assert run_once(FIXTURES / "depth1", out)[0] == OK
    code, said = run_once(FIXTURES / "depth1", out)
    assert code == OK, said
    assert steps(said) == SERVED
