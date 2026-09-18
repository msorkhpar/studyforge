"""The grader shipped with the material for `total`."""

from total import total


def test_every_price_is_counted():
    assert total([1, 2, 3]) == 6
