"""Mirror of `tests/harness/skipped.py`: the unreachable population, derived from the tally.

⭐ The pure-function arms of the tooling original's tests, carried with the product's
copy. The end-to-end arm — a child run printing the line through the root `conftest.py` — is
`tests/test_product_stands_alone.py`'s, because that file owns what the root conftest prints.
"""

from __future__ import annotations

import uuid
from types import SimpleNamespace

from tests.harness.skipped import UNREACHABLE, skip_reason, unreachable_population


def _skipped(reason: str) -> SimpleNamespace:
    """A skipped report the way pytest tallies one: `(path, line, "Skipped: reason")`."""
    return SimpleNamespace(nodeid="t.py::t", longrepr=("t.py", 1, f"Skipped: {reason}"))


def test_an_empty_population_is_still_PRINTED_as_zero():
    # ⛔ The arm a careless repair deletes: `0` is a reading, never an absence.
    assert unreachable_population({}) == [
        f"{UNREACHABLE}: 0 skipped test(s) — this run reached every test it collected"
    ]


def test_the_count_and_every_reason_are_DERIVED_from_the_tally():
    # ⛔ Reasons minted at run time, so no typed list of reasons can produce them.
    first, second = f"absent {uuid.uuid4().hex}", f"absent {uuid.uuid4().hex}"
    stats = {"skipped": [_skipped(first), _skipped(second), _skipped(first)], "passed": [1]}
    lines = unreachable_population(stats)
    assert lines[0].startswith(f"{UNREACHABLE}: 3 skipped test(s) — ")
    assert lines[1:] == [f"  2 × {first}", f"  1 × {second}"]


def test_a_reason_is_read_as_its_author_typed_it():
    assert skip_reason(_skipped("no sibling here")) == "no sibling here"


def test_a_report_with_no_reason_still_names_one():
    assert skip_reason(SimpleNamespace()) == "no reason given"
