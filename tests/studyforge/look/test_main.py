"""Mirror of `src/studyforge/look/__main__.py` (R12): the command a skill names, run for real."""

from __future__ import annotations

import os
import subprocess
import sys

from tests.authoring.support import declared_pythonpath
from tests.studyforge.look.sites import a_browser, built
from tests.support import repository_root


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env["PYTHONPATH"] = declared_pythonpath()
    return subprocess.run(  # noqa: S603 — fixed argv, interpreter is `sys.executable`
        [sys.executable, "-m", "studyforge.look", *argv],
        cwd=repository_root(),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


def test_the_module_runs_and_says_how_it_is_used():
    done = run("--help")
    assert done.returncode == 0, done.stderr
    assert "--out" in done.stdout and "--browser" in done.stdout


def test_the_command_looks_at_a_built_site_in_a_real_browser(tmp_path):
    # ⭐ The buildserve skill's own fence, on a site a build wrote, in the browser
    # the visual harness found on this machine.
    binary = a_browser()
    site = built(tmp_path)
    out = tmp_path / "shots"
    out.mkdir()
    done = run(str(site), "--out", str(out), "--browser", binary)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "look: 3 of 3 page(s) rendered" in done.stdout
    assert sorted(path.suffix for path in out.iterdir()) == [".html"] * 3 + [".png"] * 3
