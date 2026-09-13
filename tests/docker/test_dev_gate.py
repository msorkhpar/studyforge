"""The docker gate's skip reason, read both ways (`W162`).

⛔ **A reason that says WARM on a cold cache is the defect this row must not introduce, and
one that says COLD on a warm cache is the defect it repairs.** So the pure half feeds
`skip_reason` every state, and the live half makes ONE scratch checkout cold and then warm
and requires `probe` to read each.

⭐ **Nothing here builds or pulls.** The scratch checkout's inputs differ by one comment, so
they name an image no daemon holds (cold); a throwaway image is then COMMITTED under that
name from a never-started container of the pinned base (warm) and removed after. ⚠️ The
live half needs that base present and skips, saying so, when it is not.
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import (
    ANNOUNCEMENT,
    COLD,
    INVOCATION,
    MARKER,
    OPT_IN,
    UNKNOWN,
    WARM,
    Cache,
    announcement_prefix,
    base_image,
    probe,
    skip_reason,
)
from tests.docker.test_dev_image_identity import hashed_inputs
from tests.support import repository_root, run, tool_on_path

#: A name shaped like `check`'s print and held by no daemon.
NAME = "example.invalid/dev:inputs-" + "0" * 64

STATES = {
    WARM: Cache(WARM, NAME, f"{NAME} is present"),
    COLD: Cache(COLD, NAME, f"{NAME} is not present, so a run builds it"),
    UNKNOWN: Cache(UNKNOWN, None, "the docker daemon did not answer"),
}


def unconsulted() -> Cache:
    raise AssertionError("the cache was probed where the answer does not depend on it")


def reason(state: str, *, builds_fresh: bool = False) -> str | None:
    return skip_reason({}, "docker", lambda: STATES[state], builds_fresh=builds_fresh)


# --- the reason, one cache state at a time -----------------------------------


def test_a_warm_cache_is_called_warm_and_names_the_environment_that_reaches_it():
    said = reason(WARM)
    assert said is not None and "WARM" in said and INVOCATION in said, said
    assert "COLD" not in said and "needs network" not in said, f"warm refused as cold: {said}"


def test_a_cold_cache_is_called_cold_and_says_the_build_needs_network():
    said = reason(COLD)
    assert said is not None and "COLD" in said and "needs network" in said, said
    assert "WARM" not in said, f"a cold cache offered as warm: {said}"


def test_an_unread_cache_claims_neither_state():
    said = reason(UNKNOWN)
    assert said is not None and "WARM" not in said and "COLD" not in said, said


@pytest.mark.parametrize("builds_fresh", [False, True])
@pytest.mark.parametrize("state", sorted(STATES))
def test_no_cache_state_turns_the_gate_on_by_default(state, builds_fresh):
    # ⛔ The row's MUST NOT: a warm cache is a reason to NAME the run, never to start it.
    assert reason(state, builds_fresh=builds_fresh) is not None, f"{state} ran with {OPT_IN} unset"


def test_a_check_that_builds_fresh_needs_network_whatever_the_cache_holds():
    said = skip_reason({}, "docker", unconsulted, builds_fresh=True)
    assert said is not None and "FRESH" in said and "needs network" in said, said
    assert "WARM" not in said, said


def test_the_recursion_guard_answers_before_the_opt_in():
    said = skip_reason({MARKER: "1", OPT_IN: "1"}, "docker", unconsulted, builds_fresh=False)
    assert said is not None and "recurse" in said, said


def test_the_opt_in_runs_where_docker_is_and_skips_where_it_is_not():
    assert skip_reason({OPT_IN: "1"}, "docker", unconsulted, builds_fresh=False) is None
    said = skip_reason({OPT_IN: "1"}, None, unconsulted, builds_fresh=False)
    assert said == "docker is not installed", said


# --- the text the probe runs: `check`'s own, and none of it builds -----------


def prints_before_it_builds(code: str) -> bool:
    """Does `check`'s code print its image before any Compose or build command?"""
    before = code.partition(ANNOUNCEMENT)[0]
    return ANNOUNCEMENT in code and "docker compose" not in before and "docker build" not in before


def test_the_probe_runs_check_s_own_text_and_none_of_it_builds():
    script = read("check")
    prefix = announcement_prefix(script)
    assert prefix is not None and script.startswith(prefix), "the probe runs text check lacks"
    assert "STUDYFORGE_DEV_IDENTITY=$(docker run" in prefix, "the prefix stops before the identity"
    last = prefix.rstrip("\n").rpartition("\n")[2]
    assert last.startswith(ANNOUNCEMENT), f"the prefix runs on past the image print: {last!r}"
    assert prints_before_it_builds(instructions("check")), "check builds before it prints"


def test_the_prefix_checks_can_say_no():
    code = instructions("check")
    line = ANNOUNCEMENT + code.partition(ANNOUNCEMENT)[2].partition("\n")[0]
    moved = code.replace(line, ":") + "\n" + line
    assert moved != code, "the control's subject is absent"
    assert not prints_before_it_builds(moved), "a print after Compose read as before it"
    assert announcement_prefix(read("check").replace(ANNOUNCEMENT, "echo ")) is None


def test_the_base_is_the_one_from_line_and_a_second_reads_as_none():
    dockerfile = read("Dockerfile")
    base = base_image(dockerfile)
    assert base is not None and "@sha256:" in base, base
    assert base_image(dockerfile + f"FROM {base}\n") is None, "two FROM lines read as one base"


# --- a fake client: the base is inspected before anything can pull it --------

FAKE_DOCKER = """#!/bin/sh
printf '%s\\n' "$*" >> "$W162_LOG"
if [ "$1 $2" = "image inspect" ]; then echo "$W162_ANSWER" >&2; exit 1; fi
exit 0
"""


def fake_docker(tmp_path: Path, monkeypatch, answer: str) -> tuple[str, Path]:
    """A docker client first on `PATH` that logs every call and answers inspects with `answer`."""
    client = tmp_path / "client"
    client.mkdir()
    docker = client / "docker"
    docker.write_text(FAKE_DOCKER, "utf-8")
    docker.chmod(0o755)
    log = tmp_path / "calls.log"
    log.touch()
    monkeypatch.setenv("PATH", f"{client}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("W162_LOG", str(log))
    monkeypatch.setenv("W162_ANSWER", answer)
    return str(docker), log


def test_an_absent_base_reads_cold_and_no_container_is_started(tmp_path, monkeypatch):
    docker, log = fake_docker(tmp_path, monkeypatch, "Error: No such image: the-base")
    found = probe(repository_root(), docker)
    assert found.state == COLD and found.image is None, found
    assert "run" not in log.read_text("utf-8").split(), "the probe started the absent base"


def test_a_daemon_that_does_not_answer_reads_unknown_rather_than_cold(tmp_path, monkeypatch):
    docker, _ = fake_docker(tmp_path, monkeypatch, "Cannot connect to the Docker daemon")
    assert probe(repository_root(), docker).state == UNKNOWN


# --- live: one scratch checkout, cold and then warm --------------------------


def test_one_scratch_checkout_reads_cold_then_warm_off_check_s_own_identity(tmp_path):
    docker = tool_on_path("docker")
    if os.environ.get(MARKER) or docker is None:
        pytest.skip("needs a docker client outside the dev image; the fake-client checks ran")
    base = base_image(read("Dockerfile"))
    assert base is not None
    if run([docker, "image", "inspect", base], cwd=tmp_path).returncode != 0:
        pytest.skip("the pinned base is not present, and pulling it is what the gate refuses")
    root = tmp_path / "checkout"
    shutil.copytree(repository_root() / DEV, root / DEV)
    inputs = hashed_inputs(instructions("check"))
    assert inputs, "check names no hashed inputs"
    for name in inputs:
        shutil.copy2(repository_root() / name, root / name)
    requirements = root / DEV / "requirements.txt"
    requirements.write_text(f"{requirements.read_text('utf-8')}# W162 {uuid.uuid4().hex}\n")
    cold = probe(root, docker)
    assert cold.state == COLD and cold.image, f"inputs no daemon holds read as {cold}"
    created = run([docker, "create", "--network", "none", base, "true"], cwd=tmp_path)
    assert created.returncode == 0, created.stderr[-500:]
    container = created.stdout.strip()
    try:
        committed = run([docker, "commit", container, cold.image], cwd=tmp_path)
        assert committed.returncode == 0, committed.stderr[-500:]
        warm = probe(root, docker)
        assert warm.state == WARM and warm.image == cold.image, f"a present image read as {warm}"
    finally:
        run([docker, "rm", container], cwd=tmp_path)
        run([docker, "image", "rm", cold.image], cwd=tmp_path)
