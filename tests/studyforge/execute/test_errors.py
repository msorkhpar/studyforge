"""Mirror of `src/studyforge/execute/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.execute import Runner, RunRefused
from tests.studyforge.execute.runnable import FOREIGN_HOME


def test_a_refusal_is_a_value_error():
    assert issubclass(RunRefused, ValueError)


def test_a_refusal_never_repeats_the_value_it_refused(tmp_path):
    refused = f"{FOREIGN_HOME}/run.sh"
    with pytest.raises(RunRefused) as raised:
        Runner(tmp_path).start([[refused]])
    assert refused not in str(raised.value)
    assert "someone" not in str(raised.value)
