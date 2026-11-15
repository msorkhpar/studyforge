"""Mirror of `tests/harness/sources.py`: the tooling original's registry tests, carried.

⭐ The reader's positives and their controls run once, in the floor's mirror, against
this registry and this reader as well as its own. The whole-tree sweep stays with the
tooling's floor.
"""

from __future__ import annotations

from tests.harness.sources import KNOWN_SOURCES

# ⭐ `tests/floor/test_source_names.py` asserts this registry and this reader equal to the
# floor's, over every positive and every control it holds.


def test_the_registry_is_inhabited_and_every_entry_carries_a_reason():
    # ⛔ A sweep states its denominator: a registry that emptied would make every test that
    # asserts *absence* pass, and only this one would notice.
    assert len(KNOWN_SOURCES) >= 4
    for corpus, pattern, why in KNOWN_SOURCES:
        assert corpus and why and pattern.pattern
        assert len(why) > 30, corpus
