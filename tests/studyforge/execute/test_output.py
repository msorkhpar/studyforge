"""Mirror of `src/studyforge/execute/output.py` (R12): relative first, then scrubbed."""

from __future__ import annotations

import pytest

from studyforge.execute import LineGate
from tests.studyforge.execute.runnable import FOREIGN_HOME

HOST_ROOT = f"{FOREIGN_HOME}/courses/kata"


@pytest.mark.parametrize(
    ("raw", "gated"),
    [
        ("rootdir: /work", "rootdir: ."),
        (
            '  File "/work/practice/broken/area.py", line 7',
            '  File "practice/broken/area.py", line 7',
        ),
        ("/work/practice/x.py:3: AssertionError\n", "practice/x.py:3: AssertionError"),
        ("/workspace/x /work.d /srv/work/x", "/workspace/x /work.d /srv/work/x"),
    ],
)
def test_the_container_root_becomes_relative_and_nothing_else_does(raw, gated):
    assert LineGate(["/work"])(raw) == gated


def test_the_host_root_becomes_relative_the_same_way():
    gate = LineGate([HOST_ROOT])
    assert gate(f"rootdir: {HOST_ROOT}") == "rootdir: ."
    assert gate(f"{HOST_ROOT}/practice/x.py:3: E") == "practice/x.py:3: E"


def test_relative_comes_before_the_scrub():
    """Scrubbing first would leave `/path/to/project/practice/x.py` on the host only."""
    assert LineGate([HOST_ROOT])(f"{HOST_ROOT}/practice/x.py") == "practice/x.py"
    assert (
        LineGate([])(f"{HOST_ROOT}/practice/x.py") == "/path/to/project/courses/kata/practice/x.py"
    )


def test_a_home_path_outside_the_root_is_still_scrubbed():
    gated = LineGate(["/work"])(f"cache at {FOREIGN_HOME}/.cache/x")
    assert gated == "cache at /path/to/project/.cache/x"


def test_an_ordinary_line_is_untouched():
    assert LineGate(["/work"])("1 passed in 0.01s") == "1 passed in 0.01s"
