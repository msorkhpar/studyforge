"""Mirror of `src/studyforge/serve/published.py` (R12): the published form's runner and editor.

⭐ The run namespace is read end to end over the runnable fixture: a Run and a
Submit go from the route, through the run service (the real script, under
`perl`, over the fixture's root), and back — never `docker`, never the host's
own process launcher. ⭐ The allowlist is read as the records name it, and a
command a record starts naming is in the list the next run reads.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.execute import (
    ALLOWED_FILE,
    SERVICE,
    EditorProbe,
    Published,
    RunRefused,
    Service,
)
from studyforge.execute.published import allowed_bytes
from studyforge.serve import published
from studyforge.serve.routes import run
from tests.studyforge.execute.runservice import NEEDS_PERL, run_service
from tests.studyforge.serve.routes.running import (
    plant_command,
    post,
    runs_over,
    served_copy,
    serving,
    start_path,
)

EXIT_0 = "--- exit 0 ---"


@pytest.fixture
def root(tmp_path) -> Path:
    return served_copy(tmp_path)


@pytest.fixture
def container(tmp_path) -> list[str]:
    marker = tmp_path / "dockerenv"
    marker.write_text("", encoding="utf-8")
    return [str(marker)]


def config(service=None) -> Published:
    return Published(origin=None, binds=(), health=None, service=service)


def corpus_of(root: Path):
    return runs_over(root)[1].corpora[0]


def test_the_allowlist_is_every_command_the_records_name(root):
    served = corpus_of(root)
    runs = published.allowed_runs(served)
    run_commands = [argv for cwd, argv in runs if cwd == "."]
    assert len(runs) == len(run_commands), "every recorded command runs from the corpus root"
    plant_command(root, 1, "run_command", ["python3", "practice/plants/wait.py"])
    assert (".", ["python3", "practice/plants/wait.py"]) in published.allowed_runs(served)


def test_the_runner_seam_writes_the_list_then_hands_back_a_service_runner(root):
    served = corpus_of(root)
    runner = published.runner_for(config(Service("runner")))(served)
    assert runner.service == Service("runner")
    written = (root / ALLOWED_FILE).read_bytes()
    assert written == allowed_bytes(published.allowed_runs(served))


def test_a_published_config_with_no_service_refuses_a_run(root):
    with pytest.raises(RunRefused, match="no run service"):
        published.runner_for(config())(corpus_of(root))


def test_a_compose_that_declares_no_editor_answers_no_editor(root):
    probe = published.editor_for(config())(corpus_of(root))
    assert isinstance(probe, EditorProbe)
    assert probe.editor() is None


def test_outside_a_container_the_published_form_is_refused(tmp_path):
    with pytest.raises(RunRefused, match="outside"):
        published.published_config({"STUDYFORGE_RUN_SERVICE": "runner"}, [str(tmp_path / "absent")])


def test_inside_a_container_with_no_run_service_it_is_refused(container):
    with pytest.raises(RunRefused, match="run service"):
        published.published_config({}, container)


def test_inside_a_container_the_declared_config_is_read(container):
    got = published.published_config({"STUDYFORGE_RUN_SERVICE": "runner:9"}, container)
    assert (got.service.host, got.service.port) == ("runner", 9)


def test_starting_writes_every_corpus_allowlist_before_the_first_run(root, monkeypatch, container):
    monkeypatch.setattr(published, "CONTAINER_MARKERS", tuple(container))
    served = runs_over(root)[1]
    published.start_published({"STUDYFORGE_RUN_SERVICE": "runner"}, served.corpora)
    assert (root / ALLOWED_FILE).read_bytes() == allowed_bytes(
        published.allowed_runs(served.corpora[0])
    )


@pytest.fixture
def through_service(root) -> Iterator[tuple]:
    with run_service(root) as service:
        chosen = config(service)
        live, discovered = runs_over(
            root, runner=published.runner_for(chosen), editor=published.editor_for(chosen)
        )
        yield live, discovered


@NEEDS_PERL
def test_a_run_and_a_submit_go_through_the_run_service(through_service):
    live, discovered = through_service
    with serving(live, discovered) as server:
        status, _, body = post(server, start_path(1, run.RUN))
        submitted = post(server, start_path(1, run.TEST))
    assert (status, body.splitlines()) == (200, ["Hello, reader", EXIT_0])
    assert submitted[0] == 200 and submitted[2].splitlines()[-1] == EXIT_0
    assert any("1 passed" in line for line in submitted[2].splitlines())
    assert live.runner(discovered.corpora[0]).mode() == SERVICE


@NEEDS_PERL
def test_a_record_that_moves_is_run_at_the_next_run_because_the_list_follows_it(
    root, through_service
):
    live, discovered = through_service
    planted = root / "planted"
    with serving(live, discovered) as server:
        post(server, start_path(1, run.RUN))
        assert b"touch\x00planted" not in (root / ALLOWED_FILE).read_bytes()
        plant_command(root, 1, "run_command", ["touch", "planted"])
        _, _, body = post(server, start_path(1, run.RUN))
    assert body.splitlines()[-1] == EXIT_0 and planted.exists()
    assert b"touch\x00planted" in (root / ALLOWED_FILE).read_bytes()
