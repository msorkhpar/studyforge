"""The docker gate's skip reason, read both ways.

⛔ **A DEFAULT RUN MAKES NO DOCKER CALL.** A recording
client first on `PATH` must see no call from the gate, and none from any check in
`tests/docker/` run unflagged in a child session.

⛔ **Flagged, a reason that says WARM on a cold cache is the defect this gate must not
introduce, and one that says COLD on a warm cache is the defect it repairs.** So the pure
half feeds `skip_reason` every state, and the live half, flagged only, makes ONE scratch
checkout cold and then warm and requires `probe` to read each.

⭐ **Nothing here builds or pulls.** The scratch checkout's inputs differ by one comment, so
they name an image no daemon holds (cold); a throwaway image is then COMMITTED under that
name from a never-started container of the pinned base (warm) and removed after.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import uuid
from pathlib import Path

import pytest

import tests.docker.devgate as devgate
import tests.docker.test_dev_image_identity as identity
from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import (
    ANNOUNCEMENT,
    COLD,
    FRESH,
    INVOCATION,
    MARKER,
    NOT_PROBED,
    OPT_IN,
    UNKNOWN,
    WARM,
    Cache,
    announcement_prefix,
    base_image,
    probe,
    require_docker_run,
    skip_reason,
    this_checkout,
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

FLAGGED = {OPT_IN: "1"}

#: An absolute path: a slash with no word, dot, colon, tilde or dash before it.
ABSOLUTE = re.compile(r"(?<![\w.:~-])/[\w.-]")


def carries_no_path(found: Cache) -> bool:
    """Are `found` and the flagged reason it produces free of any absolute path?

    ⛔ Every skip reason prints on EVERY run, so a path in one is printed
    unconditionally, and a path is somebody's machine (R7).
    """
    said = skip_reason(FLAGGED, "docker", lambda: found, builds_fresh=False) or ""
    return not any(ABSOLUTE.search(text) for text in (found.why, said, NOT_PROBED))


def unconsulted() -> Cache:
    raise AssertionError("the daemon arm was reached where the answer does not depend on it")


def reason(state: str) -> str | None:
    return skip_reason(FLAGGED, "docker", lambda: STATES[state], builds_fresh=False)


# --- unflagged: the reason is true, and nothing asks the daemon ---------------


@pytest.mark.parametrize("environ", [{}, {OPT_IN: "0"}])
def test_a_default_run_says_the_cache_was_not_probed_and_names_the_run_that_probes(environ):
    said = skip_reason(environ, "docker", unconsulted, builds_fresh=False)
    assert said == NOT_PROBED and INVOCATION in said, said
    assert "WARM" not in said and "COLD" not in said, f"an unprobed cache named a state: {said}"


def test_a_check_that_builds_fresh_says_so_with_or_without_the_flag():
    for environ in ({}, FLAGGED):
        said = skip_reason(environ, "docker", unconsulted, builds_fresh=True)
        assert said == FRESH and "needs network" in said, said
        assert "No environment reaches it" in said and OPT_IN in said, said


@pytest.mark.parametrize("differing", sorted(identity.PROBES))
def test_the_identity_checks_skip_as_fresh_even_on_a_flagged_warm_cache(
    tmp_path, monkeypatch, differing
):
    # ⛔ A check that needs network must never read WARM. So on the most permissive
    # environment the gate knows (flagged, a client, a warm cache) the identity checks must
    # still skip as FRESH before their body runs. ⭐ No daemon is reached: the client is a
    # name, the cache is faked, and the body's first acts are refusals.
    monkeypatch.setenv(OPT_IN, "1")
    monkeypatch.delenv(MARKER, raising=False)
    monkeypatch.setattr(devgate, "tool_on_path", lambda name: "docker")
    monkeypatch.setattr(devgate, "this_checkout", lambda docker: STATES[WARM])

    def past_the_gate(*args, **kwargs):
        raise AssertionError("an identity check ran past the gate on a warm cache")

    monkeypatch.setattr(identity, "checkout", past_the_gate)
    monkeypatch.setattr(identity, "run", past_the_gate)
    with pytest.raises(pytest.skip.Exception) as raised:
        identity.test_two_checkouts_with_different_inputs_each_run_their_own_image(
            tmp_path, differing
        )
    assert str(raised.value) == FRESH, str(raised.value)


def test_the_recursion_guard_answers_first():
    said = skip_reason({MARKER: "1", **FLAGGED}, "docker", unconsulted, builds_fresh=False)
    assert said is not None and "recurse" in said, said


# --- a recording client: the default run never reaches it --------------------

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


def subcommands(log: Path) -> list[str]:
    """The first word of every recorded call: never its arguments, which carry paths."""
    return [call.split()[0] for call in log.read_text("utf-8").split("\n") if call.strip()]


@pytest.mark.parametrize("builds_fresh", [False, True])
def test_the_gate_makes_no_docker_call_on_a_default_run(tmp_path, monkeypatch, builds_fresh):
    _, log = fake_docker(tmp_path, monkeypatch, "Error: No such image: the-base")
    monkeypatch.delenv(OPT_IN, raising=False)
    monkeypatch.delenv(MARKER, raising=False)
    this_checkout.cache_clear()
    with pytest.raises(pytest.skip.Exception):
        require_docker_run(builds_fresh=builds_fresh)
    assert subcommands(log) == [], f"a default run called docker: {subcommands(log)}"


def test_no_check_in_tests_docker_calls_docker_on_a_default_run(tmp_path, monkeypatch):
    # ⛔ The whole directory, not the gate alone: a check that skipped the gate and asked
    # the daemon itself is the same breach. ⚠️ Only the last line and the subcommands reach
    # a message, because a session header carries the checkout path (R7).
    _, log = fake_docker(tmp_path, monkeypatch, "Error: No such image: the-base")
    monkeypatch.delenv(OPT_IN, raising=False)
    monkeypatch.delenv(MARKER, raising=False)
    me = (
        "tests/docker/test_dev_gate.py::test_no_check_in_tests_docker_calls_docker_on_a_default_run"
    )
    child = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    result = run(
        [*child, f"--basetemp={tmp_path / 'child'}", "tests/docker/", "--deselect", me],
        cwd=repository_root(),
    )
    last = result.stdout.strip().rpartition("\n")[2]
    assert result.returncode == 0, f"the unflagged child session did not pass: {last}"
    assert subcommands(log) == [], f"a default run called docker: {subcommands(log)}"


# --- flagged: the reason names the probed state -------------------------------


def test_a_flagged_warm_cache_runs_the_checks():
    assert reason(WARM) is None, "a warm cache was refused"


def test_a_flagged_cold_cache_is_called_cold_and_says_the_build_needs_network():
    said = reason(COLD)
    assert said is not None and "COLD" in said and "needs network" in said, said
    assert "WARM" not in said, f"a cold cache offered as warm: {said}"


def test_an_unread_cache_claims_neither_state():
    said = reason(UNKNOWN)
    assert said is not None and "WARM" not in said and "COLD" not in said, said


def test_the_flag_without_a_client_skips():
    assert skip_reason(FLAGGED, None, unconsulted, builds_fresh=False) == "docker is not installed"


def test_the_path_check_can_say_no():
    assert all(carries_no_path(found) for found in STATES.values())
    assert not carries_no_path(Cache(COLD, None, "no base under /srv/checkout")), (
        "a path read clean"
    )


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


def test_an_absent_base_reads_cold_and_no_container_is_started(tmp_path, monkeypatch):
    docker, log = fake_docker(tmp_path, monkeypatch, "Error: No such image: the-base")
    found = probe(repository_root(), docker)
    assert found.state == COLD and found.image is None, found
    assert "run" not in subcommands(log), "the probe started the absent base"
    assert carries_no_path(found), found


def test_a_daemon_that_does_not_answer_reads_unknown_rather_than_cold(tmp_path, monkeypatch):
    docker, _ = fake_docker(tmp_path, monkeypatch, "Cannot connect to the Docker daemon")
    found = probe(repository_root(), docker)
    assert found.state == UNKNOWN and carries_no_path(found), found


# --- live, flagged only: one scratch checkout, cold and then warm -------------


def test_one_scratch_checkout_reads_cold_then_warm_off_check_s_own_identity(tmp_path):
    if os.environ.get(MARKER):
        pytest.skip("inside the dev image, which has no docker client")
    if os.environ.get(OPT_IN) != "1":
        pytest.skip(f"{OPT_IN} is unset: this probe commits and removes an image, so it is flagged")
    docker = tool_on_path("docker")
    if docker is None:
        pytest.skip("docker is not installed")
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
    requirements.write_text(f"{requirements.read_text('utf-8')}# probe {uuid.uuid4().hex}\n")
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
        assert carries_no_path(cold) and carries_no_path(warm), "a live reason carries a path"
    finally:
        run([docker, "rm", container], cwd=tmp_path)
        run([docker, "image", "rm", cold.image], cwd=tmp_path)
