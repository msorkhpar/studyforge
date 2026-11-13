from pathlib import Path

from seedcrate.data import read_lots

DATA = Path(__file__).resolve().parents[1] / "data" / "lots.csv"


def test_reads_every_lot():
    """Every lot of the season's file is read with its weight and value."""
    lots = read_lots(DATA)
    assert [(lot.name, lot.weight, lot.value) for lot in lots] == [
        ("bean", 4, 7.5), ("beet", 3, 4.25), ("carrot", 2, 3.1), ("kale", 5, 8.0), ("leek", 1, 0.9)]
