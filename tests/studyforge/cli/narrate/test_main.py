"""Mirror of `src/studyforge/cli/narrate/__main__.py` (R12).

⛔ Run as a subprocess: a traceback is only visible to a real process, and
*"an absent service is a named refusal, never a traceback"* is about what a
person at a terminal sees.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys

import pytest

from studyforge.cli.narrate.report import NO_SERVICE
from studyforge.validate.cli import UNUSABLE
from tests.studyforge.cli.narrate.service import VOICE, files
from tests.studyforge.generate.corpora import a_corpus
from tests.support import repository_root

#: Both ways a person reaches the verb: the stage alone, and the one command.
ENTRY_POINTS = (("studyforge.cli.narrate",), ("studyforge.cli", "narrate"))


def module(entry: tuple[str, ...], *argv) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", *entry, *argv],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


def dead_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.mark.parametrize("entry", ENTRY_POINTS, ids=lambda entry: " ".join(entry))
def test_an_absent_service_is_a_named_refusal_and_never_a_traceback(tmp_path, entry):
    root = a_corpus(tmp_path, "depth1")
    before = files(root)

    result = module(
        entry, str(root), "--voice", VOICE, "--service", f"http://127.0.0.1:{dead_port()}"
    )

    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == UNUSABLE
    assert NO_SERVICE in result.stdout
    assert files(root) == before


def test_the_module_is_one_implementation_on_top_of_cli_main():
    source = (repository_root() / "src/studyforge/cli/narrate/__main__.py").read_text("utf-8")
    body = [
        line
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("#", '"', "'"))
    ]
    assert any("from studyforge.cli.narrate.cli import main" in line for line in body)
    assert not any("def " in line for line in body), "this module forwards and defines nothing"
