from seedcrate.data import Lot
from seedcrate.model import best_selection


def test_picks_the_most_valuable_fit():
    """The crate carries the most valuable set of lots that fits."""
    lots = [Lot("a", 3, 4.0), Lot("b", 4, 5.0), Lot("c", 2, 3.0)]
    assert best_selection(lots, 5) == ("a", "c")


def test_nothing_fits_in_an_empty_crate():
    """A crate with no room carries nothing."""
    assert best_selection([Lot("a", 1, 1.0)], 0) == ()
