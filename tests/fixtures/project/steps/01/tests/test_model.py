from pathlib import Path

import pytest

from seedcrate.data import Lot, read_lots
from seedcrate.model import best_selection

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_picks_the_most_valuable_fit():
    """The crate carries the most valuable set of lots that fits."""
    lots = [Lot("a", 3, 4.0), Lot("b", 4, 5.0), Lot("c", 2, 3.0)]
    assert best_selection(lots, 5) == ("a", "c")


def test_nothing_fits_in_an_empty_crate():
    """A crate with no room carries nothing."""
    assert best_selection([Lot("a", 1, 1.0)], 0) == ()


def test_a_must_ship_lot_is_always_chosen():
    """A must-ship lot is carried even where a better fit leaves it out."""
    assert best_selection(read_lots(FIXTURES / "must.csv"), 6) == ("rye", "flax")


def test_must_ship_lots_over_capacity_are_refused():
    """Must-ship lots that weigh more than the crate holds are refused."""
    with pytest.raises(ValueError):
        best_selection(read_lots(FIXTURES / "heavy.csv"), 5)


def test_a_worthless_must_ship_lot_still_ships():
    """A must-ship lot ships even when it adds nothing to the value."""
    assert "chaff" in best_selection(read_lots(FIXTURES / "worthless.csv"), 5)
