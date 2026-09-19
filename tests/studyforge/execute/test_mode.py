"""Mirror of `src/studyforge/execute/mode.py` (R12): is the runner container up over THIS root.

⭐ The probe is measured against a FAKE `docker` — a script that answers
`inspect` as told and logs each call — so these cases need no daemon and hold
no lock. The real container's answer is `test_acceptance.py`'s.
"""

from __future__ import annotations

import stat
import sys
from pathlib import Path

import pytest

from studyforge.execute import CONTAINER, HOST, ModeProbe

NAME = "studyforge-runner-kata"


def fake_docker(where: Path, stdout: str, status: int = 0, pause: float = 0.0) -> Path:
    """A `docker` that prints `stdout`, exits `status`, and logs its argv."""
    script = where / "docker"
    script.write_text(
        f"#!{sys.executable}\n"
        "import sys, time\n"
        f"open({str(where / 'calls')!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
        f"time.sleep({pause})\n"
        f"print({stdout!r})\n"
        f"sys.exit({status})\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def calls(where: Path) -> list[str]:
    log = where / "calls"
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


@pytest.fixture
def root(tmp_path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    return corpus


def test_running_over_this_root_is_container_mode(tmp_path, root):
    docker = fake_docker(tmp_path, f"true {root}")
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == CONTAINER
    assert calls(tmp_path)[0].startswith("inspect --format ")
    assert calls(tmp_path)[0].endswith(f"-- {NAME}")


def test_a_differently_spelled_path_to_this_root_is_still_this_root(tmp_path, root):
    link = tmp_path / "link"
    link.symlink_to(root)
    assert (
        ModeProbe(root, NAME, docker=str(fake_docker(tmp_path, f"true {link}"))).mode() == CONTAINER
    )


@pytest.mark.parametrize(
    ("stdout", "status"),
    [
        ("false {root}", 0),  # stopped
        ("true /some/other/checkout", 0),  # up, over somebody else's files
        ("true ", 0),  # up, nothing at /work
        ("", 1),  # no such container
        ("garbage", 0),
    ],
)
def test_anything_short_of_up_over_this_root_is_host_mode(tmp_path, root, stdout, status):
    docker = fake_docker(tmp_path, stdout.format(root=root), status)
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == HOST


def test_no_docker_at_all_is_host_mode(tmp_path, root):
    assert ModeProbe(root, NAME, docker=str(tmp_path / "no-such-docker")).mode() == HOST


def test_a_probe_that_hangs_is_host_mode(tmp_path, root):
    docker = fake_docker(tmp_path, f"true {root}", pause=5)
    assert ModeProbe(root, NAME, docker=str(docker), inspect_timeout=0.3).mode() == HOST


def test_no_container_named_is_host_mode_and_asks_nobody(tmp_path, root):
    docker = fake_docker(tmp_path, f"true {root}")
    assert ModeProbe(root, None, docker=str(docker)).mode() == HOST
    assert calls(tmp_path) == []


def test_an_answer_is_believed_for_the_ttl_and_then_asked_again(tmp_path, root):
    now = [100.0]
    docker = fake_docker(tmp_path, f"true {root}")
    probe = ModeProbe(root, NAME, docker=str(docker), clock=lambda: now[0], ttl=10.0)
    assert probe.mode() == CONTAINER
    now[0] += 9.9
    assert probe.mode() == CONTAINER
    assert len(calls(tmp_path)) == 1
    now[0] += 0.2
    assert probe.mode() == CONTAINER
    assert len(calls(tmp_path)) == 2
