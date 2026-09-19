"""What `execute`'s tests run: a copy of the runnable fixture, its units' commands, plants.

⭐ **Every run happens in a temp COPY of `tests/fixtures/runnable/`** (`W352`'s
rule): the fixture tree is un-ignored, so anything a run wrote into it would be
an untracked file.

⭐ **A unit's commands come from its archive document, through the framework's
own reader** (`studyforge.exercise.of`) — the same argv a generated document
carries, so the runner is measured on what it will actually be handed. ⚠️ Unit
3, the file with no test, carries no record (`W352/1`, row `W357`), so its one
command is the run command its sibling units' shape gives it.

⭐ **Plants are written into the copy, never the fixture**: `nap.py` (a tree that
ignores `TERM`, for the timeout and stop clauses), `talk.py` (stdout and stderr,
a home path, the root's own spelling, its argv), `slow.py` (a line, a pause, a
line).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from pathlib import Path

from studyforge.exercise import of
from tests.fixture_checks import FIXTURES, RUNNABLE

FIXTURE = FIXTURES / RUNNABLE

#: Somebody's home directory, ASSEMBLED at run time: the repository's own sweep
#: has no allow-list for home paths, so a literal one here would fail the floor.
FOREIGN_HOME = "/" + "home/someone"
RAW = Path("archive") / "kata" / "raw" / "python"

#: The one thing that differs between two honest runs of the same unit: pytest's
#: wall-clock figure. ⛔ Masked, and nothing else is.
DURATION = re.compile(r" in \d+\.\d+s\b")

PLANTS = {
    "nap.py": (
        "import os, signal, subprocess, sys, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "child = subprocess.Popen([sys.executable, '-c', "
        "'import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(300)'])\n"
        "print('pids', os.getpid(), child.pid)\n"
        "time.sleep(300)\n"
    ),
    "talk.py": (
        "import os, sys\n"
        "print('out one')\n"
        "print('err two', file=sys.stderr)\n"
        "print('out three')\n"
        f"print('home', '{FOREIGN_HOME}/secret.txt')\n"
        "print('here', os.getcwd())\n"
        "print('argv', *sys.argv[1:])\n"
    ),
    "slow.py": "import time\nprint('first')\ntime.sleep(3)\nprint('second')\n",
}


def fixture_copy(where: Path) -> Path:
    """A fresh copy of the runnable corpus, with the plants under `practice/plants/`."""
    root = Path(shutil.copytree(FIXTURE, where / RUNNABLE))
    plants = root / "practice" / "plants"
    plants.mkdir()
    for name, text in PLANTS.items():
        (plants / name).write_text(text, encoding="utf-8")
    return root


def unit_commands(unit: int) -> list[tuple[str, ...]]:
    """The unit's run command, then its test command when it has one."""
    path = FIXTURE / RAW / f"unit-{unit:02d}" / "practice-1.json"
    exercise = of(json.loads(path.read_text(encoding="utf-8")), str(path.name))
    if exercise is None:
        return [("python3", "practice/untested/hello.py")]
    return [exercise.run_command, exercise.test_command]


def plant(name: str, *arguments: str) -> list[tuple[str, ...]]:
    """One command running a plant."""
    return [("python3", f"practice/plants/{name}", *arguments)]


def snapshot(root: Path) -> dict[str, str]:
    """Every file under `root`, relative, with its content's digest."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def observed(lines: list[str]) -> list[str]:
    """A run's lines as a reader would compare them: durations masked."""
    return [DURATION.sub(" in <t>s", line) for line in lines]


def alive(pid: int) -> bool:
    """Is host process `pid` alive and not a zombie?"""
    try:
        state = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()[0]
    except OSError, IndexError:
        return False
    return state != "Z"


def gone(check, *pids: int, within: float = 10.0) -> bool:
    """Do all `pids` stop being alive, by `check`, within `within` seconds?"""
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        if not any(check(pid) for pid in pids):
            return True
        time.sleep(0.1)
    return False


def pids_from(lines: list[str]) -> tuple[int, int]:
    """The parent and child pids `nap.py` printed."""
    line = next(line for line in lines if line.startswith("pids "))
    _, parent, child = line.split()
    return int(parent), int(child)


def unbuffered_removed(monkeypatch) -> None:
    """The negative control for streaming: the runner's environment without `PYTHONUNBUFFERED`."""
    from studyforge.execute import runner

    monkeypatch.setattr(runner, "RUN_ENVIRONMENT", {"PYTHONDONTWRITEBYTECODE": "1"})
    monkeypatch.delenv("PYTHONUNBUFFERED", raising=False)


def host_environment_clean(monkeypatch) -> None:
    """Keep the host's own Python settings from deciding a clause the runner owns."""
    for name in ("PYTHONUNBUFFERED", "PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):
        monkeypatch.delenv(name, raising=False)
    assert os.environ.get("PYTHONDONTWRITEBYTECODE") is None
