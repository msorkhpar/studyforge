"""Mirror of `tests/floor/deviations.py` (R12).

⭐ **This module is DATA, so its mirror asserts the shape of the declaration rather than
a reading.** ⛔ Whether the declaration still MATCHES the tree is the check's question and
is asserted in `test_surfaces.py`, both ways — here the question is whether an entry can
be added that excuses something while saying nothing.
"""

from __future__ import annotations

from tests.floor.deviations import DECLARED, NO_SURFACE, REACHED_PAST, Declaration


def test_the_declaration_is_inhabited():
    # ⛔ An empty table satisfies every comparison below vacuously, and it
    # would also make the check's "closed" claim true by holding nothing.
    assert DECLARED


def test_every_entry_carries_a_ground_and_at_least_one_name():
    # ⛔ The row's clause: an exemption is DECLARED WITH ITS GROUND, never silent. An
    # entry with an empty ground is a silent exemption wearing the shape of a declared one.
    for package, declaration in DECLARED.items():
        assert declaration.names, f"{package} declares a ground and excuses nothing"
        assert declaration.ground.strip(), f"{package} excuses names and states no ground"
        assert len(declaration.ground) > len(package), package


def test_the_two_grounds_are_the_only_ones_and_they_name_different_remedies():
    # ⚠️ The distinction is load-bearing: one is a line on an existing surface, the other
    # is a package-sized row. A third ground appearing silently would blur them.
    assert {declaration.ground for declaration in DECLARED.values()} == {
        REACHED_PAST,
        NO_SURFACE,
    }
    assert "one line" in REACHED_PAST
    assert "not a line" in NO_SURFACE


def test_a_package_is_named_once_and_its_names_are_a_set():
    for package, declaration in DECLARED.items():
        assert isinstance(declaration.names, frozenset), package
        assert package.startswith("studyforge."), package


def test_a_declaration_is_frozen_so_a_reading_cannot_edit_it():
    # ⭐ The data may not be mutated by whatever reads it: an instrument that could
    # rewrite its own exemption while running would be excusing itself.
    declaration = Declaration("a ground", frozenset({"NAME"}))
    try:
        declaration.ground = "another"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("a Declaration was mutated in place")
