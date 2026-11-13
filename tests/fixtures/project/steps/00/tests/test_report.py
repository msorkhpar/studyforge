from seedcrate.data import Lot
from seedcrate.report import render


def test_the_report_ends_with_the_total_value():
    """The report's last line is the total value of what the crate carries."""
    lots = [Lot("a", 3, 4.0), Lot("b", 4, 5.0)]
    assert render(lots, ("a", "b"), 7).splitlines()[-1] == "total value: 9.00"
