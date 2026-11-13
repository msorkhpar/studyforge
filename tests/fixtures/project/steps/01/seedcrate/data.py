"""Reading the seed lots a crate may carry."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

#: What a `must` cell says when the lot has to ship, compared without case.
YES = ("yes", "y", "true")


@dataclass(frozen=True)
class Lot:
    """One seed lot: its name, its weight in kilograms, its value, and whether it must ship."""

    name: str
    weight: int
    value: float
    must: bool = False


def read_lots(path: Path) -> list[Lot]:
    """Read every lot of a CSV file with the columns name, weight, value and an optional must."""
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            Lot(
                row["name"],
                int(row["weight"]),
                float(row["value"]),
                (row.get("must") or "").strip().lower() in YES,
            )
            for row in csv.DictReader(handle)
        ]
