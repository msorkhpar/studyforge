from pathlib import Path

from seedcrate.data import read_lots
from seedcrate.model import must_ship

DATA = Path(__file__).resolve().parents[1] / "data" / "lots.csv"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_reads_every_lot():
    """Every lot of the season's file is read with its weight and value."""
    lots = read_lots(DATA)
    assert [(lot.name, lot.weight, lot.value) for lot in lots] == [
        ("bean", 4, 7.5), ("beet", 3, 4.25), ("carrot", 2, 3.1), ("kale", 5, 8.0), ("leek", 1, 0.9)]


def test_reads_the_must_ship_flag():
    """The must column marks the lots that have to ship."""
    assert must_ship(read_lots(DATA)) == ("beet",)


def test_the_flag_is_read_without_case():
    """YES and True mark a must-ship lot as yes does."""
    assert must_ship(read_lots(FIXTURES / "shouted.csv")) == ("oat", "flax")
