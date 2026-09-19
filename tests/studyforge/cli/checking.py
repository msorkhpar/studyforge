"""Shared by the `check` verb's tests: a copy of the runnable corpus, the verb, what it handed on.

⭐ **Every run happens in a temp COPY of `tests/fixtures/runnable/`** (`W352`'s rule, and
`execute`'s helper makes the copy), so nothing a run writes lands in the fixture tree.

⭐ **The records are read with the framework's own reader** (`exercise.of`), so each test
compares what the verb handed on with what the unit's record says, never with an argv typed
here.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.cli.check import main
from studyforge.execute import Runner
from studyforge.exercise import Exercise, of
from studyforge.progress import Progress
from tests.studyforge.execute.runnable import FIXTURE, RAW

#: The fixture's units, by the shape each is named for (its `container.json`).
PASSING, FAILING, UNTESTED, BROKEN, READING = 1, 2, 3, 4, 5

#: The files the graded and ungraded units name, as their records spell them.
GRADED_UNITS = (PASSING, FAILING, BROKEN)


def record(unit: int) -> Exercise:
    """The unit's exercise record, read from the fixture's archive by the framework's reader."""
    path = FIXTURE / RAW / f"unit-{unit:02d}" / "practice-1.json"
    exercise = of(json.loads(path.read_text(encoding="utf-8")), path.name)
    assert exercise is not None, f"unit {unit} carries no exercise record"
    return exercise


@dataclass
class Handed:
    """A `runner_for` that runs on the host and remembers everything it was given."""

    built: list[tuple[Path, str]] = field(default_factory=list)
    started: list[tuple[tuple[str, ...], ...]] = field(default_factory=list)

    def __call__(self, root: Path, container: str) -> _Watching:
        self.built.append((Path(root), container))
        return _Watching(Runner(root, None), self)


class _Watching:
    """A host `Runner` that notes each command list before starting it."""

    def __init__(self, runner: Runner, handed: Handed) -> None:
        self._runner = runner
        self._handed = handed

    def mode(self) -> str:
        return self._runner.mode()

    def start(self, commands, cwd="."):
        self._handed.started.append(tuple(tuple(command) for command in commands))
        return self._runner.start(commands, cwd)


@dataclass
class Checked:
    """One run of the verb: its exit code, its lines, and what it handed the runner."""

    code: int
    lines: list[str]
    handed: Handed

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def exit_lines(self) -> list[str]:
        return [line for line in self.lines if line.startswith("--- exit ")]


def check(*argv: str, runner_for=None) -> Checked:
    """Run the verb in-process, on the host, and capture everything it wrote."""
    handed = Handed()
    out = io.StringIO()
    code = main(list(argv), out=out, runner_for=runner_for or handed)
    return Checked(code, out.getvalue().splitlines(), handed)


def main_path(root: Path, unit: int) -> str:
    """The unit's file as an absolute path inside the copy `root`."""
    return str(root / record(unit).main_path)


def entries(root: Path) -> dict:
    """Every practice entry the copy's progress store holds, by key."""
    return Progress(root, depth=1).read()["practices"]
