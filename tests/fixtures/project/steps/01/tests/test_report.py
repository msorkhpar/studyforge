from pathlib import Path

from seedcrate.data import Lot, read_lots
from seedcrate.report import render

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_the_report_ends_with_the_total_value():
    """The report's last line is the total value of what the crate carries."""
    lots = [Lot("a", 3, 4.0), Lot("b", 4, 5.0)]
    assert render(lots, ("a", "b"), 7).splitlines()[-1] == "total value: 9.00"


def test_must_ship_lots_are_starred_and_the_weight_totalled():
    """A must-ship lot's line is starred, and the total weight is printed."""
    lines = render(read_lots(FIXTURES / "must.csv"), ("rye", "flax"), 6).splitlines()
    assert lines[1].startswith("* rye") and lines[2].startswith("  flax")
    assert "total weight: 5 kg" in lines
