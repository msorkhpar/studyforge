"""The grader shipped with the material for `area`."""

from area import area


def test_a_two_by_three_rectangle():
    assert area(2, 3) == 6
