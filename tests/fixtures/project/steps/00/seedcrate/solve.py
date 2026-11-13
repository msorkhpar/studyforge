"""One plan, end to end: read the lots, choose, and write the report."""

from __future__ import annotations

from pathlib import Path

from seedcrate.data import read_lots
from seedcrate.model import best_selection
from seedcrate.report import render


def plan(path: Path, capacity: int) -> str:
    """The report for the lots in `path` and a crate holding `capacity` kilograms."""
    lots = read_lots(path)
    return render(lots, best_selection(lots, capacity), capacity)
