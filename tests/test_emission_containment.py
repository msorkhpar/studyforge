"""The emission sweep cannot write anywhere the harness does not own.

⛔ **Every write here is aimed at a directory the process CAN write** —
`tmp_path`, at whatever uid runs the suite — so the only thing between each
plant and the disk is `tests/emission/containment.py`. That is what makes this
pass at the default uid for a reason, and not by permission.
"""

from __future__ import annotations

import errno
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from tests.emission import POISON, POISON_ROOT, probe_callable
from tests.emission.containment import Tally, contained

WHERE = "a writer invented inside a test"


def _write_text(target: Path) -> None:
    target.write_text("alpha", encoding="utf-8")


def _os_open(target: Path) -> None:
    os.close(os.open(target, os.O_WRONLY | os.O_CREAT))


def _mkdir(target: Path) -> None:
    target.mkdir()


def _mkdir_by_descriptor(target: Path) -> None:
    descriptor = os.open(target.parent, os.O_RDONLY)
    try:
        os.mkdir(target.name, dir_fd=descriptor)
    finally:
        os.close(descriptor)


@pytest.mark.parametrize(
    ("shape", "event"),
    [
        (_write_text, "open"),
        (_os_open, "open"),
        (_mkdir, "os.mkdir"),
        (_mkdir_by_descriptor, "os.mkdir"),
    ],
)
def test_a_write_outside_is_refused_where_the_process_could_have_made_it(tmp_path, shape, event):
    # ⛔ THE PLANT, in every shape the audit vocabulary distinguishes: a public
    # callable that ignores what it was handed and writes to a fixed absolute
    # path. `tmp_path` is outside the minted directory and writable, so a
    # refusal here is the harness's and nobody else's.
    target = tmp_path / "escaped"

    def emit(note: str) -> None:
        shape(target)

    found = probe_callable(emit, WHERE)

    assert [escape.event for escape in found.contained.escapes] == [event], found.report()
    assert not target.exists()


def test_a_write_into_the_poisons_namespace_is_refused_and_is_not_an_escape():
    # ⭐ The writers the framework really has: handed the poison, they write
    # where they were told. That is correct behaviour, so it is refused and
    # counted — never reported — and the error is the one an unprivileged
    # process gets, so the census reads the same at every uid.
    def emit(root: str) -> None:
        Path(root).mkdir(parents=True)

    found = probe_callable(emit, WHERE)
    assert found.contained.escapes == []
    assert found.contained.refused >= 1

    with contained(Tally(), WHERE, POISON_ROOT), pytest.raises(PermissionError) as raised:
        Path(POISON).mkdir(parents=True)
    assert raised.value.errno == errno.EACCES
    assert POISON not in str(raised.value)


def test_a_call_that_starts_a_process_is_refused_before_the_process_exists():
    # ⛔ A child's writes are outside any audit hook's population, so the door
    # is shut rather than watched.
    def emit(note: str) -> None:
        subprocess.run([sys.executable, "-c", "pass"], check=True)

    found = probe_callable(emit, WHERE)
    assert found.contained.spawns == 1
    assert found.accepted == 0


def test_the_containment_stands_down_when_the_call_returns(tmp_path):
    # ⚠️ The hook stays installed for the rest of the session; what must not
    # stay is the arming, the working directory or the temporary directory.
    before = (os.getcwd(), tempfile.tempdir, sys.dont_write_bytecode)

    def emit(note: str) -> None:
        Path("alpha").write_text(note, encoding="utf-8")

    found = probe_callable(emit, WHERE)

    assert (os.getcwd(), tempfile.tempdir, sys.dont_write_bytecode) == before
    assert found.contained.landed == 1
    (tmp_path / "after").write_text("alpha", encoding="utf-8")
    assert (tmp_path / "after").is_file()
