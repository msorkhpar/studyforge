"""Mirror of `tests/floor/vacuity.py`: every product check answers for an empty run."""

from __future__ import annotations

from tests.floor import CHECKS
from tests.floor.vacuity import DISCLOSED_BY, POPULATIONS, TAG, vacuity_notice
from tests.support import repository_root


def test_every_check_is_answered_for_in_a_table():
    disclosed = {check for check, _ in DISCLOSED_BY}
    populated = {population.check for population in POPULATIONS}
    assert set(CHECKS) <= disclosed | populated, "a product check answers for no empty run"


def test_silent_on_this_repository_and_speaking_on_an_empty_tree(tmp_path):
    # ⛔ The pairing is not the evidence: the two readings must differ.
    assert vacuity_notice(repository_root()) == []
    printed = vacuity_notice(tmp_path)
    assert len(printed) == 1 and printed[0].startswith(TAG)
    for population in POPULATIONS:
        assert population.label() in printed[0], population.label()
