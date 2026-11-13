"""Reading the seed lots a crate may carry."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Lot:
    """One seed lot: its name, its weight in kilograms and its value to the bank."""

    name: str
    weight: int
    value: float


def read_lots(path: Path) -> list[Lot]:
    """Read every lot of a CSV file with the columns name, weight and value."""
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            Lot(row["name"], int(row["weight"]), float(row["value"]))
            for row in csv.DictReader(handle)
        ]
