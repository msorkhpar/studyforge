"""The `check` verb takes `SF-20`'s mode: the runner container when it is up, the host otherwise.

⭐ **The verb chooses no mode.** It hands the runner the corpus's container name
(`execute.container_for`) and the runner probes. So the same file checked in either mode
must print the same lines and exit the same way (§8.3, rule 4).

⭐ **Container mode runs when `STUDYFORGE_RUNNER_IMAGE` names the runner image and Docker is
reachable** (`tests/studyforge/execute/container.py`), against a container started with the
documented run line over the same copy. ⛔ Never a mock. Where it cannot run, it SKIPS and
says why. ⛔ Any invocation that reaches it holds the shared container lock.
"""

from __future__ import annotations

import pytest

from studyforge.execute import CONTAINER, HOST, Runner
from tests.studyforge.cli.checking import FAILING, PASSING, UNTESTED, check, main_path
from tests.studyforge.execute import container
from tests.studyforge.execute.runnable import fixture_copy, host_environment_clean, observed


@pytest.fixture(scope="module")
def stage(tmp_path_factory):
    """One copy of the corpus, and, when the image is named, the reader's container over it."""
    root = fixture_copy(tmp_path_factory.mktemp("sf44"))
    reason = container.skip_reason()
    name = None if reason else container.start(root)
    try:
        yield root, name, reason
    finally:
        if name is not None:
            container.remove(name)


def checked_in(stage, mode: str, unit: int, monkeypatch):
    """Check the unit's file with a runner that WILL take `mode`, asserted, not assumed."""
    root, name, reason = stage
    if mode == CONTAINER and name is None:
        pytest.skip(reason)
    host_environment_clean(monkeypatch)

    def runner_for(source_root, _container):
        runner = Runner(source_root, name if mode == CONTAINER else None)
        assert runner.mode() == mode
        return runner

    return check(main_path(root, unit), runner_for=runner_for)


@pytest.mark.parametrize("unit", [PASSING, FAILING, UNTESTED])
def test_both_modes_print_the_same_lines_and_exit_alike(stage, unit, monkeypatch):
    host = checked_in(stage, HOST, unit, monkeypatch)
    inside = checked_in(stage, CONTAINER, unit, monkeypatch)
    assert inside.code == host.code
    assert observed(inside.lines[1:]) == observed(host.lines[1:])
    assert host.lines[0].endswith(f"mode {HOST}")
    assert inside.lines[0].endswith(f"mode {CONTAINER}")


def test_the_runner_is_handed_the_corpus_container_and_takes_host_when_it_is_not_up(stage):
    # ⭐ The default: the real `Runner`, over the corpus root, naming the corpus's container.
    root, name, _ = stage
    checked = check(main_path(root, PASSING), runner_for=Runner)
    if name is None:
        assert checked.lines[0].endswith(f"mode {HOST}")
    recorded = check(main_path(root, PASSING)).handed.built
    assert recorded == [(root, "studyforge-runner-runnable-demo")]
