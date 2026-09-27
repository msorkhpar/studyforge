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
        f"open({str(where / 'calls')!r}, 'a').write("
        "' '.join(a.replace(chr(10), '\\\\n') for a in sys.argv[1:]) + '\\n')\n"
        f"time.sleep({pause})\n"
        f"print({stdout!r})\n"
        f"sys.exit({status})\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def answer(running: str, source: object = "", working_dir: object = "", binds: str = "") -> str:
    """What `docker inspect` prints for the probe's format: the run state, both labels, `/work`."""
    mounts = f"{source}\t/work\n" if source else ""
    return f"{running}\n{working_dir}\n{binds}\n{mounts}"


def up(root: object) -> str:
    """A running container a reader started by hand over `root`: no labels, `/work` from it."""
    return answer("true", root)


def calls(where: Path) -> list[str]:
    log = where / "calls"
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


@pytest.fixture
def root(tmp_path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    return corpus


def test_running_over_this_root_is_container_mode(tmp_path, root):
    docker = fake_docker(tmp_path, up(root))
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == CONTAINER
    assert calls(tmp_path)[0].startswith("inspect --format ")
    assert calls(tmp_path)[0].endswith(f"-- {NAME}")


def test_a_differently_spelled_path_to_this_root_is_still_this_root(tmp_path, root):
    link = tmp_path / "link"
    link.symlink_to(root)
    assert ModeProbe(root, NAME, docker=str(fake_docker(tmp_path, up(link)))).mode() == CONTAINER


@pytest.mark.parametrize(
    ("stdout", "status"),
    [
        (answer("false", "{root}"), 0),  # stopped
        (answer("true", "/some/other/checkout"), 0),  # up, over somebody else's files
        (answer("true"), 0),  # up, nothing at /work
        ("", 1),  # no such container
        ("garbage", 0),
    ],
)
def test_anything_short_of_up_over_this_root_is_host_mode(tmp_path, root, stdout, status):
    docker = fake_docker(tmp_path, stdout.replace("{root}", str(root)), status)
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == HOST


def test_no_docker_at_all_is_host_mode(tmp_path, root):
    assert ModeProbe(root, NAME, docker=str(tmp_path / "no-such-docker")).mode() == HOST


def test_a_probe_that_hangs_is_host_mode(tmp_path, root):
    docker = fake_docker(tmp_path, up(root), pause=5)
    assert ModeProbe(root, NAME, docker=str(docker), inspect_timeout=0.3).mode() == HOST


def test_no_container_named_is_host_mode_and_asks_nobody(tmp_path, root):
    docker = fake_docker(tmp_path, up(root))
    assert ModeProbe(root, None, docker=str(docker)).mode() == HOST
    assert calls(tmp_path) == []


def test_an_answer_is_believed_for_the_ttl_and_then_asked_again(tmp_path, root):
    now = [100.0]
    docker = fake_docker(tmp_path, up(root))
    probe = ModeProbe(root, NAME, docker=str(docker), clock=lambda: now[0], ttl=10.0)
    assert probe.mode() == CONTAINER
    now[0] += 9.9
    assert probe.mode() == CONTAINER
    assert len(calls(tmp_path)) == 1
    now[0] += 0.2
    assert probe.mode() == CONTAINER
    assert len(calls(tmp_path)) == 2


# ---------------------------------------------------------------------------
# ⭐ a container the compose file started is matched by its LABELS, so a
# Docker Desktop engine, whose `Source` is a path inside its VM, matches too.

#: What Docker Desktop for Windows reports as a bind's source: the VM's spelling.
VM_SOURCE = "/run/desktop/mnt/host/c/path/to/project"

#: The corpus root as `serve` holds it on that Windows host.
WINDOWS_ROOT = r"C:\path\to\project"


def labelled(working_dir: object, source: object = VM_SOURCE, binds: str = "=/work") -> str:
    """A compose-started runner: compose's working directory, the skill's binds label."""
    return answer("true", source, working_dir, binds)


def test_a_compose_runner_on_windows_is_matched_by_its_labels_not_its_vm_path():
    """⛔ The mount's source is the VM's spelling; the probe must not need it."""
    import ntpath

    from studyforge.execute.mode import up_from

    working_dir = r"c:\PATH\to\project\.studyforge\execution"
    assert up_from(labelled(working_dir), WINDOWS_ROOT, path=ntpath)


def test_a_compose_runner_of_another_checkout_is_not_this_one_on_windows():
    import ntpath

    from studyforge.execute.mode import up_from

    other = r"C:\path\to\other\.studyforge\execution"
    assert not up_from(labelled(other, source=VM_SOURCE), WINDOWS_ROOT, path=ntpath)


def test_a_labelled_runner_over_this_checkout_is_container_mode(tmp_path, root):
    working_dir = root / ".studyforge" / "execution"
    docker = fake_docker(tmp_path, labelled(working_dir, source="/somewhere/the/engine/sees"))
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == CONTAINER


@pytest.mark.parametrize(
    ("binds", "mounted"),
    [
        ("practice=/work", True),  # the root is not what /work holds
        ("=/elsewhere", True),  # the root is mounted, not at /work
        ("=/work", False),  # the label says /work, nothing is mounted there
    ],
)
def test_a_labelled_runner_that_does_not_hold_the_root_at_work_is_host_mode(
    tmp_path, root, binds, mounted
):
    working_dir = root / ".studyforge" / "execution"
    source = "/engine/path" if mounted else ""
    docker = fake_docker(tmp_path, answer("true", source, working_dir, binds))
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == HOST


def test_a_labelled_runner_of_another_checkout_is_host_mode_even_over_this_source(tmp_path, root):
    """⭐ The label decides once present: a matching source does not overrule it."""
    other = tmp_path / "other" / ".studyforge" / "execution"
    docker = fake_docker(tmp_path, labelled(other, source=root))
    assert ModeProbe(root, NAME, docker=str(docker)).mode() == HOST
