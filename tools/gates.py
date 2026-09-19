"""`W364`: the gates a guarded merge reads, and the FORM each suite gate is taken in.

**What it does.** Declares the gates `tools.mergegate` runs on a merged tree — the floor
and the suite in the pinned image, the suite on the host — and decides, per environment,
whether a suite is taken SERIAL or PARALLEL (`pytest-xdist`'s `-n auto`). Every gate
carries its form as text, so a reading SAYS which one it took.

**How you use it.** `declared()` returns the gates for THIS host; `GATES` is the static
declaration (the host suite serial). `suite_gate(environment, parallel)` builds either
form, which is how the mirror asserts both argv shapes.

**Depends on.** `dataclasses`, `fcntl`, `subprocess`, `typing` and `collections.abc` — the
standard library. `ContainerLock` is `W364` clause 6: the shared container lock, taken by the
merge gate around its pinned-image gates only (the argument is in `tools/mergegate.py`).
⛔ Nothing from `studyforge` or `tools.quality`: it is on the merge path, whose property
is that a tree too broken to import is REFUSED rather than crashing the gate (`W310`).

## ⛔ WHY THIS IS ITS OWN MODULE (Ruling 261: a SPLIT, never a trim)

⚠️ `tools/mergegate.py` stood at 389 of R11's 400 lines when `W364` needed the form
decision, and reached 410 with clause 6's lock. ⭐ The seam is the question each file
answers: THIS file says *which commands are the gates and how each is taken* — its form,
and under which lock; `mergegate` says *what the merged tree read under them*.

## ⛔ WHY THE IMAGE IS ALWAYS PARALLEL AND THE HOST ONLY SOMETIMES

⭐ The pinned image installs `pytest-xdist` by `==` pin (`docker/dev/requirements.txt`),
so its suite gate is parallel unconditionally. ⛔ The HOST installs nothing on the
register's behalf, so its suite gate is parallel only where `python3` — the interpreter
the gate itself runs — can import `xdist`, and is otherwise the serial run it always was.
⚠️ Asked of THAT interpreter by a child process, never of the one running this module:
the two need not be the same Python.
"""

from __future__ import annotations

import fcntl
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import TextIO

#: The two environments, named so every reading carries one (Ruling 326).
IMAGE, HOST = "pinned image", "host"

#: What makes a suite gate parallel: one worker per core the environment exposes.
PARALLEL = ("-n", "auto")

#: The two forms a suite gate can take, as a reading prints them.
PARALLEL_FORM = "parallel: pytest-xdist, -n auto"
SERIAL_FORM = "serial: pytest-xdist is not importable here"

#: The wrapper that is the only spelling of the pinned environment this repository has.
WRAPPER = "docker/dev/check"


@dataclass(frozen=True)
class Gate:
    """One gate: the command, where it is taken, what only it answers, and its form."""

    name: str
    environment: str
    argv: tuple[str, ...]
    answers: str
    #: ⭐ `W364`: SAID in every reading; empty for a gate that has only one form.
    form: str = ""


#: What each environment's suite answers that the other cannot. ⛔ Every entry is required.
SUITE_ANSWERS = {
    IMAGE: (
        "the `ruff` lint and format enforcement, which the host reports as SKIPPED "
        "rather than passed, and every assertion about the image itself"
    ),
    HOST: (
        "the sibling and workspace assertions, which the pinned image cannot reach "
        "because it mounts only the checkout (Ruling 248(a))"
    ),
}

FLOOR = Gate(
    name="floor",
    environment=IMAGE,
    argv=(WRAPPER, "python3", "-m", "tools.quality"),
    answers="the standard-library floor, taken where the linter actually exists",
)


def suite_gate(environment: str, parallel: bool) -> Gate:
    """Return the suite gate for `environment`, in the parallel or the serial form."""
    prefix = (WRAPPER,) if environment == IMAGE else ()
    return Gate(
        name="suite",
        environment=environment,
        argv=(*prefix, "python3", "-m", "pytest", "-q", *(PARALLEL if parallel else ())),
        answers=SUITE_ANSWERS[environment],
        form=PARALLEL_FORM if parallel else SERIAL_FORM,
    )


def xdist_importable(python: str = "python3") -> bool:
    """Report whether `python` — the host gate's own interpreter — can import `xdist`."""
    try:
        return (
            subprocess.run(  # noqa: S603 - fixed argv, no shell
                [python, "-c", "import xdist"], capture_output=True, check=False
            ).returncode
            == 0
        )
    except OSError:
        return False


#: ⛔ **EVERY ENTRY IS REQUIRED AND THE LIST IS THE UNIT.** ⭐ The static declaration: the
#: image suite parallel, the host suite in the form a host WITHOUT `xdist` takes.
GATES = (FLOOR, suite_gate(IMAGE, parallel=True), suite_gate(HOST, parallel=False))


def declared(importable: Callable[[], bool] = xdist_importable) -> tuple[Gate, ...]:
    """Return `GATES` with the host suite in the form THIS host can take (`W364`)."""
    return (FLOOR, suite_gate(IMAGE, parallel=True), suite_gate(HOST, parallel=importable()))


#: ⛔ `W364` clause 6: the variable NAMING the shared container lock file. Unset: no lock.
LOCK_VARIABLE = "STUDYFORGE_CONTAINER_LOCK"


class ContainerLock:
    """An exclusive `flock` on the file `path` names, held only while an image gate runs."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.handle: TextIO | None = None

    def hold(self, wanted: bool) -> None:
        """Take the lock when `wanted` and not held; release it when held and not wanted."""
        if not self.path or wanted == (self.handle is not None):
            return
        if wanted:
            # ⚠️ Not a `with`: the handle IS the lock, held across calls until released.
            self.handle = open(self.path, "a", encoding="utf-8")
            fcntl.flock(self.handle, fcntl.LOCK_EX)
            return
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None
