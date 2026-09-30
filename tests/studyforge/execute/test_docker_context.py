"""Every `docker` the serving path runs carries the caller's `DOCKER_CONTEXT` and names no context.

⭐ Every docker step runs on any engine: the
engine is the caller's choice, made with `DOCKER_CONTEXT` (or the current
context), and the framework never overrides, drops or switches it. ⭐ Measured
against a FAKE `docker` first on `PATH` that records its argv and the context
it was handed, so no daemon is reached and no lock is held.
"""

from __future__ import annotations

import json
import os
import signal
import stat
import sys
from pathlib import Path

import pytest

from studyforge.execute import ModeProbe
from studyforge.execute.editor import EditorProbe
from studyforge.execute.runner import ContainerLauncher

NAME = "studyforge-runner-kata"
CONTEXT = "a-context-the-caller-chose"


@pytest.fixture
def recorded(tmp_path, monkeypatch) -> Path:
    """A recording `docker` first on `PATH`, and `DOCKER_CONTEXT` set to a name no engine has."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.jsonl"
    script = bin_dir / "docker"
    script.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        f"with open({str(log)!r}, 'a') as out:\n"
        "    out.write(json.dumps({'args': sys.argv[1:], "
        "'context': os.environ.get('DOCKER_CONTEXT')}) + '\\n')\n"
        "print('false ')\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("DOCKER_CONTEXT", CONTEXT)
    return log


def calls(log: Path) -> list[dict]:
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_every_docker_the_serving_path_runs_carries_the_callers_context(recorded, tmp_path):
    ModeProbe(tmp_path, NAME).mode()
    EditorProbe(tmp_path, NAME).editor()
    launcher = ContainerLauncher(NAME, ".")
    process = launcher.spawn(["true"])
    process.wait(timeout=30)
    launcher.signal(process, signal.SIGTERM)
    seen = calls(recorded)
    assert {tuple(call["args"][:1]) for call in seen} == {("inspect",), ("exec",)}, seen
    assert len(seen) == 4, seen
    for call in seen:
        assert call["context"] == CONTEXT, f"the caller's DOCKER_CONTEXT was dropped: {call}"
        assert "--context" not in call["args"], call
        assert call["args"][:2] != ["context", "use"], call


def test_no_module_names_or_switches_a_context():
    source = Path(__file__).resolve().parents[3] / "src" / "studyforge"
    for path in sorted(source.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert "context use" not in text, path.relative_to(source).as_posix()
        assert '"--context"' not in text, path.relative_to(source).as_posix()
